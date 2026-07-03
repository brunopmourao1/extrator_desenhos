# -*- coding: utf-8 -*-
"""
Exportação das linhas revisadas para a planilha OS ACOMPANHAMENTO (.xlsm) existente.

Usa xlwings (controla o Excel via COM) para preservar 100% das macros, tabelas
dinâmicas e formatação condicional do arquivo — requisito para os .xlsm da LS Control.
Antes de gravar, cria um backup do arquivo original.
"""
import shutil
from datetime import datetime
from pathlib import Path

ABA_DESTINO = "OS ACOMPANHAMENTO"
LINHA_INICIAL = 6  # dados começam na linha 6 (1-5 são cabeçalhos)

# coluna da planilha -> chave do dicionário de linha
MAPEAMENTO = {
    "A": "desenho",    # DESENHO
    "B": "rev",        # REV.
    "C": "qtde",       # QTDE
    "D": "processo",   # PROCESSO
    "G": "descricao",  # DESCRIÇÃO
    "H": "dimensao",   # DIMENSÃO SOLICITADA
    "I": "material",   # MATERIAL
    "J": "qtd",        # QTD (matéria-prima)
}


def fazer_backup(caminho_xlsm: Path) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = caminho_xlsm.with_name(f"{caminho_xlsm.stem}_BACKUP_{ts}{caminho_xlsm.suffix}")
    shutil.copy2(caminho_xlsm, destino)
    return destino


def desenhos_existentes(ws) -> set:
    ultima = ws.range(f"A{ws.cells.last_cell.row}").end("up").row
    if ultima < LINHA_INICIAL:
        return set()
    valores = ws.range(f"A{LINHA_INICIAL}:A{ultima}").value
    if not isinstance(valores, list):
        valores = [valores]
    return {str(v).strip() for v in valores if v}


def exportar(caminho_xlsm: str, linhas: list, pular_duplicados: bool = True,
             log=print) -> dict:
    """Insere as linhas na primeira linha vazia da aba OS ACOMPANHAMENTO.

    Retorna {"inseridas": n, "puladas": n, "backup": caminho}.
    """
    import xlwings as xw  # import tardio: só necessário na exportação (Windows + Excel)

    caminho = Path(caminho_xlsm)
    if not caminho.exists():
        raise FileNotFoundError(f"Planilha não encontrada: {caminho}")

    backup = fazer_backup(caminho)
    log(f"Backup criado: {backup.name}")

    app = xw.App(visible=False, add_book=False)
    inseridas = puladas = 0
    try:
        wb = app.books.open(str(caminho))
        if wb.api.ReadOnly:
            raise RuntimeError(
                f"A planilha já está aberta no Excel por outro processo/usuário "
                f"(abriu como somente leitura): {caminho.name}. "
                f"Feche o arquivo no Excel e tente novamente.")
        try:
            ws = wb.sheets[ABA_DESTINO]
        except Exception:
            raise RuntimeError(f'Aba "{ABA_DESTINO}" não encontrada na planilha.')

        existentes = desenhos_existentes(ws) if pular_duplicados else set()

        ultima = ws.range(f"A{ws.cells.last_cell.row}").end("up").row
        prox = max(ultima + 1, LINHA_INICIAL)
        # se a planilha estiver vazia (linha 5 = cabeçalho), começa na 6
        if ws.range(f"A{prox - 1}").value is None and prox - 1 >= LINHA_INICIAL:
            prox = LINHA_INICIAL

        ja_avisados = set()
        for ln in linhas:
            des = str(ln.get("desenho", "")).strip()
            if pular_duplicados and des and des in existentes:
                if des not in ja_avisados:
                    log(f"Pulado (já existe na planilha): {des}")
                    ja_avisados.add(des)
                puladas += 1
                continue
            for col, chave in MAPEAMENTO.items():
                valor = ln.get(chave, "")
                if valor not in ("", None):
                    ws.range(f"{col}{prox}").value = valor
            prox += 1
            inseridas += 1

        wb.save()
        wb.close()
        log(f"Exportação concluída: {inseridas} linha(s) inserida(s), {puladas} pulada(s).")
    finally:
        app.quit()

    return {"inseridas": inseridas, "puladas": puladas, "backup": str(backup)}
