# Deploy IJMDB on Streamlit Community Cloud

This repo is set up for [Streamlit Community Cloud](https://share.streamlit.io/). The app reads a bundled SQLite file (`ijmdb.db` at the repository root).

## One-time setup

1. Push this repository to GitHub (see `origin` remote).
2. Confirm `ijmdb.db` is committed (~4 MB). It is required at runtime; flatfiles used only to rebuild the DB stay gitignored.
3. Sign in at [share.streamlit.io](https://share.streamlit.io/) with GitHub.

## Create the app

1. **Create app** → **Yup, I have an app**.
2. **Repository:** your `ijmdb` (or CS50) repo; **Branch:** `main`.
3. **Main file path:** `frontend/app.py`
4. **App URL (optional):** pick a `*.streamlit.app` subdomain.

Community Cloud installs dependencies from `frontend/requirements.txt` (same directory as the entrypoint).

### Python version

`.python-version` at the repo root requests **Python 3.12.8**. In the Cloud app **Settings → General**, match that version if the build picks something else.

### Secrets (optional)

Default: no secrets needed; `frontend/db.py` opens `{repo_root}/ijmdb.db`.

To override the database file path, add **Secrets** (TOML):

```toml
[sqlite]
database_path = "ijmdb.db"
```

Paths are relative to the repository root unless absolute. See `.streamlit/secrets.toml.example`.

## Run locally like the cloud

From the **repository root** (same working directory as Community Cloud):

```bash
streamlit run frontend/app.py
```

Or:

```bash
./frontend/start_ijmdb.sh
```

Do not rely on `cd frontend && streamlit run app.py` for path debugging—the cloud always uses the repo root as cwd.

## Troubleshooting

| Symptom | Check |
|--------|--------|
| Build fails on dependencies | `frontend/requirements.txt`; Python 3.12 |
| “Could not run query” / no such table | `ijmdb.db` missing from the deployed branch |
| Database file not found | Ensure `ijmdb.db` is tracked in git on that branch |
| Wrong Python | Set 3.12 in Cloud settings and `.python-version` |

## Updating data

Rebuild `ijmdb.db` locally (`schema.sql`, load scripts, `inserts.sql`), commit the new file, and redeploy (or wait for auto-redeploy on push).