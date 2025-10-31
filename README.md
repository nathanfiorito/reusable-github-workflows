# reusable-githuib-workflows
Repositório com workflows reutilizáveis do GitHub Actions, prontos para automatizar pipelines de build, testes, releases e deploys em múltiplos projetos. Facilita padronização, reuso e manutenção contínua em todo o ecossistema.

## Como usar
- Importe o workflow `ci-cd.yml` em outros repositórios com `uses: nathanfiorito/reusable-githuib-workflows/.github/workflows/ci-cd.yml@<ref>`.
- Ajuste apenas os inputs necessários (diretório do projeto, Dockerfile, automações de PR); os demais têm defaults seguros.
- Consulte o guia detalhado em [docs/workflows/ci-cd.md](docs/workflows/ci-cd.md) para exemplos, lista completa de parâmetros e requisitos adicionais.
