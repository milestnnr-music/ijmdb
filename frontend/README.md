# IJMDB Streamlit app

Browser UI for the **ijmdb** SQLite database (`../ijmdb.db` from this folder, resolved via `db.py` from the repo root).

## Local run

From the **repository root** (matches Streamlit Community Cloud):

```bash
./frontend/start_ijmdb.sh
```

Or, with a venv in `frontend/` or the repo root:

```bash
streamlit run frontend/app.py
```

Open **http://localhost:8501**.

## Setup

1. **Database** — `ijmdb.db` at the repo root (see root [`README.MD`](../README.MD)).
2. **Dependencies:** `pip install -r frontend/requirements.txt`
3. **Python** — 3.12 recommended (see root `.python-version`).

## Community Cloud

See [`DEPLOY.md`](../DEPLOY.md): main file `frontend/app.py`, no secrets required if `ijmdb.db` is in the repo.

## Layout

| File | Role |
|------|------|
| `app.py` | Streamlit UI |
| `db.py` | SQLAlchemy + SQLite path + `foreign_keys` pragma |
| `queries/guided.py` | Parameterized SQL |
| `requirements.txt` | Cloud/local pip deps |