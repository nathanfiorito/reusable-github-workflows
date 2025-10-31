# CI/CD Pipeline Workflow

Workflow reutilizável que padroniza build, testes e publicação de imagem Docker, além de automatizar pull requests de feature e hotfix.

## Como reutilizar

No repositório consumidor crie um workflow (por exemplo `.github/workflows/pipeline.yml`) chamando este pipeline:

```yaml
name: Pipeline compartilhada

on:
  push:
    branches:
      - main

jobs:
  ci_cd:
    uses: nathanfiorito/reusable-githuib-workflows/.github/workflows/ci-cd.yml@main
    with:
      project_directory: kanban-core
      publish_image: true
      docker_context: kanban-core
      dockerfile: kanban-core/Dockerfile
      docker_image: ghcr.io/<owner>/<repo>
      feature_prefix: feature/
      feature_target: develop
      feature_title_prefix: Feature
      enable_auto_pr_feature: true
      hotfix_prefix: hotfix/
      hotfix_target: main
      hotfix_title_prefix: Hotfix
      enable_auto_pr_hotfix: true
      auto_pr_script: scripts/create-pr.sh
    secrets:
      PR_AUTOMATION_TOKEN: ${{ secrets.PR_AUTOMATION_TOKEN }}
```

- Substitua `@main` por uma tag ou SHA na produção.
- Ajuste apenas os parâmetros necessários; os demais usam valores padrão.
- Configure `PR_AUTOMATION_TOKEN` somente se desejar abrir PRs automaticamente.

## Inputs

| Nome | Tipo | Default | Descrição |
| --- | --- | --- | --- |
| `project_directory` | string | `kanban-core` | Diretório base para compilação e testes. |
| `publish_image` | boolean | `true` | Publica imagem Docker quando branch é `main` ou `develop`. |
| `docker_context` | string | `kanban-core` | Caminho do contexto de build. |
| `dockerfile` | string | `kanban-core/Dockerfile` | Dockerfile usado no build. |
| `docker_image` | string | `ghcr.io/${{ github.repository }}` | Nome base da imagem enviada ao GHCR. |
| `auto_pr_script` | string | `scripts/create-pr.sh` | Script que abre PRs automatizados. |
| `feature_prefix` | string | `feature/` | Prefixo das branches que geram PR para `feature_target`. |
| `feature_target` | string | `develop` | Branch alvo das PRs de feature. |
| `feature_title_prefix` | string | `Feature` | Prefixo do título das PRs de feature. |
| `enable_auto_pr_feature` | boolean | `true` | Desliga a automação de PR de feature quando falso. |
| `hotfix_prefix` | string | `hotfix/` | Prefixo das branches que geram PR para `hotfix_target`. |
| `hotfix_target` | string | `main` | Branch alvo das PRs de hotfix. |
| `hotfix_title_prefix` | string | `Hotfix` | Prefixo do título das PRs de hotfix. |
| `enable_auto_pr_hotfix` | boolean | `true` | Desliga a automação de PR de hotfix quando falso. |

## Secrets

| Nome | Obrigatório | Uso |
| --- | --- | --- |
| `PR_AUTOMATION_TOKEN` | Não | Token alternativo para a automação de PR quando `GITHUB_TOKEN` não tem permissões suficientes. |

## Dicas de customização

- Defina `publish_image: false` quando não houver Dockerfile ou necessidade de publicar imagens.
- Configure `auto_pr_script` apenas se o repositório consumidor possuir o script referenciado; caso contrário defina `enable_auto_pr_feature` e `enable_auto_pr_hotfix` como `false`.
- Para desabilitar qualquer automação de PR basta setar o input correspondente para `false`.
