#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

source .venv/bin/activate
echo "Opening IJMDB at http://localhost:8501"
exec streamlit run app.py
