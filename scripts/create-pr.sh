#!/usr/bin/env bash

# Automates creation of pull requests targeting a base branch while keeping the
# source branch untouched. Expects the GitHub Actions environment variables to
# be available (`GITHUB_REPOSITORY`, `GITHUB_REF_NAME`, etc.).

set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <base-branch> <title-prefix>" >&2
  exit 2
fi

BASE_BRANCH="$1"
TITLE_PREFIX="$2"

# Prefer the default GitHub token, fallback to a custom automation token when provided.
TOKEN="${DEFAULT_TOKEN:-${GITHUB_TOKEN:-}}"
if [ -z "${TOKEN}" ]; then
  TOKEN="${FALLBACK_TOKEN:-}"
fi

if [ -z "${TOKEN}" ]; then
  echo "Nenhum token disponível para criar pull request." >&2
  exit 1
fi

OWNER="${GITHUB_REPOSITORY%/*}"
REPO="${GITHUB_REPOSITORY#*/}"
HEAD_BRANCH="${GITHUB_REF_NAME}"
API_ROOT="https://api.github.com/repos/${OWNER}/${REPO}"

encoded_head=$(printf '%s' "${OWNER}:${HEAD_BRANCH}" | jq -sRr @uri)
encoded_base=$(printf '%s' "${BASE_BRANCH}" | jq -sRr @uri)

echo "Verificando PR existente para ${HEAD_BRANCH} -> ${BASE_BRANCH}..."
existing=$(curl -sS \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  "${API_ROOT}/pulls?state=open&head=${encoded_head}&base=${encoded_base}")

existing_url=$(echo "${existing}" | jq -r '.[0].html_url // empty')
if [ -n "${existing_url}" ]; then
  echo "Pull request já existe: ${existing_url}"
  exit 0
fi

body_template=$'## 🤖 PR Automático\n\n- Branch de origem: `__HEAD__`\n- Branch de destino: `__BASE__`\n\nBuild e testes executados com sucesso via pipeline CI/CD.\n'
BODY="${body_template/__HEAD__/${HEAD_BRANCH}}"
BODY="${BODY/__BASE__/${BASE_BRANCH}}"

payload=$(jq -nc \
  --arg title "[Automated] ${TITLE_PREFIX} ${HEAD_BRANCH} -> ${BASE_BRANCH}" \
  --arg head "${HEAD_BRANCH}" \
  --arg base "${BASE_BRANCH}" \
  --arg body "${BODY}" \
  '{title:$title, head:$head, base:$base, body:$body, maintainer_can_modify:true, draft:false}')

echo "Criando pull request..."
response_file=$(mktemp)
trap 'rm -f "${response_file}"' EXIT

status=$(curl -sS -o "${response_file}" -w '%{http_code}' \
  -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  "${API_ROOT}/pulls" \
  -d "${payload}")

if [ "${status}" -ge 200 ] && [ "${status}" -lt 300 ]; then
  pr_url=$(jq -r '.html_url' < "${response_file}")
  echo "Pull request criado: ${pr_url}"
  rm -f "${response_file}"
  trap - EXIT
  exit 0
elif [ "${status}" -eq 422 ]; then
  echo "Pull request não criado (possivelmente já existe). Resposta:"
  cat "${response_file}"
  rm -f "${response_file}"
  trap - EXIT
  exit 0
else
  echo "Falha ao criar pull request (status ${status}):"
  cat "${response_file}"
  rm -f "${response_file}"
  trap - EXIT
  exit 1
fi
