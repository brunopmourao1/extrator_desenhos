# 02 — Arquitetura

## 1. Visão geral

Aplicativo desktop monolítico em três módulos com dependências em sentido único:

```
┌─────────────────────────────────────────────────────┐
│ main.py — GUI (PySide6)                              │
│  · JanelaPrincipal                                   │
│  · ThreadVarredura (QThread)  → usa extrator         │
│  · ThreadExportacao (QThread) → usa exportador       │
└──────────────┬───────────────────────┬───────────────┘
               ▼                       ▼
┌──────────────────────────┐ ┌─────────────────────────┐
│ extrator.py              │ │ exportador.py           │
│ (puro: pdfplumber + re)  │ │ (xlwings + shutil)      │
│  · processar_pdf()       │ │  · exportar()           │
│  · extrair_carimbo()     │ │  · fazer_backup()       │
│  · extrair_bom_mp()      │ │  · desenhos_existentes()│
│  · gerar_linhas()        │ │                         │
│  · escanear_pasta()      │ │                         │
└──────────────────────────┘ └─────────────────────────┘
```

Regras de dependência: `extrator.py` importa apenas stdlib + pdfplumber;
`exportador.py` importa xlwings **tardiamente** (dentro de `exportar()`) para que
o módulo carregue em máquinas sem Excel; `main.py` é o único que conhece Qt.

## 2. Fluxo de dados

1. Usuário informa pasta raiz → `ThreadVarredura` chama
   `escanear_pasta(raiz, callback)` → lista de `DadosDesenho`.
2. GUI converte cada `DadosDesenho` em linhas de planilha via `gerar_linhas()`
   (dicts com chaves `desenho, rev, qtde, processo, descricao, dimensao,
   material, qtd, arquivo`).
3. Usuário edita/marca linhas na `QTableWidget`.
4. `ThreadExportacao` chama `exportar(caminho_xlsm, linhas_marcadas)`:
   backup → abre Excel oculto → localiza primeira linha vazia → grava colunas
   mapeadas → salva → fecha.

## 3. Modelo de dados

```python
@dataclass
class ItemMP:            # linha da tabela de matéria-prima
    item: int            # nº sequencial no desenho
    descricao: str       # ex. "METALON 50 X 50 X 3,17", "CHAPA"
    comprimento: str     # ex. "1890.00", '1" X 460 X 465', "CONF. DESENHO"
    qtd: int
    folha: int           # página do PDF onde a tabela foi encontrada

@dataclass
class DadosDesenho:      # resultado de um PDF
    arquivo, caminho, desenho, rev, qtde, nome, material,
    dimensao, massa, titulo: str
    itens_mp: list[ItemMP]
    erro: str            # vazio = sucesso; preenchido = "revisar manualmente"
```

## 4. Threading

- Varredura e exportação rodam em `QThread` para não congelar a UI.
- Comunicação exclusivamente por `Signal` (progresso, log, concluído, falhou) —
  nunca tocar em widgets a partir da thread.
- Uma operação por vez: botões desabilitados durante execução.

## 5. Tratamento de erros

- **Por PDF:** `processar_pdf` captura qualquer exceção e devolve
  `DadosDesenho(erro=...)`; a varredura nunca aborta (RF-09).
- **Exportação:** qualquer exceção após o backup deixa o original intacto
  (xlwings só salva no final); `finally: app.quit()` garante que não fica
  processo EXCEL.EXE órfão.
- Erros inesperados vão para o log da UI com traceback completo.

## 6. Dependências

| Pacote | Uso | Observação |
|--------|-----|------------|
| pdfplumber ≥ 0.11 | extração de palavras com coordenadas | não usar PyPDF2/pypdf para extração posicional |
| PySide6 ≥ 6.6 | GUI | licença LGPL, ok para uso interno |
| xlwings ≥ 0.31 | escrita no `.xlsm` | requer Excel instalado; import tardio |
| pyinstaller | build | apenas em dev |

**Por que xlwings e não openpyxl na escrita:** openpyxl reescreve o arquivo
inteiro e degrada tabelas dinâmicas e formatação condicional do template da
LS Control (aviso "Conditional Formatting extension is not supported" observado
na prática). xlwings comanda o Excel real, preservando tudo. openpyxl pode ser
usado livremente em testes de *leitura* da planilha.

## 7. Empacotamento e distribuição

- `build.bat`: `pyinstaller --onefile --windowed --name "ExtratorDesenhosLS" main.py`.
- O exe é auto-contido (Python + libs embutidos); o único pré-requisito da
  máquina de destino é o Excel.
- Distribuir pela rede interna (`\\192.168.1.5\...`); o app não requer instalação.

## 8. Extensibilidade prevista (não implementar sem demanda)

- `PREFIXOS_MP` em `extrator.py`: lista de prefixos de descrição de MP; novos
  materiais entram como string simples.
- `PROCESSOS` em `main.py`: valores do combo; combo é editável, então valores
  fora da lista já são aceitos.
- Consolidação em barras (descartada na v1) entraria como transformação opcional
  entre `gerar_linhas()` e a tabela, sem tocar na extração.
