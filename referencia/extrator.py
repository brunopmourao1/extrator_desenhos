# -*- coding: utf-8 -*-
"""
Motor de extração de dados de desenhos mecânicos LS Control (template SGQ FOR ENG 004).
Extrai campos do carimbo e a tabela de matéria-prima (ITEM | DESCRIÇÃO | COMPRIMENTO | QTD.)
usando âncoras posicionais — método validado com 100% de acerto nos desenhos de teste.
"""
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import pdfplumber

RX_NUM_DESENHO = re.compile(r"\d{4}-\d{2}-\d{3}")

# prefixos conhecidos de descrição de matéria-prima (2 palavras antes de 1)
PREFIXOS_MP = [
    "BARRA CHATA", "BARRA REDONDA", "BARRA QUADRADA", "PERFIL DE ALUMINIO",
    "PERFIL DE ALUMÍNIO", "METALON", "CANTONEIRA", "CHAPA", "OXICORTE",
    "LASER", "PERFIL", "TUBO", "VIGA", "BARRA",
]


@dataclass
class ItemMP:
    item: int
    descricao: str
    comprimento: str
    qtd: int
    folha: int


@dataclass
class DadosDesenho:
    arquivo: str = ""
    caminho: str = ""
    desenho: str = ""
    rev: str = "00"
    qtde: str = ""
    nome: str = ""
    material: str = ""
    dimensao: str = ""
    massa: str = ""
    titulo: str = ""
    itens_mp: list = field(default_factory=list)
    erro: str = ""


# ---------------------------------------------------------------- carimbo

_IGNORAR = {"N°", "DESENHO:", "NOME:", "MATERIAL:", "QTDE:", "DIMENSÃO:",
            "MASSA", "(Kg):", "TÍTULO:", "TRAT.", "TÉRMICO:", "ESCALA",
            "FOLHA"}


def _find_label(words, *toks):
    n = len(toks)
    for i in range(len(words) - n + 1):
        if all(words[i + j]["text"] == toks[j] for j in range(n)):
            return words[i], words[i + n - 1]
    return None, None


def _valor_abaixo(words, a0, a1, dy=20, dx_esq=10, dx_dir=250):
    cand = [w for w in words
            if a1["bottom"] - 2 < w["top"] < a1["bottom"] + dy
            and a0["x0"] - dx_esq < w["x0"] < a0["x0"] + dx_dir
            and w["text"] not in _IGNORAR and ":" not in w["text"]]
    cand.sort(key=lambda w: (round(w["top"]), w["x0"]))
    return " ".join(w["text"] for w in cand) or None


def _num_desenho(words, txt):
    a0, a1 = _find_label(words, "N°", "DESENHO:")
    if a0:
        # valor pode estar acima ou abaixo do rótulo, com possível sufixo (ex: OXICORTE B)
        cand = [w for w in words
                if (abs(w["top"] - a1["bottom"]) < 25 or abs(a0["top"] - w["bottom"]) < 15)
                and a0["x0"] - 40 < w["x0"] < a0["x0"] + 220
                and (RX_NUM_DESENHO.search(w["text"])
                     or w["text"] in ("OXICORTE", "LASER")
                     or re.fullmatch(r"[A-Z]", w["text"]))]
        cand.sort(key=lambda w: (round(w["top"]), w["x0"]))
        base = [w for w in cand if RX_NUM_DESENHO.search(w["text"])]
        if base:
            linha_top = round(base[0]["top"])
            toks = [w["text"] for w in cand if round(w["top"]) == linha_top]
            return " ".join(toks)
    m = RX_NUM_DESENHO.search(txt)
    return m.group(0) if m else ""


def extrair_carimbo(page) -> dict:
    words = page.extract_words()
    txt = page.extract_text() or ""
    out = {}
    out["desenho"] = _num_desenho(words, txt)

    for campo, toks, mesma_linha in [
        ("nome", ("NOME:",), False),
        ("material", ("MATERIAL:",), False),
        ("qtde", ("QTDE:",), False),
        ("dimensao", ("DIMENSÃO:",), True),
        ("titulo", ("TÍTULO:",), True),
    ]:
        a0, a1 = _find_label(words, *toks)
        if not a0:
            out[campo] = ""
            continue
        v = None
        if mesma_linha:
            ml = [w for w in words if abs(w["top"] - a0["top"]) < 3
                  and w["x0"] > a1["x1"] and w["x0"] - a1["x1"] < 300
                  and ":" not in w["text"]]
            if ml:
                v = " ".join(w["text"] for w in sorted(ml, key=lambda w: w["x0"]))
        if not v:
            v = _valor_abaixo(words, a0, a1)
        out[campo] = v or ""

    m = re.search(r"MASSA \(Kg\):\s*([\d.,]+)", txt)
    out["massa"] = m.group(1) if m else ""
    out["rev"] = _rev_vigente(words)
    return out


def _rev_vigente(words) -> str:
    """Lê a coluna REV. da tabela de revisões (header: REV | ANTIGO | ATUAL |
    DATA | RESPONSÁVEL) e devolve a maior revisão. Posicional: imune a cotas
    do desenho coladas no texto."""
    for i, w in enumerate(words):
        if w["text"] != "REV.":
            continue
        mesma_linha = [x for x in words if abs(x["top"] - w["top"]) < 3]
        textos = {x["text"].upper().rstrip(".") for x in mesma_linha}
        if not {"DATA", "RESPONSÁVEL"} <= textos:
            continue  # é o "REV." do carimbo, não o da tabela de revisões
        revs = [x["text"] for x in words
                if re.fullmatch(r"\d{2}", x["text"])
                and w["bottom"] < x["top"] < w["bottom"] + 120
                and w["x0"] - 8 < (x["x0"] + x["x1"]) / 2 < w["x1"] + 12]
        if revs:
            return max(revs)
    return "00"


# ------------------------------------------------- tabela de matéria-prima

def extrair_bom_mp(pdf) -> list:
    """Extrai a tabela ITEM | DESCRIÇÃO | COMPRIMENTO | QTD. de todas as folhas."""
    itens = []
    for pnum, page in enumerate(pdf.pages, 1):
        words = page.extract_words()
        hdr = defaultdict(list)
        for w in words:
            t = w["text"].upper().rstrip(".")
            if t in ("ITEM", "DESCRIÇÃO", "COMPRIMENTO", "QTD"):
                hdr[t].append(w)
        achado = None
        for wi in hdr["ITEM"]:
            linha = {k: w for k in ("DESCRIÇÃO", "COMPRIMENTO", "QTD")
                     for w in hdr[k] if abs(w["top"] - wi["top"]) < 3}
            if len(linha) == 3:
                achado = {"ITEM": wi, **linha}
                break
        if not achado:
            continue
        centros = {k: (v["x0"] + v["x1"]) / 2 for k, v in achado.items()}
        top0 = achado["ITEM"]["bottom"]
        x_min = achado["ITEM"]["x0"] - 20
        x_max = achado["QTD"]["x1"] + 25
        abaixo = [w for w in words if w["top"] > top0
                  and x_min < w["x0"] and w["x1"] < x_max]
        linhas = defaultdict(list)
        for w in abaixo:
            linhas[round(w["top"] / 3)].append(w)
        for _, ws in sorted(linhas.items()):
            ws.sort(key=lambda w: w["x0"])
            cols = defaultdict(list)
            for w in ws:
                cw = (w["x0"] + w["x1"]) / 2
                k = min(centros, key=lambda k: abs(cw - centros[k]))
                cols[k].append(w["text"])
            ci, cd = cols["ITEM"], cols["DESCRIÇÃO"]
            cc, cq = cols["COMPRIMENTO"], cols["QTD"]
            if len(ci) == 1 and ci[0].isdigit() and cd and cq and cq[-1].isdigit():
                itens.append(ItemMP(int(ci[0]), " ".join(cd),
                                    " ".join(cc) or "-", int(cq[-1]), pnum))
            elif ws and not (ci and ci[0].isdigit()):
                break  # fim da tabela
    return itens


# ---------------------------------------------------------------- pipeline

def separar_descricao(desc: str, comprimento: str):
    """'METALON 50 X 50 X 3,17' + '1890.00' -> ('METALON', '50 X 50 X 3,17 X 1890')"""
    desc = desc.strip()
    up = desc.upper()
    prefixo = next((p for p in PREFIXOS_MP if up.startswith(p)), None)
    if prefixo:
        resto = desc[len(prefixo):].strip()
        comp = comprimento.strip()
        comp_num = re.fullmatch(r"(\d+)(?:[.,]0+)?", comp)
        if comp_num:
            comp = comp_num.group(1)
        if comp.upper() in ("CONF. DESENHO", "CONF DESENHO", "-", ""):
            dim = (resto + " - CONFORME DESENHO").strip(" -") if resto else "CONFORME DESENHO"
        elif resto:
            dim = f"{resto} X {comp}"
        else:
            dim = comp
        # OXICORTE A / LASER B: a letra faz parte da descrição
        if prefixo in ("OXICORTE", "LASER") and re.fullmatch(r"[A-Z]", resto or ""):
            return desc, "CONFORME DESENHO"
        return prefixo, dim
    return desc, comprimento


def processar_pdf(caminho: Path) -> DadosDesenho:
    d = DadosDesenho(arquivo=caminho.name, caminho=str(caminho))
    try:
        with pdfplumber.open(caminho) as pdf:
            carimbo = extrair_carimbo(pdf.pages[0])
            d.desenho = carimbo["desenho"]
            d.rev = carimbo["rev"]
            d.qtde = carimbo["qtde"]
            d.nome = carimbo["nome"]
            d.material = carimbo["material"]
            d.dimensao = carimbo["dimensao"]
            d.massa = carimbo["massa"]
            d.titulo = carimbo["titulo"]
            d.itens_mp = extrair_bom_mp(pdf)
            # carimbo de conjunto às vezes traz MATERIAL "N/A" na folha 1;
            # busca nas demais folhas um material válido
            if d.material.upper().replace(".", "") in ("N/A", "NA", "") and len(pdf.pages) > 1:
                for page in pdf.pages[1:]:
                    c2 = extrair_carimbo(page)
                    mat2 = c2.get("material", "")
                    if mat2 and mat2.upper().replace(".", "") not in ("N/A", "NA"):
                        d.material = mat2
                        break
        if not d.desenho:
            d.erro = "Nº de desenho não encontrado (PDF fora do padrão ou sem texto)"
    except Exception as e:  # PDF corrompido, protegido etc.
        d.erro = f"Falha ao ler PDF: {e}"
    return d


def gerar_linhas(d: DadosDesenho) -> list:
    """Converte os dados de um desenho nas linhas da planilha OS ACOMPANHAMENTO.

    Colunas: DESENHO, REV, QTDE, PROCESSO, DESCRIÇÃO, DIMENSÃO, MATERIAL, QTD
    """
    linhas = []
    if d.itens_mp:  # desenho com tabela de matéria-prima -> 1 linha por corte
        for i, it in enumerate(d.itens_mp):
            descricao, dimensao = separar_descricao(it.descricao, it.comprimento)
            linhas.append({
                "desenho": d.desenho,
                "rev": d.rev if i == 0 else "",
                "qtde": d.qtde if i == 0 else "",
                "processo": "",
                "descricao": descricao,
                "dimensao": dimensao,
                "material": d.material,
                "qtd": it.qtd,
                "arquivo": d.arquivo,
            })
    else:  # peça simples -> 1 linha com dados do carimbo
        linhas.append({
            "desenho": d.desenho,
            "rev": d.rev,
            "qtde": d.qtde,
            "processo": "",
            "descricao": "",
            "dimensao": d.dimensao or "CONFORME DESENHO",
            "material": d.material,
            "qtd": d.qtde,
            "arquivo": d.arquivo,
        })
    return linhas


def escanear_pasta(raiz: Path, callback=None):
    """Varre a pasta raiz recursivamente. callback(atual, total, nome) para progresso."""
    pdfs = sorted(raiz.rglob("*.pdf"), key=lambda p: p.name.lower())
    resultados = []
    for i, p in enumerate(pdfs, 1):
        if callback:
            callback(i, len(pdfs), p.name)
        resultados.append(processar_pdf(p))
    return resultados
