# 08 — Progresso do Projeto

Documento vivo: atualizar a cada sessão de trabalho com o que foi concluído e o
que falta. Não é fonte de verdade de requisitos (isso é `docs/01` a `docs/07`) —
é o rastreador de "onde paramos".

## Status atual (03/07/2026)

Fases 0 a 3 do `docs/06-plano-implementacao.md` concluídas. Fase 4
(Empacotamento e piloto) em andamento: build gerado e validado localmente,
faltam os testes de campo antes da tag `v1.0`.

## Histórico de commits

| Commit | O que entregou |
|--------|-----------------|
| `bc3bba3` | Documentação completa e implementação de referência validada |
| `cc1409d` | Motor de extração (`extrator.py`) promovido para a raiz, com testes de regressão (19 PDFs → 79 linhas, 0 erros) |
| `4721f65` | `exportador.py` promovido; corrigida falha silenciosa quando a planilha está aberta no Excel |
| `fdf9250` | `main.py` (GUI) promovido; fluxo completo validado com PDFs reais |
| `91868f2` | Build do executável validado via PyInstaller (`dist/ExtratorDesenhosLS.exe`, ~75 MB) |

## Concluído

- [x] Motor de extração com 100% de acerto nos 19 PDFs de `amostras/` (pytest verde)
- [x] Exportador com backup automático, antiduplicidade e tratamento de erro de arquivo aberto
- [x] GUI funcional (PySide6) com fluxo escanear → revisar → exportar
- [x] Build `--onefile --windowed` gerado com sucesso (`build.bat`)

## Pendências da Fase 4 (antes da tag v1.0)

- [ ] Testar o `.exe` em máquina limpa (sem Python instalado), só com Excel
- [ ] Rodar o app na pasta real "TESTE PDF'S" com uma **cópia** da planilha oficial
      (nunca contra o arquivo de produção)
- [ ] Coletar os PDFs que caírem em "revisar manualmente" durante o teste real
      e avaliar se precisam de ajuste de âncoras/prefixos em `extrator.py`
      (abrir como itens de backlog, não corrigir às pressas)
- [ ] Depois dos testes acima: commit final + tag `v1.0`

## Backlog (Fase 5 — só depois do piloto, ver docs/06 §Fase 5)

- [ ] `QSettings` para lembrar os últimos caminhos usados
- [ ] Exportar `.csv` de conferência junto do backup
- [ ] Coluna de status visual na tabela (ok / precisa atenção)
- [ ] Detecção de PDF escaneado com sugestão de OCR (v2)
- [ ] Externalizar `PREFIXOS_MP` e `PROCESSOS` em config JSON

## Próxima sessão — por onde retomar

1. Conferir se `dist/ExtratorDesenhosLS.exe` ainda está atualizado (rebuildar
   com `build.bat` se `main.py`/`extrator.py`/`exportador.py` mudaram).
2. Executar o roteiro de teste manual de campo (pasta real + cópia da planilha).
3. Registrar nesta tabela os PDFs problemáticos encontrados, com o motivo.
4. Só então commitar e criar a tag `v1.0`.
