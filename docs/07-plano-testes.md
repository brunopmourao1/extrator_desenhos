# 07 — Plano de Testes

## 1. Estratégia

Três níveis: (a) **regressão automatizada do motor** com pytest sobre os PDFs
reais de `amostras/` — o coração da qualidade do projeto; (b) **teste manual
guiado do exportador** com cópia da planilha modelo (exige Excel);
(c) **teste exploratório da GUI** no fluxo completo.

Regra de ouro: nenhuma alteração em `extrator.py` é aceita com pytest vermelho.

## 2. Massa de teste

Copiar para `amostras/` os 19 PDFs reais da OS 1808 usados na validação
original (lista abaixo) e uma **cópia** da planilha
`FOR ENG 003 ... MODELO LISTA NOVA.XLSM`. Esses arquivos não devem ir para
repositório público (desenhos de cliente).

## 3. Gabarito de regressão — carimbo (valores EXATOS esperados)

Gerado pela implementação validada em 03/07/2026 (19 PDFs → 79 linhas, 0 erros):

| Arquivo | DESENHO | REV | QTDE | NOME | MATERIAL | DIMENSÃO | MASSA | Linhas |
|---|---|---|---|---|---|---|---|---|
| 1808-00-001-OXICORTE_B.pdf | 1808-00-001-OXICORTE B | 00 | 04 | OXICORTE | SAE 1020 | 1" X 100 X 100 | 1.52 | 1 |
| 1808-00-001-OXICORTE_C.pdf | 1808-00-001-OXICORTE C | 00 | 01 | BASE | SAE 1020 | 3/4" X 450 X 1103 | 73.66 | 1 |
| 1808-00-001.pdf | 1808-00-001 | 00 | 01 | ESTRUTURA | SAE 1020 | *(vazia)* | 1058.74 | 48 |
| 1808-00-002.pdf | 1808-00-002 | 00 | 02 | CONJ SOLDADO | SAE 1020 | *(vazia)* | 23.89 | 6 |
| 1808-00-003.pdf | 1808-00-003 | 00 | 01 | ESTRUTURA BANCADA | SAE 1020 | *(vazia)* | 56.52 | 7 |
| 1808-00-004.pdf | 1808-00-004 | 00 | 02 | SUPORTE DA CAIXA KLT | SAE 1020 | *(vazia)* | 3.86 | 3 |
| 1808-00-026.pdf | 1808-00-026 | 00 | 02 | FECHAMENTO | PERFIL DE ALUMÍNIO | *(vazia)* | 6.26 | 1 |
| 1808-00-027.pdf | 1808-00-027 | 00 | 02 | FECHAMENTO | PERFIL DE ALUMÍNIO | *(vazia)* | 9.59 | 1 |
| 1808-00-038.pdf | 1808-00-038 | 00 | 01 | CHAPA PISO | ALUMÍNIO | *(vazia)* | 9.31 | 1 |
| 1808-00-067.pdf | 1808-00-067 | 00 | 01 | BASE DOS BERÇOS | ALUMÍNIO NAVAL | *(vazia)* | 18.66 | 1 |
| 1808-00-068.pdf | 1808-00-068 | 00 | 01 | PLACA | ALUMÍNIO NAVAL | 7/8" x 255 x 355 | 5.01 | 1 |
| 1808-00-069.pdf | 1808-00-069 | 00 | 02 | PLACA | ALUMÍNIO NAVAL | 7/8" X 205 X 255 | 2.62 | 1 |
| 1808-00-083.pdf | 1808-00-083 | 00 | 02 | EIXO | SAE 1045 RETIFICADO | Ø 12 X 215 | 0.18 | 1 |
| 1808-00-172.pdf | 1808-00-172 | 00 | 01 | BERÇO | ALUMÍNIO NAVAL | 60 X 65 X 125 | 0.55 | 1 |
| 1808-00-173.pdf | 1808-00-173 | 00 | 01 | BERÇO | ALUMÍNIO NAVAL | 60 X 65 X 125 | 0.55 | 1 |
| 1808-00-174.pdf | 1808-00-174 | 00 | 01 | PISADOR | ALUMÍNIO NAVAL | 105 X 115 X 145 | 1.70 | 1 |
| 1808-00-175.pdf | 1808-00-175 | 00 | 01 | PISADOR | ALUMÍNIO NAVAL | 105 X 115 X 145 | 1.7 | 1 |
| 1808-00-204.pdf | 1808-00-204 | 00 | 02 | PUNÇÃO | VC 131 | Ø1.1/4" X 35 | 0.12 | 1 |
| 1808-00-207.pdf | 1808-00-207 | 00 | 01 | SUP. PISTOLA DE AR | PLA | *(vazia)* | 0.19 | 1 |

Total: **19 PDFs → 79 linhas → 0 erros**.

## 4. Gabarito de regressão — tabela de matéria-prima

| Desenho | Itens esperados | Amostras que DEVEM bater exatamente |
|---|---|---|
| 1808-00-001 | 48 (itens 1–48, folha 1) | item 1: `METALON 50 X 50 X 3,17` / `1890.00` / qtd 1 · item 36: `METALON 200 X 100 X 4,76` / `1690.00` / qtd 2 · item 37: `CHAPA` / `1" X 460 X 465` / qtd 2 · item 40: `BARRA CHATA` / `3/8" X 2" X 165` / qtd 1 · item 42: `OXICORTE A` / `CONF. DESENHO` / qtd 4 · item 48: `LASER C` / `CONF. DESENHO` / qtd 1 |
| 1808-00-002 | 6 (folha 2) | item 6: `CANTONEIRA 25,4 X 25,4 X 3,17` / `40.00` / qtd 8 |
| 1808-00-003 | 7 (folha 1) | item 7: `CHAPA` / `1" X 33 X 33` / qtd 4 |
| 1808-00-004 | 3 (folha 1) | item 1: `CANTONEIRA 38,1 X 38,1 X 3,17` / `915.00` / qtd 1 |
| todos os demais | 0 | — |

Comportamentos que devem ser verificados nesses casos:
- 1808-00-002: a tabela de conjunto da folha 1 (`Nº DA PEÇA`: 1808-00-002/050/051/052)
  **não** gera linhas; MATERIAL vem da folha 2 (`SAE 1020`), não do "N/A" da folha 1.
- 1808-00-001 e 1808-00-068: as Tabelas de Furos **não** geram linhas.
- Itens sequenciais completos: 1..N sem buracos (o item 4 do -001 já foi perdido
  por um algoritmo anterior — teste de não-regressão específico).

## 5. Gabarito — gerar_linhas (transformação para planilha)

Para `1808-00-002` (6 linhas):

| # | desenho | rev | qtde | descricao | dimensao | material | qtd |
|---|---------|-----|------|-----------|----------|----------|-----|
| 1 | 1808-00-002 | 00 | 02 | METALON | 30 X 30 X 1,5 X 704 | SAE 1020 | 4 |
| 2 | 1808-00-002 | *(vazio)* | *(vazio)* | METALON | 30 X 30 X 1,5 X 644 | SAE 1020 | 1 |
| 3 | 1808-00-002 | — | — | METALON | 30 X 30 X 1,5 X 470 | SAE 1020 | 4 |
| 4 | 1808-00-002 | — | — | METALON | 30 X 30 X 1,5 X 415 | SAE 1020 | 4 |
| 5 | 1808-00-002 | — | — | METALON | 30 X 30 X 1,5 X 355 | SAE 1020 | 2 |
| 6 | 1808-00-002 | — | — | CANTONEIRA | 25,4 X 25,4 X 3,17 X 40 | SAE 1020 | 8 |

Observação: DESENHO repete em todas as linhas (requisito das tabelas dinâmicas);
REV e QTDE só na primeira linha de cada desenho.

Para `1808-00-172` (peça simples, 1 linha):
`desenho=1808-00-172, rev=00, qtde=01, descricao="", dimensao=60 X 65 X 125,
material=ALUMÍNIO NAVAL, qtd=01`.

Para OXICORTE/LASER desdobrados do -001: `descricao="OXICORTE A"`,
`dimensao="CONFORME DESENHO"`.

## 6. Casos negativos do motor

| Caso | Entrada | Esperado |
|------|---------|----------|
| PDF sem texto | qualquer PDF de imagem/scan | `erro` preenchido; varredura continua |
| PDF corrompido | arquivo truncado `.pdf` | idem |
| PDF não-desenho | um manual/catálogo qualquer | nº não encontrado → `erro`; sem exceção |
| Pasta sem PDFs | dir vazio | lista vazia; UI informa 0 arquivos |

## 7. Testes do exportador (manuais, Excel obrigatório)

1. **Inserção básica:** exportar 3 linhas numa cópia da planilha → linhas nas
   posições certas (primeira vazia ≥ 6), somente colunas A,B,C,D,G,H,I,J.
2. **Preservação:** após salvar, abrir no Excel → macros/botões operantes,
   aba TAB. DINAMICA íntegra, formatação condicional das colunas STATUS ativa.
3. **Backup:** arquivo `_BACKUP_...` criado e abrindo no Excel.
4. **Duplicidade:** exportar duas vezes → 2ª execução insere 0 e loga os pulos.
5. **Arquivo aberto:** com a planilha aberta no Excel → erro claro, sem
   corromper original, sem processo EXCEL.EXE órfão (conferir no Gerenciador
   de Tarefas).
6. **Aba ausente:** planilha qualquer sem `OS ACOMPANHAMENTO` → RuntimeError
   amigável.

## 8. Testes de GUI (exploratórios, roteiro mínimo)

Escanear `amostras/` → 79 linhas na tabela · editar uma célula e conferir que a
edição vai para a exportação · trocar PROCESSO via combo e digitar valor fora da
lista · desmarcar 5 linhas → exportação insere 74 · caminho colado com aspas
funciona · UI responsiva durante varredura · log exibe avisos de PDFs ruins.

## 9. Esqueleto do teste automatizado

```python
# tests/test_extrator.py
import pytest
from pathlib import Path
from extrator import processar_pdf, gerar_linhas, escanear_pasta

AMOSTRAS = Path(__file__).parent.parent / "amostras"

CARIMBO_ESPERADO = {
    # arquivo: (desenho, rev, qtde, nome, material, n_linhas)
    "1808-00-001.pdf": ("1808-00-001", "00", "01", "ESTRUTURA", "SAE 1020", 48),
    "1808-00-002.pdf": ("1808-00-002", "00", "02", "CONJ SOLDADO", "SAE 1020", 6),
    "1808-00-026.pdf": ("1808-00-026", "00", "02", "FECHAMENTO", "PERFIL DE ALUMÍNIO", 1),
    "1808-00-207.pdf": ("1808-00-207", "00", "01", "SUP. PISTOLA DE AR", "PLA", 1),
    "1808-00-001-OXICORTE_B.pdf": ("1808-00-001-OXICORTE B", "00", "04", "OXICORTE", "SAE 1020", 1),
    # ... completar com TODA a tabela da seção 3
}

@pytest.mark.parametrize("arquivo,esperado", CARIMBO_ESPERADO.items())
def test_carimbo(arquivo, esperado):
    d = processar_pdf(AMOSTRAS / arquivo)
    assert d.erro == ""
    assert (d.desenho, d.rev, d.qtde, d.nome, d.material,
            len(gerar_linhas(d))) == esperado

def test_total_geral():
    res = escanear_pasta(AMOSTRAS)
    assert sum(1 for d in res if d.erro) == 0
    assert sum(len(gerar_linhas(d)) for d in res) == 79

def test_bom_001_completa_e_sem_buracos():
    d = processar_pdf(AMOSTRAS / "1808-00-001.pdf")
    itens = sorted(d.itens_mp, key=lambda i: i.item)
    assert [i.item for i in itens] == list(range(1, 49))
    assert (itens[36].descricao, itens[36].comprimento, itens[36].qtd) == \
        ("CHAPA", '1" X 460 X 465', 2)

def test_conjunto_nao_duplica_e_material_multifolha():
    d = processar_pdf(AMOSTRAS / "1808-00-002.pdf")
    assert len(d.itens_mp) == 6          # só a MP da folha 2
    assert d.material == "SAE 1020"      # não o "N/A" da folha 1
```
