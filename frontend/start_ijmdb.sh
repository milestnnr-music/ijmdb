#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f frontend/.venv/bin/activate ]]; then
  # shellcheck source=/dev/null
  source frontend/.venv/bin/activate
elif [[ -f .venv/bin/activate ]]; then
  # shellcheck source=/dev/null
  source .venv/bin/activate
fi

echo "Opening IJMDB at http://localhost:8501"
exec streamlit run frontend/app.py