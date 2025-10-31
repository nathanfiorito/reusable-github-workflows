#!/usr/bin/env bash

# Checks that a set of environment variables are defined and non-empty.
# Usage: check-required-env.sh VAR_NAME [VAR_NAME...]

set -euo pipefail

if [ "$#" -eq 0 ]; then
  echo "Usage: $0 <env-var> [env-var ...]" >&2
  exit 2
fi

missing=0
for var in "$@"; do
  value="${!var-}"
  if [ -z "${value}" ]; then
    echo "Required configuration '${var}' not provided. Set workflow input or repository variable." >&2
    missing=1
  fi
done

if [ "${missing}" -ne 0 ]; then
  exit 1
fi
