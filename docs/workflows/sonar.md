# SonarQube Workflow

Workflow reutilizável para executar build + análise SonarQube/SonarCloud em projetos Maven.

## Como reutilizar

```yaml
name: SonarQube

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  sonar:
    uses: nathanfiorito/reusable-githuib-workflows/.github/workflows/sonar.yml@main
    with:
      project_directory: backend
      sonar_project_key: my-org_backend
      java_version: '21'
      java_distribution: temurin
      maven_goals: verify
      sonar_organization: my-github-org         # opcional
      sonar_host_url: https://sonarcloud.io   # opcional
    secrets:
      SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
      SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }} # opcional
      SONAR_ORGANIZATION: ${{ secrets.SONAR_ORGANIZATION }} # opcional
```

- Prefira tags ou SHAs fixos no lugar de `@main` em ambientes produtivos.
- `project_directory` e `sonar_project_key` são obrigatórios; o workflow falha caso não sejam informados (via `with` ou variáveis do repositório).
- Defina `sonar_host_url` somente quando não estiver usando o SonarCloud padrão; é possível declarar via input ou secret.
- Para análises em organizações do SonarCloud informe `sonar_organization` (ou o secret equivalente); em instâncias self-hosted deixe vazio.

## Inputs

| Nome | Tipo | Default | Descrição |
| --- | --- | --- | --- |
| `project_directory` | string | — | Diretório base para o build/análise Maven. |
| `sonar_project_key` | string | — | Chave cadastrada no SonarQube/SonarCloud. |
| `java_version` | string | `21` | Versão do JDK usada durante o build. |
| `java_distribution` | string | `temurin` | Distribuição do JDK (temurin, zulu, etc.). |
| `maven_goals` | string | `verify` | Metas Maven executadas antes do scanner. |
| `sonar_host_url` | string | vazio | URL do servidor SonarQube; deixe vazio para SonarCloud. |
| `sonar_organization` | string | vazio | Organização SonarCloud; deixe vazio para instâncias self-hosted. |

## Secrets

| Nome | Obrigatório | Uso |
| --- | --- | --- |
| `SONAR_TOKEN` | Sim | Token com permissão de análise para o projeto Sonar. |
| `SONAR_HOST_URL` | Não | URL do servidor quando não quiser expor via input. |
| `SONAR_ORGANIZATION` | Não | Organização SonarCloud quando preferir fornecê-la como secret. |

## Dicas de customização

- Adicione etapas extras de build/teste antes da análise ajustando `maven_goals` (ex.: `clean verify`).
- Quando usar este repositório diretamente (gatilho `push`), configure `SONAR_PROJECT_DIRECTORY` e `SONAR_PROJECT_KEY` em *Repository Variables* para que o workflow encontre os valores obrigatórios.
