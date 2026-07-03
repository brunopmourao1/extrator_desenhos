# 05 — Interface do Usuário

## 1. Janela única (QMainWindow, 1280×760, redimensionável)

```
┌──────────────────────────────────────────────────────────────────────┐
│ Pasta raiz dos PDFs: [__________________________] [Procurar…] [Escanear] │
│ Planilha destino (.xlsm): [_______________________] [Procurar…]          │
│ ████████████████████░░░░░░░░  37/112 — 1808-00-041.pdf                   │
│ ┌──────────────────────────────────────────────────────────────────┐ │
│ │ ✔ │ DESENHO │ REV. │ QTDE │ PROCESSO ▾ │ DESCRIÇÃO │ DIMENSÃO │ … │ │
│ │ ☑ │ 1808-…  │ 00   │ 1    │ [combo]    │ METALON   │ 50 X 50… │   │ │
│ │ …                                                                  │ │
│ └──────────────────────────────────────────────────────────────────┘ │
│ ☑ Marcar/desmarcar todos            79 linha(s)  [Exportar para planilha] │
│ ┌ Log ───────────────────────────────────────────────────────────────┐ │
│ │ ⚠ digitalizado_antigo.pdf: Nº de desenho não encontrado…            │ │
│ └────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

## 2. Componentes e comportamento

| Componente | Especificação |
|-----------|---------------|
| Campo pasta raiz | `QLineEdit` editável (aceita colar caminho com aspas — strip `"`); botão abre `QFileDialog.getExistingDirectory` |
| Campo planilha | `QLineEdit` + `getOpenFileName` com filtro `*.xlsm` |
| Botão Escanear | desabilita durante varredura; valida pasta antes |
| Barra de progresso | `QProgressBar` com texto `atual/total — nome_do_arquivo` |
| Tabela de revisão | `QTableWidget`; colunas: ✔ (QCheckBox), DESENHO, REV., QTDE, PROCESSO (QComboBox **editável** com valores de `PROCESSOS`), DESCRIÇÃO, DIMENSÃO SOLICITADA, MATERIAL, QTD, ARQUIVO (somente leitura). Todas as demais células editáveis; seleção por linha; `resizeColumnsToContents` após popular |
| Marcar/desmarcar todos | `QCheckBox` no rodapé, aplica a todos os checkboxes |
| Botão Exportar | habilita só com linhas na tabela; `QMessageBox.question` de confirmação com contagem; desabilita durante exportação |
| Log | `QPlainTextEdit` somente leitura, ~140 px, recebe avisos por PDF, pulos por duplicidade, backup criado e resumo final |
| Diálogos finais | sucesso: inseridas/puladas/backup; erro de exportação: mencionar explicitamente "verifique se o arquivo não está aberto no Excel" |

## 3. Lista de processos (combo)

`"", CNC, USINAGEM, ESTRUTURA E CONJ. SOLDADO, CALDEIRARIA, CORTE ÁGUA,
IMPRESSÃO 3D, COMPRA` — editável: o usuário pode digitar valor fora da lista.

## 4. Regras de UX

- Nenhuma operação bloqueia a janela (threads + sinais).
- Erros nunca em silêncio: sempre log + diálogo quando fatal.
- A varredura substitui o conteúdo anterior da tabela (limpa antes).
- Fechamento da janela durante operação: aceitável na v1 não tratar
  (threads são daemon do processo); não corromper planilha é garantido pelo
  design do exportador (save único no final).

## 5. Fora do escopo visual da v1

Ícone customizado, temas, i18n, persistência dos últimos caminhos usados
(candidato natural para v1.1 via `QSettings`).
