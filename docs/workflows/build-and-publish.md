# Build and Publish Workflow

Pipeline reutilizavel responsavel por compilar, testar e (opcionalmente) publicar uma imagem Docker.

Embora o nome sugira Docker Hub, este workflow publica a imagem no GitHub Container Registry (GHCR) por padrao. Quando voce preenche `docker_image` como `ghcr.io/<owner>/<repo>`, a imagem fica no namespace do GHCR associado ao repositorio atual. O acesso usa `github.actor` e `GITHUB_TOKEN`, entao nenhuma credencial extra e necessaria para esse caso. Ajuste `docker_registry` apenas se quiser publicar em outro registry (por exemplo, Docker Hub).

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

- Troque `@main` por uma tag ou SHA fixo em producao.
- Todas as chaves `project_directory`, `docker_context`, `dockerfile` e `docker_image` sao obrigatorias e o workflow falha se omitidas.
- Para Docker Hub, use `docker_registry: docker.io`, aponte `docker_image` para `docker.io/<org>/<repo>` e configure `REGISTRY_USERNAME` / `REGISTRY_PASSWORD` com credenciais validas.
- Para GHCR, mantenha `docker_registry: ghcr.io` e `docker_image` com prefixo `ghcr.io`. A imagem ficara disponivel em `ghcr.io/<owner>/<repo>:tag` dentro da sua organizacao ou conta no GitHub.

## Inputs

| Nome | Tipo | Default | Descricao |
| --- | --- | --- | --- |
| `project_directory` | string | - | Diretorio base para compilacao e testes. |
| `publish_image` | boolean | `true` | Publica a imagem Docker quando a branch e `main` ou `develop`. |
| `docker_context` | string | - | Caminho do contexto de build. |
| `dockerfile` | string | - | Dockerfile usado no build. |
| `docker_image` | string | - | Nome completo da imagem enviada (`ghcr.io/<owner>/<repo>:tag`). |
| `docker_registry` | string | `ghcr.io` | Registry utilizado no login; por padrao publica no GHCR e nao no Docker Hub. |

## Secrets

| Nome | Obrigatorio | Uso |
| --- | --- | --- |
| `REGISTRY_USERNAME` | Nao | Forca usuario especifico para o login (necessario para Docker Hub). |
| `REGISTRY_PASSWORD` | Nao | Senha ou token do registry (necessario para Docker Hub). |

Se os secrets nao forem informados, o workflow usa `github.actor` + `${{ secrets.GITHUB_TOKEN }}`, comportamento adequado para GHCR.

## Dicas de customizacao

- Ajuste o Java ou ferramentas de build adicionando etapas extras no job `build-test`.
- Defina variaveis de repositorio (`PROJECT_DIRECTORY`, `DOCKER_CONTEXT`, `DOCKERFILE`, `DOCKER_IMAGE`) quando o workflow for executado via gatilho `push` neste repositorio.
- Combine com o workflow de PR Automation para abrir PRs automaticamente apos as execucoes de feature/hotfix.
