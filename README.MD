# IJMDB
(Or Internet Jazz Musician Database)

A small, searchable database of jazz musicians, records and labels built using Wikidata, Python and SQLite.
Complete with a prototype frontend for average users using the Streamlit Python library.

You can read more at [`DESIGN.md`](DESIGN.md). After building and populating the database (see below), start the app with [frontend/start_ijmdb.sh](frontend/start_ijmdb.sh) or deploy to **Streamlit Community Cloud** using [`DEPLOY.md`](DEPLOY.md).

## Database setup

1. Create the schema (from the project root):
   ```bash
   sqlite3 ijmdb.db ".read schema.sql"
   ```
2. Load record tables from flatfiles via [`data_insert.ipynb`](data_insert.ipynb) / [`wiki_tools/data_insert.py`](wiki_tools/data_insert.py).
3. Run junction inserts: `sqlite3 ijmdb.db ".read inserts.sql"`

Example queries live in [`queries.sql`](queries.sql).

## Dependencies

- Python 3.10 or newer (developed on 3.14)
- SQLite 3 (included with macOS; used via the `sqlite3` CLI and SQLAlchemy)

Python packages the project imports:

- `requests`, for Wikidata calls in [`wiki_tools/web_queries.py`](wiki_tools/web_queries.py)
- `pandas` and `numpy`, for cleaning and loading in [`wiki_tools/data_insert.py`](wiki_tools/data_insert.py)
- `sqlalchemy`, for the loader and the Streamlit app
- `streamlit`, for the frontend

`frontend/requirements.txt` covers the app only (`streamlit`, `pandas`, `sqlalchemy`) and does not include `requests` or `numpy`.

Install the full set from the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests pandas numpy sqlalchemy streamlit
```

The notebooks also need Jupyter if you want to rerun them.

## Streamlit app

From the repository root (same layout as Community Cloud):

```bash
pip install -r frontend/requirements.txt
streamlit run frontend/app.py
```

Public hosting steps: [`DEPLOY.md`](DEPLOY.md). Entrypoint: `frontend/app.py`; database: `ijmdb.db` in this repo.