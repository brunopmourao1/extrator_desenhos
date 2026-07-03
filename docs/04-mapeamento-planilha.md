# 04 — Mapeamento da Planilha e Exportação

## 1. Arquivo destino

- Formato: `.xlsm` (Excel com macros) — template `FOR ENG 003 ACOMPANHAMENTO
  MONTAGEM MECÂNICA`.
- Contém múltiplas abas (`TAB. DINAMICA`, `OS ACOMPANHAMENTO`, `OBSOLETO`,
  `PERIFÉRICOS`, `FIXAÇÕES`, `TABELA DINAMICA`, `RESUMO`, `HORAS`...),
  macros VBA, tabelas dinâmicas e formatação condicional.
- **Somente** a aba `OS ACOMPANHAMENTO` é gravada; todas as demais e todos os
  recursos do arquivo devem permanecer intactos.

## 2. Estrutura da aba OS ACOMPANHAMENTO

- Linhas 1–3: cabeçalho da OS (`OS:`, `CLIENTE:`, datas).
- Linha 4: grupos de colunas (CÓPIA CONTROLADA, MATÉRIA PRIMA ENGENHARIA,
  MATÉRIA PRIMA COMPRAS, ALMOXARIFADO, PRÉ USINAGEM, USINAGEM, TRATAMENTO
  TÉRMICO, TRATAMENTO SUPERFÍCIE).
- Linha 5: cabeçalhos de coluna.
- **Linha 6 em diante: dados** (`LINHA_INICIAL = 6`).

## 3. Mapeamento de colunas (contrato de escrita)

| Coluna | Cabeçalho (linha 5) | Origem no app | Observação |
|--------|--------------------|---------------|------------|
| A | DESENHO | `desenho` | repete em TODAS as linhas do desdobramento |
| B | REV. | `rev` | só na 1ª linha de cada desenho |
| C | QTDE | `qtde` | só na 1ª linha; qtde de conjuntos/peças do desenho |
| D | PROCESSO | `processo` | escolhido pelo usuário na revisão |
| E | ENVIO | — | **não gravar** |
| F | RECEBIMENTO | — | **não gravar** |
| G | DESCRIÇÃO | `descricao` | tipo de MP (METALON, CHAPA...) ou vazio |
| H | DIMENSÃO SOLICITADA | `dimensao` | seção X comprimento, ou dimensão do carimbo |
| I | MATERIAL | `material` | do carimbo (com fallback multi-folha) |
| J | QTD | `qtd` | quantidade da matéria-prima |
| K em diante | REV., FORNECEDOR, PC, datas, STATUS... | — | **não gravar jamais** |

Valores vazios (`""`/`None`) não são escritos — a célula fica intocada
(preserva `-` ou fórmulas pré-existentes do template).

## 4. Regras de exportação (exportador.py)

1. **Backup obrigatório** antes de abrir o arquivo:
   `shutil.copy2` → `{stem}_BACKUP_{AAAAMMDD_HHMMSS}.xlsm` na mesma pasta.
2. Abrir via `xlwings.App(visible=False, add_book=False)`;
   `finally: app.quit()` sempre (sem processo Excel órfão).
3. **Linha de inserção:** `ws.range(f"A{last_cell.row}").end("up").row + 1`,
   nunca menor que 6.
4. **Duplicidade:** ler coluna A de 6 até a última linha; montar set de
   desenhos existentes; pular toda linha cujo `desenho` esteja no set,
   logando uma vez por desenho pulado. Como o set de existentes é lido
   **antes** da gravação, todas as linhas de um desenho novo (que repetem o
   mesmo nº na coluna A) passam juntas; numa reexportação, todas são puladas.
5. Gravar célula a célula apenas nas colunas do mapeamento; `wb.save()` uma
   única vez ao final; retorno `{"inseridas", "puladas", "backup"}`.

## 5. Condições de erro

| Situação | Comportamento |
|----------|--------------|
| Planilha inexistente | `FileNotFoundError` antes de qualquer ação |
| Aba `OS ACOMPANHAMENTO` ausente | `RuntimeError` claro; original intacto |
| Arquivo aberto no Excel / bloqueado | exceção do COM propagada à UI com orientação "feche o arquivo no Excel" |
| Falha no meio da gravação | original só é alterado no `save()`; backup sempre disponível |

## 6. Verificação pós-exportação (manual, critério de aceite)

Abrir o `.xlsm` no Excel e conferir: macros funcionam (botões), aba
`TAB. DINAMICA` atualiza, formatação condicional das colunas STATUS segue
ativa, e as linhas novas aparecem corretamente a partir da primeira vazia.
