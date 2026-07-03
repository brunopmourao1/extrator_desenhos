# -*- coding: utf-8 -*-
"""Testes de regressão do motor de extração.

Gabarito completo em docs/07-plano-testes.md. Requer os PDFs reais em amostras/.
Completar CARIMBO_ESPERADO com a tabela integral do doc 07 na Fase 1.
"""
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "referencia"))
from extrator import processar_pdf, gerar_linhas, escanear_pasta  # noqa: E402

AMOSTRAS = Path(__file__).parent.parent / "amostras"

pytestmark = pytest.mark.skipif(
    not list(AMOSTRAS.glob("*.pdf")),
    reason="PDFs de teste ausentes em amostras/ (ver docs/07 §2)")

CARIMBO_ESPERADO = {
    "1808-00-001.pdf": ("1808-00-001", "00", "01", "ESTRUTURA", "SAE 1020", 48),
    "1808-00-002.pdf": ("1808-00-002", "00", "02", "CONJ SOLDADO", "SAE 1020", 6),
    "1808-00-003.pdf": ("1808-00-003", "00", "01", "ESTRUTURA BANCADA", "SAE 1020", 7),
    "1808-00-004.pdf": ("1808-00-004", "00", "02", "SUPORTE DA CAIXA KLT", "SAE 1020", 3),
    "1808-00-026.pdf": ("1808-00-026", "00", "02", "FECHAMENTO", "PERFIL DE ALUMÍNIO", 1),
    "1808-00-027.pdf": ("1808-00-027", "00", "02", "FECHAMENTO", "PERFIL DE ALUMÍNIO", 1),
    "1808-00-038.pdf": ("1808-00-038", "00", "01", "CHAPA PISO", "ALUMÍNIO", 1),
    "1808-00-067.pdf": ("1808-00-067", "00", "01", "BASE DOS BERÇOS", "ALUMÍNIO NAVAL", 1),
    "1808-00-068.pdf": ("1808-00-068", "00", "01", "PLACA", "ALUMÍNIO NAVAL", 1),
    "1808-00-069.pdf": ("1808-00-069", "00", "02", "PLACA", "ALUMÍNIO NAVAL", 1),
    "1808-00-083.pdf": ("1808-00-083", "00", "02", "EIXO", "SAE 1045 RETIFICADO", 1),
    "1808-00-172.pdf": ("1808-00-172", "00", "01", "BERÇO", "ALUMÍNIO NAVAL", 1),
    "1808-00-173.pdf": ("1808-00-173", "00", "01", "BERÇO", "ALUMÍNIO NAVAL", 1),
    "1808-00-174.pdf": ("1808-00-174", "00", "01", "PISADOR", "ALUMÍNIO NAVAL", 1),
    "1808-00-175.pdf": ("1808-00-175", "00", "01", "PISADOR", "ALUMÍNIO NAVAL", 1),
    "1808-00-204.pdf": ("1808-00-204", "00", "02", "PUNÇÃO", "VC 131", 1),
    "1808-00-207.pdf": ("1808-00-207", "00", "01", "SUP. PISTOLA DE AR", "PLA", 1),
    "1808-00-001-OXICORTE_B.pdf": ("1808-00-001-OXICORTE B", "00", "04", "OXICORTE", "SAE 1020", 1),
    "1808-00-001-OXICORTE_C.pdf": ("1808-00-001-OXICORTE C", "00", "01", "BASE", "SAE 1020", 1),
}


@pytest.mark.parametrize("arquivo,esperado", CARIMBO_ESPERADO.items())
def test_carimbo(arquivo, esperado):
    d = processar_pdf(AMOSTRAS / arquivo)
    assert d.erro == ""
    assert (d.desenho, d.rev, d.qtde, d.nome, d.material,
            len(gerar_linhas(d))) == esperado


def test_total_geral():
    res = escanear_pasta(AMOSTRAS)
    res = [d for d in res if d.arquivo in CARIMBO_ESPERADO]
    assert sum(1 for d in res if d.erro) == 0
    assert sum(len(gerar_linhas(d)) for d in res) == 79


def test_bom_001_completa_e_sem_buracos():
    d = processar_pdf(AMOSTRAS / "1808-00-001.pdf")
    itens = sorted(d.itens_mp, key=lambda i: i.item)
    assert [i.item for i in itens] == list(range(1, 49))
    assert (itens[36].descricao, itens[36].comprimento, itens[36].qtd) == \
        ("CHAPA", '1" X 460 X 465', 2)
    assert (itens[41].descricao, itens[41].comprimento, itens[41].qtd) == \
        ("OXICORTE A", "CONF. DESENHO", 4)


def test_conjunto_nao_duplica_e_material_multifolha():
    d = processar_pdf(AMOSTRAS / "1808-00-002.pdf")
    assert len(d.itens_mp) == 6           # só a MP da folha 2; conjunto ignorado
    assert d.material == "SAE 1020"       # não o "N/A" da folha 1


def test_gerar_linhas_002():
    d = processar_pdf(AMOSTRAS / "1808-00-002.pdf")
    lns = gerar_linhas(d)
    assert lns[0]["desenho"] == "1808-00-002" and lns[0]["rev"] == "00"
    assert lns[1]["desenho"] == "1808-00-002" and lns[1]["rev"] == ""
    assert (lns[0]["descricao"], lns[0]["dimensao"], lns[0]["qtd"]) == \
        ("METALON", "30 X 30 X 1,5 X 704", 4)
    assert (lns[5]["descricao"], lns[5]["dimensao"], lns[5]["qtd"]) == \
        ("CANTONEIRA", "25,4 X 25,4 X 3,17 X 40", 8)
