# Pull Request Automation Workflow

Workflow reutilizável que garante a criação de PRs padronizados para branches de feature e hotfix.

## Como reutilizar

```yaml
name: PR Automation

on:
  push:
    branches:
      - 'feature/**'
      - 'hotfix/**'

jobs:
  auto_pr:
    uses: nathanfiorito/reusable-githuib-workflows/.github/workflows/pr-automation.yml@main
    with:
      feature_prefix: feature/
      feature_target: develop
      feature_title_prefix: Feature
      enable_auto_pr_feature: true
      hotfix_prefix: hotfix/
      hotfix_target: main
      hotfix_title_prefix: Hotfix
      enable_auto_pr_hotfix: true
    secrets:
      PR_AUTOMATION_TOKEN: ${{ secrets.PR_AUTOMATION_TOKEN }}
```

- Use `@main` apenas em desenvolvimento; prefira tags ou SHAs estáveis em produção.
- `PR_AUTOMATION_TOKEN` só é necessário quando o `GITHUB_TOKEN` não possui permissão para abrir PRs no repositório de destino.
- Ajuste os inputs de prefixo/target/título para refletir a convenção de branches do repositório consumidor.
- Garanta que o repositório consumidor inclua o script `scripts/create-pr.sh` ou adapte a localização antes de reutilizar o workflow (por exemplo, sincronizando esse diretório via submódulo).

## Inputs

| Nome | Tipo | Default | Descrição |
| --- | --- | --- | --- |
| `feature_prefix` | string | `feature/` | Prefixo das branches que geram PRs para `feature_target`. |
| `feature_target` | string | `develop` | Branch alvo dos PRs de feature. |
| `feature_title_prefix` | string | `Feature` | Prefixo do título dos PRs de feature. |
| `enable_auto_pr_feature` | boolean | `true` | Desliga a automação de PR de feature quando falso. |
| `hotfix_prefix` | string | `hotfix/` | Prefixo das branches que geram PRs para `hotfix_target`. |
| `hotfix_target` | string | `main` | Branch alvo dos PRs de hotfix. |
| `hotfix_title_prefix` | string | `Hotfix` | Prefixo do título dos PRs de hotfix. |
| `enable_auto_pr_hotfix` | boolean | `true` | Desliga a automação de PR de hotfix quando falso. |

## Secrets

| Nome | Obrigatório | Uso |
| --- | --- | --- |
| `PR_AUTOMATION_TOKEN` | Não | Token alternativo usado quando `GITHUB_TOKEN` não consegue criar PRs. |

## Dicas de customização

- Combine com o workflow de build para garantir que apenas branches aprovadas abram PRs automaticamente.
- Se o repositório consumidor não possuir o script `scripts/create-pr.sh`, importe-o ou forneça o caminho via `auto_pr_script`.
