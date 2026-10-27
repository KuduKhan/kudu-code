#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -f .env ]]; then
  cp .env.example .env
  echo 'Created .env with loopback-only developer mode. Never expose this mode publicly.'
fi
if [[ ! -d .venv ]]; then python -m venv .venv; fi
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
exec python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
