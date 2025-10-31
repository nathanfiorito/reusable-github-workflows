# OpenAI Code Review Workflow

Workflow reutilizável que roda uma análise automática de Pull Requests utilizando o script Python integrado (`scripts/python/ai-code-review.py`) e a API da OpenAI. Ele comenta o resumo diretamente no PR e publica artefatos (`review-summary.md`, `review-details.json`) com o conteúdo completo da revisão.

## Como reutilizar

```yaml
name: AI Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  ai-review:
    uses: nathanfiorito/reusable-githuib-workflows/.github/workflows/openai-code-review.yml@main
    with:
      pr_number: ${{ github.event.pull_request.number }}
      # repo_name: my-org/outro-repo # opcional quando a revisão ocorre em outro repositório
    secrets:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

- Substitua `@main` por uma tag ou SHA fixo em produção.
- `pr_number` é obrigatório na reutilização via `workflow_call` (o workflow resolve sozinho quando disparado diretamente por `pull_request`).
- Informe `repo_name` apenas se o PR pertencer a outro repositório (formato `owner/nome`).
- O `GITHUB_TOKEN` pode ser herdado com `secrets: inherit`, desde que o repositório/chamada possua permissão para comentar no PR.

## Inputs

| Nome | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `pr_number` | string | Sim | Número do Pull Request que receberá a revisão automática. |
| `repo_name` | string | Não | Repositório (owner/nome) alvo. Default: mesmo repositório do workflow. |

## Secrets

| Nome | Obrigatório | Uso |
| --- | --- | --- |
| `OPENAI_API_KEY` | Sim | Chave da OpenAI com acesso ao modelo escolhido. |
| `GITHUB_TOKEN` | Sim | Utilizado para ler arquivos do PR e publicar comentários. Pode ser herdado (`secrets: inherit`). |

## Variáveis de ambiente opcionais

| Nome | Default | Descrição |
| --- | --- | --- |
| `OPENAI_MODEL` | `gpt-4o-mini` | Modelo a ser utilizado na revisão. |
| `OPENAI_MAX_TOKENS` | `2000` | Limite de tokens na resposta. |
| `OPENAI_TEMPERATURE` | `0.3` | Temperatura da geração (criatividade). |
| `AI_REVIEW_MAX_FILE_SIZE` | `10000` | Tamanho máximo (caracteres) do trecho diff analisado. |
| `AI_REVIEW_MAX_FILES` | `20` | Número máximo de arquivos considerados na revisão. |

Defina-as via `env` no job que consome o workflow, quando quiser ajustar o comportamento do reviewer.

## Resultado da execução

- Comentário resumido postado no PR com achados principais.
- Arquivo `review-summary.md` com o mesmo texto do comentário.
- Arquivo `review-details.json` contendo metadados da execução (PR, modelo, lista de arquivos). Ambos são publicados como artefatos (`code-review-results`).

## Observações

- O script ignora arquivos removidos e só analisa extensões suportadas (`.java`, `.yaml`, `.xml`, `.sql`, `.properties`, `.json`, `.sh`, `.py`, etc.). Ajuste diretamente no script se precisar ampliar a cobertura.
- Certifique-se de que o token utilizado tenha permissão de leitura no repositório e de comentar no PR (escopos `contents:read`, `pull-requests:write`).
- O workflow baixa a mesma versão deste repositório que foi referenciada na chamada (`uses: ...@ref`), garantindo que o script Python está alinhado com a versão do workflow utilizada.
