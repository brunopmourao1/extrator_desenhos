# 03 — Especificação de Extração (VALIDADA)

Este documento registra os algoritmos **validados com 100% de acerto** em 19 PDFs
reais da OS 1808 (03/07/2026): carimbo 19/19, tabelas de MP 64/64 itens
(48+6+7+3), sufixos de numeração e conjuntos multi-folha. A implementação de
referência está em `referencia/extrator.py`. Qualquer alteração deve passar nos
testes de regressão de `docs/07-plano-testes.md`.

## 1. Princípio fundamental

**Nunca confiar na ordem do texto extraído do PDF.** PDFs gerados por CAD
(SolidWorks) emitem o texto em ordem arbitrária — regex sobre `extract_text()`
falha de forma imprevisível (validado: abordagem sequencial errou DESENHO e NOME
em 7/7 desenhos). Toda extração usa **coordenadas de palavras**
(`page.extract_words()` → dicts com `text, x0, x1, top, bottom`).

## 2. Anatomia do desenho (padrão SGQ FOR ENG 004 REV 06)

- Folhas A3/A2/A1/A0; carimbo no canto inferior direito com rótulos fixos:
  `N° DESENHO:`, `NOME:`, `MATERIAL:`, `QTDE:`, `DIMENSÃO:`, `MASSA (Kg):`,
  `TÍTULO:`, `TRAT. TÉRMICO:`.
- Tabela de revisões no topo: `REV. | ANTIGO | ATUAL | DATA | RESPONSÁVEL`,
  linhas como `00 - EMISSÃO INICIAL 24/04/2026 PAULO LOPES`.
- Desenhos de estrutura/conjunto soldado podem ter, em qualquer folha:
  - **Tabela de matéria-prima:** `ITEM | DESCRIÇÃO | COMPRIMENTO | QTD.` ← EXTRAIR
  - **Tabela de conjunto:** `ITEM | Nº DA PEÇA | QTD. | MONTADOR` ← IGNORAR
    (referencia sub-desenhos que têm PDF próprio; extrair causaria duplicidade)
  - **Tabela de Furos:** `RÓTULO | LOCX | LOC Y | TAMANHO` ← IGNORAR
- Conjuntos multi-folha: carimbo se repete em cada folha; a tabela de MP pode
  estar em folha ≠ 1 (ex.: 1808-00-002 tem conjunto na folha 1 e MP na folha 2).

## 3. Nº do desenho

Formato: `\d{4}-\d{2}-\d{3}` com sufixo opcional (ex. `1808-00-001-OXICORTE B`,
`1808-00-001-LASER A`). No carimbo, o valor pode estar **acima ou abaixo** do
rótulo `N° DESENHO:` dependendo da ordem de emissão do CAD.

Algoritmo (função `_num_desenho`):
1. Localizar as palavras consecutivas `N°` + `DESENHO:`.
2. Candidatos: palavras a até 25 pt abaixo do rótulo OU 15 pt acima, dentro da
   janela horizontal `x0-40 .. x0+220`, que casem `\d{4}-\d{2}-\d{3}`, sejam
   `OXICORTE`/`LASER` ou uma letra isolada `[A-Z]` (o sufixo quebra em tokens).
3. Tomar a linha (mesmo `top` arredondado) do primeiro candidato numérico e
   juntar os tokens dela em ordem de `x0`.
4. Fallback: primeiro match do padrão no texto bruto da página.

## 4. Demais campos do carimbo

Função `extrair_carimbo(page)`:

| Campo | Rótulo âncora | Posição do valor |
|-------|---------------|------------------|
| nome | `NOME:` | abaixo do rótulo (célula do carimbo) |
| material | `MATERIAL:` | abaixo |
| qtde | `QTDE:` | abaixo |
| dimensao | `DIMENSÃO:` | mesma linha, à direita; fallback abaixo |
| titulo | `TÍTULO:` | mesma linha, à direita (pode continuar na linha seguinte — aceitável truncar) |
| massa | — | regex no texto: `MASSA \(Kg\):\s*([\d.,]+)` |
| rev | ver §4.1 | posicional pela tabela de revisões |

**Atenção à lista de exclusão de rótulos (`_IGNORAR`):** ela NÃO pode conter
palavras comuns do português como `DE` — isso corrompeu valores reais
("PERFIL **DE** ALUMÍNIO" → "PERFIL ALUMÍNIO", "SUP. PISTOLA **DE** AR" →
"SUP. PISTOLA AR"). Manter só tokens que são inequivocamente rótulos do carimbo.

### 4.1 Revisão vigente (posicional — bug corrigido em 03/07/2026)

A abordagem por regex no texto (`(\d{2})\s+\S.*?EMISSÃO INICIAL`) FALHOU em
produção de teste: no 1808-00-026, uma cota "30" do desenho veio adjacente no
texto extraído (`"30 00 - EMISSÃO INICIAL"`) e o `max()` devolveu REV=30.
Além disso, linhas de revisão > 00 não contêm palavras-chave previsíveis
(formato: `01 | <estado antigo> | <estado novo> | data | responsável`).

Algoritmo correto (`_rev_vigente(words)`):
1. Localizar a palavra `REV.` que tenha `DATA` e `RESPONSÁVEL` na **mesma
   linha** (isso a distingue do "REV." do carimbo e de qualquer cota).
2. Coletar tokens `\d{2}` abaixo desse cabeçalho (até ~120 pt) cujo **centro
   horizontal** caia na coluna do rótulo `REV.` (janela `x0-8 .. x1+12`).
3. Revisão vigente = `max()` dos tokens; fallback `"00"`.

Captura de valor "abaixo": palavras com `rótulo.bottom-2 < top < rótulo.bottom+20`
e `x0` na janela `rótulo.x0-10 .. rótulo.x0+250`, excluindo tokens que são outros
rótulos ou contêm `:`; ordenar por `(top, x0)` e juntar com espaço.

**Fallback de material em conjuntos:** se o material da folha 1 for
`N/A`/`NA`/vazio e o PDF tiver mais folhas, extrair carimbo das folhas seguintes
e usar o primeiro material válido (caso real: 1808-00-002 → folha 1 "N/A",
folha 2 "SAE 1020").

## 5. Tabela de matéria-prima (algoritmo posicional)

Função `extrair_bom_mp(pdf)` — o algoritmo decisivo do projeto. As tentativas
com `extract_tables()` (linhas desenhadas) e regex por linha **falharam**
(0 tabelas detectadas / 19 de 48 itens). O que funciona:

1. **Localizar o cabeçalho:** em cada página, indexar palavras cujo texto
   (upper, sem ponto final) seja `ITEM`, `DESCRIÇÃO`, `COMPRIMENTO` ou `QTD`.
   O cabeçalho é um `ITEM` que tenha os outros três na **mesma linha**
   (`|Δtop| < 3 pt`).
2. **Centros de coluna:** ponto médio horizontal `(x0+x1)/2` de cada palavra do
   cabeçalho.
3. **Região de dados:** palavras com `top > ITEM.bottom`, entre
   `ITEM.x0-20` e `QTD.x1+25`.
4. **Agrupar em linhas:** por `round(top/3)` (tolerância de ~3 pt).
5. **Classificar cada palavra na coluna de centro mais próximo** ao centro da
   palavra — robusto para colunas centralizadas de largura variável.
6. **Validar linha:** coluna ITEM = exatamente 1 token numérico; DESCRIÇÃO
   não vazia; último token de QTD numérico. Linha com ITEM não numérico
   encerra a tabela (evita vazar para o carimbo abaixo).
7. Repetir para todas as páginas (MP pode estar em qualquer folha).

Conteúdos reais a suportar (dos PDFs de teste):

```
1   METALON 50 X 50 X 3,17        1890.00          1
37  CHAPA                         1" X 460 X 465   2    ← dimensão na col. COMPRIMENTO
40  BARRA CHATA                   3/8" X 2" X 165  1    ← descrição de 2 palavras
42  OXICORTE A                    CONF. DESENHO    4    ← letra faz parte da descrição
6   CANTONEIRA 25,4 X 25,4 X 3,17 40.00            8
```

## 6. Pós-processamento: `separar_descricao(desc, comprimento)`

Converte o item de MP em (DESCRIÇÃO, DIMENSÃO SOLICITADA) da planilha:

- Prefixos conhecidos (`PREFIXOS_MP`): `BARRA CHATA`, `BARRA REDONDA`,
  `BARRA QUADRADA`, `METALON`, `CANTONEIRA`, `CHAPA`, `OXICORTE`, `LASER`,
  `PERFIL DE ALUMÍNIO`, `PERFIL`, `TUBO`, `VIGA`, `BARRA` — testar os mais
  longos primeiro.
- `METALON 50 X 50 X 3,17` + `1890.00` → (`METALON`, `50 X 50 X 3,17 X 1890`)
  — comprimento numérico perde o `.00`.
- `CHAPA` + `1" X 460 X 465` → (`CHAPA`, `1" X 460 X 465`).
- `OXICORTE A` + `CONF. DESENHO` → (`OXICORTE A`, `CONFORME DESENHO`)
  — a letra permanece na descrição.
- Descrição sem prefixo conhecido → passar (desc, comprimento) sem transformar.

## 7. Geração de linhas: `gerar_linhas(DadosDesenho)`

- **Com itens de MP:** uma linha por item; **DESENHO se repete em todas as
  linhas** (as tabelas dinâmicas da planilha filtram pela coluna A); REV e QTDE
  apenas na primeira linha do desenho (padrão da planilha preenchida da
  LS Control); MATERIAL do carimbo em todas; QTD = qtd do item.
- **Sem itens de MP (peça simples):** uma linha; DESCRIÇÃO vazia (decisão
  humana); DIMENSÃO do carimbo ou `CONFORME DESENHO` se vazia; QTD = QTDE.

## 8. Casos de falha controlada (→ log "revisar manualmente")

- PDF sem camada de texto (escaneado): nº do desenho não encontrado.
- PDF protegido/corrompido: exceção do pdfplumber capturada.
- Carimbo de outro template: rótulos-âncora ausentes → campos vazios; se nem o
  padrão numérico existir no texto, erro de "fora do padrão".

## 9. Resultados de validação (baseline de regressão)

19 PDFs → 79 linhas, 0 erros. Detalhe por arquivo em `docs/07-plano-testes.md`.
