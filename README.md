# reusable-githuib-workflows
Repositório com workflows reutilizáveis do GitHub Actions, prontos para automatizar pipelines de build, testes, releases e deploys em múltiplos projetos. Facilita padronização, reuso e manutenção contínua em todo o ecossistema.

## Como usar
- Consuma `build-and-publish.yml` com `uses: nathanfiorito/reusable-githuib-workflows/.github/workflows/build-and-publish.yml@<ref>` para compilar/testar e publicar imagens.
- Consuma `pr-automation.yml` com `uses: nathanfiorito/reusable-githuib-workflows/.github/workflows/pr-automation.yml@<ref>` para automatizar abertura de PRs.
- Consuma `sonar.yml` com `uses: nathanfiorito/reusable-githuib-workflows/.github/workflows/sonar.yml@<ref>` para rodar build + análise SonarQube/SonarCloud.
- Consuma `openai-code-review.yml` com `uses: nathanfiorito/reusable-githuib-workflows/.github/workflows/openai-code-review.yml@<ref>` para gerar revisões automáticas de PR via OpenAI.
- Consulte os guias em [docs/workflows/build-and-publish.md](docs/workflows/build-and-publish.md), [docs/workflows/pr-automation.md](docs/workflows/pr-automation.md), [docs/workflows/sonar.md](docs/workflows/sonar.md) e [docs/workflows/openai-code-review.md](docs/workflows/openai-code-review.md) para inputs, secrets e exemplos detalhados.
