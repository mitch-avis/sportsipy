#!/usr/bin/env bash
set -euo pipefail

# Runs from the repo root regardless of where it's invoked from.
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

if ! command -v uv >/dev/null 2>&1; then
  echo "Error: 'uv' is not installed or not on PATH." >&2
  echo "Install it from https://astral.sh/uv (or: curl -LsSf https://astral.sh/uv/install.sh | sh)" >&2
  exit 1
fi

# If supported, keep uv itself up to date (no-op on older uv builds).
uv self update >/dev/null 2>&1 || true

echo "==> Compiling requirements.txt (upgrade all)"
uv pip compile \
  --upgrade \
  requirements.in \
  --output-file requirements.txt \
  --strip-extras

echo "==> Installing requirements.txt"
uv pip install -U -r requirements.txt

echo "==> Compiling requirements-dev.txt (upgrade all)"
uv pip compile \
  --upgrade \
  requirements-dev.in \
  --output-file requirements-dev.txt \
  --strip-extras

echo "==> Installing requirements-dev.txt"
uv pip install -U -r requirements-dev.txt

echo "Done."
