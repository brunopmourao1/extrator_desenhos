# Extrator de Desenhos — LS Control

Aplicativo desktop Windows que varre uma pasta raiz com PDFs de desenhos mecânicos
(padrão SGQ FOR ENG 004 REV 06), extrai dados do carimbo e da tabela de matéria-prima,
permite revisão em tela e insere as linhas na aba "OS ACOMPANHAMENTO" de uma
planilha `.xlsm` existente.

## Stack

- Python 3.11+ · PySide6 (GUI) · pdfplumber (extração) · xlwings (escrita no Excel via COM)
- Empacotamento: PyInstaller `--onefile --windowed` (ver `build.bat`)
- Idioma do código, comentários, UI e mensagens: **português brasileiro**

## Comandos

- Rodar app: `python main.py`
- Testes: `pytest tests/ -v` (usam os PDFs de `amostras/`)
- Build do exe: `build.bat` → `dist/ExtratorDesenhosLS.exe`

## Estrutura

```
main.py          # GUI (PySide6) — janela única, threads de varredura/exportação
extrator.py      # motor de extração de PDFs (puro, sem dependência de GUI)
exportador.py    # escrita na planilha .xlsm via xlwings
tests/           # pytest com resultados esperados reais (docs/07)
amostras/        # PDFs reais de teste (não commitar desenhos de clientes em repo público)
referencia/      # implementação validada — usar como base, não reescrever do zero
docs/            # especificação completa (fonte da verdade)
```

## Documentação (fonte da verdade — ler antes de implementar)

- @docs/01-requisitos.md — escopo, requisitos funcionais/não funcionais, decisões de negócio
- @docs/02-arquitetura.md — módulos, fluxo de dados, threading, empacotamento
- @docs/03-especificacao-extracao.md — algoritmos de extração VALIDADOS (âncoras, regex, casos)
- @docs/04-mapeamento-planilha.md — colunas da OS ACOMPANHAMENTO, backup, duplicidade
- @docs/05-interface-usuario.md — layout, componentes e comportamento da GUI
- @docs/06-plano-implementacao.md — fases de trabalho com checklist
- @docs/07-plano-testes.md — casos de teste com valores esperados dos PDFs reais

## Regras do projeto

- O código em `referencia/` foi validado com 100% de acerto em 19 PDFs reais
  (79 linhas extraídas, 0 erros). Evoluir a partir dele; não reescrever a lógica
  de extração sem rodar os testes de regressão de `docs/07-plano-testes.md`.
- `extrator.py` NUNCA importa PySide6/xlwings — deve rodar puro (testável via pytest).
- Toda extração usa âncoras posicionais (coordenadas de palavras), nunca a ordem
  do texto do PDF — CAD embaralha a ordem (detalhes em @docs/03).
- Exportação SEMPRE cria backup do `.xlsm` antes de gravar e pula desenhos
  já existentes na coluna A (detalhes em @docs/04).
- Nunca gravar nas colunas de acompanhamento (fornecedores/datas/status) —
  somente A, B, C, D, G, H, I, J.
- Falha em um PDF não pode interromper a varredura: registrar no log e continuar.
- Rodar `pytest` após qualquer mudança em `extrator.py`.
- Mudanças mínimas e focadas; não refatorar código não relacionado à tarefa.
