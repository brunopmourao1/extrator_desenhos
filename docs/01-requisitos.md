# 01 — Especificação de Requisitos

**Projeto:** Extrator de Desenhos — LS Control
**Versão:** 1.0 · **Data:** 03/07/2026 · **Autor:** Bruno (LS Control)

## 1. Contexto e problema

A LS Control produz, por Ordem de Serviço (OS), dezenas a centenas de desenhos
mecânicos em PDF (gerados por CAD no padrão de folha **SGQ FOR ENG 004 REV 06**),
organizados em uma pasta raiz com subpastas. Hoje, a equipe abre cada PDF
manualmente e digita os dados do carimbo e da lista de materiais na planilha de
acompanhamento de montagem mecânica (`FOR ENG 003`, arquivo `.xlsm` com macros,
tabelas dinâmicas e formatação condicional). O processo é lento e sujeito a erro
de digitação.

O aplicativo automatiza essa alimentação: varre a pasta, extrai os dados,
apresenta para revisão e insere as linhas na planilha existente.

## 2. Escopo

**Dentro do escopo:** varredura recursiva de PDFs; extração de carimbo e tabela
de matéria-prima; tela de revisão editável; exportação para a aba
`OS ACOMPANHAMENTO` de um `.xlsm` existente; backup automático; log de problemas;
distribuição como `.exe` único.

**Fora do escopo (v1):** OCR de desenhos escaneados; consolidação de cortes em
barras de compra (decisão de negócio: listar cortes como no desenho); edição das
colunas de acompanhamento de produção (compras, usinagem, tratamentos); leitura
de desenhos fora do padrão SGQ FOR ENG 004.

## 3. Requisitos funcionais

| ID | Requisito |
|----|-----------|
| RF-01 | O usuário informa a pasta raiz por campo de texto editável ou diálogo "Procurar", podendo alterá-la antes de iniciar. |
| RF-02 | O app varre a pasta raiz e todas as subpastas buscando `*.pdf`, ordenados por nome. |
| RF-03 | De cada PDF, extrair do carimbo: nº do desenho (com sufixo, ex. `1808-00-001-OXICORTE B`), revisão vigente, QTDE, NOME, MATERIAL, DIMENSÃO, MASSA e TÍTULO. |
| RF-04 | Se o desenho contiver tabela de matéria-prima (`ITEM \| DESCRIÇÃO \| COMPRIMENTO \| QTD.`), gerar **uma linha por item de corte**, sem consolidação. |
| RF-05 | Se não contiver tabela de MP, gerar **uma linha** com DIMENSÃO e MATERIAL do carimbo. |
| RF-06 | Ignorar a "Tabela de Furos" e a tabela de conjunto (`ITEM \| Nº DA PEÇA \| QTD.`) — sub-peças de conjunto têm PDF próprio e gerariam duplicidade. |
| RF-07 | Exibir barra de progresso (arquivo atual / total) durante a varredura, sem travar a interface. |
| RF-08 | Apresentar as linhas extraídas em tabela editável: qualquer célula corrigível; coluna PROCESSO com lista suspensa editável (CNC, USINAGEM, ESTRUTURA E CONJ. SOLDADO, CALDEIRARIA, CORTE ÁGUA, IMPRESSÃO 3D, COMPRA); checkbox por linha para incluir/excluir da exportação; marcar/desmarcar todos. |
| RF-09 | PDFs ilegíveis, sem texto ou fora do padrão entram no log como "revisar manualmente" e **não interrompem** a varredura. |
| RF-10 | O usuário informa o caminho da planilha `.xlsm` destino (campo + "Procurar"). |
| RF-11 | Antes de gravar, criar backup do arquivo (`NOME_BACKUP_AAAAMMDD_HHMMSS.xlsm`) na mesma pasta. |
| RF-12 | Inserir as linhas marcadas a partir da primeira linha vazia da coluna A da aba `OS ACOMPANHAMENTO` (dados começam na linha 6). |
| RF-13 | Pular desenhos cujo nº já exista na coluna A, informando no log quais foram pulados. |
| RF-14 | Preencher somente as colunas A, B, C, D, G, H, I, J (ver docs/04); jamais tocar nas demais. |
| RF-15 | Exibir confirmação antes de exportar e resumo ao final (inseridas / puladas / backup). |

## 4. Requisitos não funcionais

| ID | Requisito |
|----|-----------|
| RNF-01 | Plataforma: Windows 10/11, 64 bits. |
| RNF-02 | Distribuição: executável único via PyInstaller, sem exigir Python instalado. |
| RNF-03 | A exportação usa o Excel instalado na máquina via COM (xlwings) para preservar 100% de macros, tabelas dinâmicas e formatação do `.xlsm`. Excel é pré-requisito da máquina. |
| RNF-04 | Interface, mensagens, log e documentação em português brasileiro. |
| RNF-05 | Varredura de 200 PDFs em menos de 2 minutos em máquina de escritório típica. |
| RNF-06 | O motor de extração (`extrator.py`) não depende de GUI nem de Excel — testável isoladamente com pytest. |
| RNF-07 | Nenhuma perda de dados possível na planilha: backup obrigatório antes de qualquer gravação; gravação célula a célula apenas nas colunas mapeadas. |

## 5. Decisões de negócio registradas

1. **Desdobrar matéria-prima:** cada item da tabela de MP vira uma linha
   (decisão do usuário em 03/07/2026), listando os cortes exatamente como no
   desenho — sem consolidar metalons em barras de 6000 mm.
2. **Saída:** colar em planilha `.xlsm` já existente (não gerar arquivo novo).
3. **Fluxo:** revisão obrigatória em tela antes de exportar.
4. **PROCESSO e DESCRIÇÃO de peças simples** são decisões humanas do fluxo de
   produção: o app deixa PROCESSO em branco (combo na revisão) e DESCRIÇÃO
   em branco nas peças sem tabela de MP.

## 6. Premissas e restrições

- Os PDFs são gerados por CAD e possuem camada de texto (validado: 19/19 nos
  testes). Desenhos escaneados não são suportados na v1.
- O padrão de carimbo é o SGQ FOR ENG 004 REV 06; variações de template de
  outros clientes/épocas devem cair no log de revisão manual, nunca em dado errado.
- A planilha destino não pode estar aberta no Excel durante a exportação.

## 7. Critérios de aceite da v1

- Extração dos 19 PDFs de amostra com os valores exatos de `docs/07-plano-testes.md`
  (79 linhas, 0 erros).
- Exportação em planilha de teste preserva macros, pivôs e formatação (abrir no
  Excel e verificar aba TAB. DINAMICA e botões após gravação).
- Duplicidade: segunda exportação da mesma pasta insere 0 linhas.
- Backup gerado e íntegro (abre no Excel) a cada exportação.
