# IJMDB Streamlit demo (local)

Browser UI for querying the **ijmdb** MySQL database on this Mac.

## First-time setup

1. **MySQL** — database `ijmdb` loaded (see parent `dump.sql`). Start server:
   ```bash
   brew services start mysql
   ```

2. **Read-only app user** (if not already created):
   ```sql
   CREATE USER 'ijmdb_app'@'localhost' IDENTIFIED BY 'your_password';
   GRANT SELECT ON ijmdb.* TO 'ijmdb_app'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. **Secrets** — copy and edit:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

4. **Python env**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## Run the app

```bash
./start_ijmdb.sh
```

Or manually:

```bash
source .venv/bin/activate
streamlit run app.py
```

Open **http://localhost:8501** in a browser.

## Hand-the-laptop demo

- Start MySQL and run `./start_ijmdb.sh` before handing over the machine.
- Use fullscreen in the browser; disable sleep while demoing.
- Quit with Ctrl+C in the Terminal window running Streamlit.

## Project layout

| File | Role |
|------|------|
| `app.py` | Streamlit UI (tabs + Advanced SQL) |
| `db.py` | SQLAlchemy engine and `run_query` |
| `queries/guided.py` | Parameterized SQL from `../queries.sql` |
| `.streamlit/secrets.toml` | Local DB credentials (gitignored) |

See **`plan.md`** for the full learning guide and architecture notes.
