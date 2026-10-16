#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if ! brew services list 2>/dev/null | grep -q "mysql.*started"; then
  echo "Starting MySQL (brew services start mysql)..."
  brew services start mysql
fi

if [[ ! -f .streamlit/secrets.toml ]]; then
  echo "Missing .streamlit/secrets.toml — copy from .streamlit/secrets.toml.example"
  exit 1
fi

source .venv/bin/activate
echo "Opening IJMDB at http://localhost:8501"
exec streamlit run app.py
