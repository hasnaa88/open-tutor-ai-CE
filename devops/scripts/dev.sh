#!/usr/bin/env bash
# Local development startup script for Open TutorAI backend.
# Loads .env from the project root and starts uvicorn with hot-reload.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -f ".env" ]; then
  echo "No .env found — copying .env.example"
  cp .env.example .env
fi

# Export .env vars into the current shell so uvicorn inherits them.
# python-dotenv also does this at runtime, but exporting here ensures
# any shell-level tooling (e.g. alembic) sees them too.
set -a
# shellcheck disable=SC1091
source .env
set +a

exec uvicorn main:app --reload --port 8080 --host 0.0.0.0
