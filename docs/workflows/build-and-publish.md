# Build and Publish Workflow

Pipeline reutilizável responsável por compilar, testar e (opcionalmente) publicar uma imagem Docker.

## Como reutilizar

```yaml
name: Build and Publish

on:
  push:
    branches:
      - main

jobs:
  ci:
    uses: nathanfiorito/reusable-githuib-workflows/.github/workflows/build-and-publish.yml@main
    with:
      project_directory: backend
      docker_context: backend
      dockerfile: backend/Dockerfile
      docker_image: ghcr.io/<owner>/<repo>
      publish_image: true
      docker_registry: ghcr.io
    secrets:
      REGISTRY_USERNAME: ${{ secrets.REGISTRY_USERNAME }}
      REGISTRY_PASSWORD: ${{ secrets.REGISTRY_PASSWORD }}
```

- Troque `@main` por uma tag ou SHA fixo em produção.
- Todas as chaves `project_directory`, `docker_context`, `dockerfile` e `docker_image` são obrigatórias e o workflow falha se omitidas.
- Para Docker Hub, use `docker_registry: docker.io`, aponte `docker_image` para `docker.io/<org>/<repo>` e configure `REGISTRY_USERNAME` / `REGISTRY_PASSWORD` com credenciais válidas.

## Inputs

| Nome | Tipo | Default | Descrição |
| --- | --- | --- | --- |
| `project_directory` | string | — | Diretório base para compilação e testes. |
| `publish_image` | boolean | `true` | Publica imagem Docker quando branch é `main` ou `develop`. |
| `docker_context` | string | — | Caminho do contexto de build. |
| `dockerfile` | string | — | Dockerfile usado no build. |
| `docker_image` | string | — | Nome completo da imagem enviada. |
| `docker_registry` | string | `ghcr.io` | Registry utilizado no login (`docker.io` para Docker Hub). |

## Secrets

| Nome | Obrigatório | Uso |
| --- | --- | --- |
| `REGISTRY_USERNAME` | Não | Força usuário específico para o login (necessário para Docker Hub). |
| `REGISTRY_PASSWORD` | Não | Senha/token do registry (necessário para Docker Hub). |

Se os secrets não forem informados, o workflow usa `github.actor` + `${{ secrets.GITHUB_TOKEN }}`, comportamento adequado para GHCR.

## Dicas de customização

- Ajuste o Java ou ferramentas de build adicionando etapas extras no job `build-test`.
- Defina variáveis de repositório (`PROJECT_DIRECTORY`, `DOCKER_CONTEXT`, `DOCKERFILE`, `DOCKER_IMAGE`) quando o workflow for executado via gatilho `push` neste repositório.
- Combine com o workflow de PR Automation para abrir PRs automaticamente após as execuções de feature/hotfix.
