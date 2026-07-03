# 06 — Plano de Implementação

Fases pensadas para execução com Claude Code, cada uma terminando em estado
testável. O código de `referencia/` é a base validada — a Fase 1 consiste em
promovê-lo, não reescrevê-lo. Marcar os checkboxes conforme concluído.

## Fase 0 — Preparação do ambiente

- [ ] Criar venv Python 3.11+ e instalar `requirements.txt` + `pytest`
- [ ] Copiar PDFs de teste reais para `amostras/` (mínimo: os 19 da OS 1808
      listados em docs/07) e uma CÓPIA da planilha modelo para `amostras/`
- [ ] `git init` + primeiro commit da documentação

## Fase 1 — Motor de extração + testes de regressão

- [ ] Promover `referencia/extrator.py` para a raiz do projeto
- [ ] Escrever `tests/test_extrator.py` com TODOS os valores esperados de
      docs/07-plano-testes.md (carimbo, contagem de linhas, amostras de MP)
- [ ] `pytest` verde: 19 PDFs → 79 linhas, 0 erros, valores exatos
- [ ] Commit: "motor de extração validado com regressão"

**Critério de saída:** qualquer alteração futura no extrator que quebre um
valor esperado falha no pytest.

## Fase 2 — Exportador

- [ ] Promover `referencia/exportador.py`
- [ ] Teste manual guiado (Excel necessário): exportar 3 linhas fictícias numa
      cópia da planilha modelo; conferir backup, posição (linha 6+), colunas
      certas e preservação de macros/pivôs (checklist de docs/04 §6)
- [ ] Testar duplicidade: segunda exportação → 0 inseridas
- [ ] Testar erro com arquivo aberto no Excel → mensagem clara, original intacto
- [ ] Commit: "exportador com backup e antiduplicidade"

## Fase 3 — Interface

- [ ] Promover `referencia/main.py`
- [ ] Testar fluxo completo com `amostras/`: escanear → editar células →
      trocar PROCESSO no combo → desmarcar linhas → exportar
- [ ] Verificar responsividade (UI viva durante varredura de pasta grande)
- [ ] Verificar log de PDF problemático (incluir um PDF qualquer não-desenho
      em `amostras/` para provocar o aviso)
- [ ] Commit: "GUI completa"

## Fase 4 — Empacotamento e piloto

- [ ] `build.bat` → `dist/ExtratorDesenhosLS.exe`
- [ ] Testar o exe em máquina limpa (sem Python) com Excel instalado
- [ ] Rodar na pasta real `TESTE PDF'S` com cópia da planilha oficial
- [ ] Coletar PDFs que caíram em "revisar manualmente" e avaliar ajustes de
      âncoras/prefixos (abrir issues, não corrigir na pressa)
- [ ] Commit + tag `v1.0`

## Fase 5 — Melhorias candidatas (backlog, só após piloto)

- [ ] `QSettings` para lembrar últimos caminhos usados
- [ ] Exportar também um `.csv` de conferência junto do backup
- [ ] Coluna de status visual na tabela (ok / precisa de atenção)
- [ ] Detecção de PDFs escaneados com sugestão explícita de OCR (v2)
- [ ] Configuração externa (JSON) para `PREFIXOS_MP` e `PROCESSOS`

## Diretrizes de execução para o Claude Code

- Uma fase por sessão; `/clear` entre fases.
- Sempre rodar `pytest` antes de considerar uma tarefa concluída.
- Mudanças mínimas: não refatorar além do escopo da fase.
- Em dúvida entre duas abordagens, apresentar as duas e aguardar decisão.
- Nunca commitar PDFs de desenhos de clientes em repositório que possa se
  tornar público.
