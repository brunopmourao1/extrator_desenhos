# Extrator de Desenhos — LS Control

Aplicativo desktop (Windows) que automatiza a alimentação da planilha de
acompanhamento de montagem mecânica (`FOR ENG 003`, `.xlsm`) a partir dos PDFs
de desenhos mecânicos das OSs (padrão de folha SGQ FOR ENG 004 REV 06).

Fluxo: **selecionar pasta raiz → escanear → revisar/editar em tela → exportar**
para a aba `OS ACOMPANHAMENTO` da planilha existente, com backup automático e
proteção contra duplicidade.

## Status

v1.0: motor de extração, exportador e GUI promovidos e validados (19 PDFs
reais → 79 linhas, 0 erros; backup/antiduplicidade/preservação de macros e
pivôs testados com Excel real; build via PyInstaller gerando
`dist/ExtratorDesenhosLS.exe` com sucesso). Falta piloto em máquina limpa
e na pasta real de produção (docs/06 Fase 4).

## Começando (desenvolvimento)

```bash
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt pytest
# copiar os PDFs de teste para amostras/ (ver docs/07 §2)
pytest tests/ -v
python main.py
```

Build do executável para distribuição interna: `build.bat`
→ `dist/ExtratorDesenhosLS.exe` (requer apenas Excel na máquina de destino).

## Documentação

| Doc | Conteúdo |
|-----|----------|
| [CLAUDE.md](CLAUDE.md) | Instruções de sessão para o Claude Code |
| [docs/01-requisitos.md](docs/01-requisitos.md) | Escopo, RF/RNF, decisões de negócio, critérios de aceite |
| [docs/02-arquitetura.md](docs/02-arquitetura.md) | Módulos, fluxo de dados, threading, dependências |
| [docs/03-especificacao-extracao.md](docs/03-especificacao-extracao.md) | Algoritmos de extração validados (leitura obrigatória) |
| [docs/04-mapeamento-planilha.md](docs/04-mapeamento-planilha.md) | Contrato de escrita na OS ACOMPANHAMENTO |
| [docs/05-interface-usuario.md](docs/05-interface-usuario.md) | Especificação da GUI |
| [docs/06-plano-implementacao.md](docs/06-plano-implementacao.md) | Fases de trabalho com checklist |
| [docs/07-plano-testes.md](docs/07-plano-testes.md) | Gabarito de regressão com valores reais |

## Decisões de projeto (resumo)

- Extração 100% posicional (coordenadas de palavras) — texto de PDF de CAD tem
  ordem embaralhada.
- Cortes de matéria-prima listados **como no desenho** (sem consolidação em barras).
- Escrita no `.xlsm` via **xlwings/COM** para preservar macros, tabelas dinâmicas
  e formatação (openpyxl degrada o template).
- Backup obrigatório antes de qualquer gravação; desenhos duplicados são pulados.

## Licença / confidencialidade

Uso interno LS Control. Desenhos de clientes (`amostras/`) não devem ser
publicados.
