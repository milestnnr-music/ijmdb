# Local Streamlit app for IJMDB (hand-the-laptop demo)

## Implementation status

This guide matches the approved plan. The app is implemented in this folder:

- `app.py`, `db.py`, `queries/guided.py`
- `.streamlit/config.toml`, `.streamlit/secrets.toml` (local), `.streamlit/secrets.toml.example`
- `start_ijmdb.sh`, `README.md`

Run with `./start_ijmdb.sh` or `streamlit run app.py` after MySQL is up.

---

## What you are building

You already have the hard parts done: schema, data, and example questions in the parent project ([`schema.sql`](../schema.sql), [`dump.sql`](../dump.sql), [`queries.sql`](../queries.sql)). The new piece is a **thin UI layer** in `frontend/` that:

1. Connects to **MySQL on `localhost`** (same machine as the browser).
2. Runs **read-only** `SELECT` queries.
3. Presents **guided screens** for common jazz-DB questions, plus an **Advanced SQL** area for experimentation.

```mermaid
flowchart LR
  subgraph yourMac [Your Mac]
    Browser[Browser localhost:8501]
    Streamlit[Streamlit Python process]
    MySQL[(MySQL ijmdb)]
  end
  Browser -->|HTTP| Streamlit
  Streamlit -->|TCP 127.0.0.1:3306| MySQL
```

**Why this works without Streamlit Cloud:** Streamlit and MySQL both run on one computer. The app uses host `127.0.0.1` (or `localhost`)—no internet, tunnels, or port forwarding required.

**Database name:** Your dump uses **`ijmdb`** (`dump.sql` line 3). Note: `schema.sql` has `CREATE DATABASE ijmdb` but `USE imjdb` (typo)—when configuring the app, use whichever database you actually restored (almost certainly `ijmdb`).

---

## Phase 0 — Prerequisites checklist (before writing UI code)

Do this once; repeat only if you reinstall MySQL or wipe the DB.

| Step | What to verify | Why it matters |
|------|----------------|----------------|
| MySQL running | `brew services list` shows `mysql` started (per your DESIGN.md stack) | Streamlit cannot connect if the server is stopped |
| Database loaded | Client connects and `USE ijmdb; SHOW TABLES;` lists `musicians`, `albums`, etc. | Empty or wrong DB = blank app |
| Views exist | `SHOW FULL TABLES WHERE Table_type = 'VIEW';` shows `instrument_count`, `musician_stats`, `album_list` | Guided pages can reuse views from `schema.sql` |
| Sample query works | Run one query from `queries.sql` in DBeaver or CLI | Confirms credentials and data before debugging Python |

**Restore path (if needed):** import `dump.sql` into MySQL so the laptop matches your development state.

---

## Phase 1 — Python project in `frontend/`

### 1.1 Virtual environment

Create an isolated environment inside `frontend/` so dependencies do not clash with notebook work in the parent folder:

```bash
cd /Users/milestanner/Desktop/CS50SQL_FP/frontend
python3 -m venv .venv
source .venv/bin/activate
```

**Concept:** Streamlit is just a Python script; `venv` pins the packages for this app only.

### 1.2 Dependencies

Align with what you already use for data work (SQLAlchemy + PyMySQL + Pandas), and add Streamlit:

**`requirements.txt`**:

```text
streamlit
pandas
sqlalchemy
pymysql
python-dotenv
```

Install: `pip install -r requirements.txt`

**Concept:** SQLAlchemy builds a **connection URL**; Pandas turns result rows into a table widget; Streamlit renders widgets and reruns the script on interaction.

### 1.3 Git hygiene

Add to `frontend/.gitignore` (or extend a repo root ignore):

- `.venv/`
- `.env`
- `.streamlit/secrets.toml`

Never commit MySQL passwords.

---

## Phase 2 — Configuration (secrets without hardcoding)

### 2.1 Local secrets file

Create `frontend/.streamlit/secrets.toml`:

```toml
[mysql]
host = "127.0.0.1"
port = 3306
user = "ijmdb_app"
password = "choose_a_local_password"
database = "ijmdb"
```

Streamlit loads this automatically. In code: `st.secrets["mysql"]`.

**Alternative for learning:** `python-dotenv` + `.env` with the same keys; load in `app.py` only when not using secrets. Pick one pattern and stick to it.

### 2.2 Dedicated MySQL user (recommended)

Create a user that can **only read** your project data—safe if someone types SQL in Advanced mode:

```sql
CREATE USER 'ijmdb_app'@'localhost' IDENTIFIED BY 'your_password';
GRANT SELECT ON ijmdb.* TO 'ijmdb_app'@'localhost';
FLUSH PRIVILEGES;
```

**Concept:** Your admin/root user can still manage the DB; the app uses `ijmdb_app` so mistakes in the UI cannot `DROP` tables.

---

## Phase 3 — App architecture (files to add)

Suggested layout:

```text
frontend/
  app.py                 # entry: streamlit run app.py
  db.py                  # engine + run_query helper
  pages/                 # optional: Streamlit multipage
    01_Musicians.py
    02_Albums.py
    03_Stats.py
    99_Advanced_SQL.py
  queries/
    guided.py            # parameterized SQL strings
  requirements.txt
  .streamlit/
    config.toml          # theme, maybe server address for demo
    secrets.toml         # local only, gitignored
  README.md              # short "how to start" for you
  plan.md                # this document
```

**Single-file MVP is fine:** start with one `app.py`; split into `pages/` when guided sections grow. The current build uses **tabs in `app.py`** instead of multipage files.

### 3.1 `db.py` — one connection, many queries

Pattern to learn:

- `@st.cache_resource` on `get_engine()` — open the pool once per Streamlit server process.
- `run_query(sql, params)` — use `sqlalchemy.text(sql)` and **bound parameters** (`:name`, `:year`) for guided queries.
- Return `pd.DataFrame` for `st.dataframe()`.

Connection URL (same style as your notebooks):

`mysql+pymysql://user:pass@127.0.0.1:3306/ijmdb`

### 3.2 Guided UI — map to `queries.sql`

Build **parameterized** versions of your file’s questions (never paste user text directly into SQL strings without binding).

| Guided screen | User inputs | Based on | SQL idea |
|---------------|-------------|----------|----------|
| Discography | Musician name | queries.sql L6–13 | Albums via `recorded_by` + `musicians.id` |
| Albums by year | Year | L18–21 | `albums.release_year` |
| Albums per year | (none) | L26–29 | `GROUP BY release_year` chart/table |
| Disambiguate musicians | Name | L34–40 | Join `played` / `instruments` (Bill Evans case) |
| Labels for musician | Name + birth year | L46–58 | Subqueries through `recorded_on` |
| Instrument popularity | (none) | L63–68 or view `instrument_count` | Prefer **view** for simpler SQL |
| Saxophone breakdown | (none) | L73–79 | `LIKE '%saxophone'` |
| Rare instruments | max count threshold | L84–86 | `instrument_count` with `WHERE count <= :n` |
| Instruments for musician | Name | L93 | `musician_stats` view |

**UX patterns for family/friends:**

- `st.selectbox` or `st.text_input` with **examples in placeholder** (“Miles Davis”, “1959”).
- `st.button("Run")` — clear cause and effect.
- `st.info` when a name matches multiple rows → prompt for birth year (teaches your data model).
- `st.bar_chart` on year/count queries for visual payoff.

**Duplicate names:** Your indexes and queries already assume `name` + `year_of_birth` disambiguation—surface that in the UI copy (one sentence in the sidebar).

### 3.3 Advanced SQL page

For power users and your own testing:

- `st.text_area` for SQL.
- On Run:
  - Strip whitespace; reject unless the statement **starts with** `SELECT` (case-insensitive). This is a **UX guard**, not security—the real guard is the read-only MySQL user.
  - Optional: append `LIMIT 500` if no `LIMIT` present (protects against huge accidental scans).
- Show errors with `st.exception` or friendly `st.error` (hide raw stack traces for demo mode if you prefer).

Do **not** use Python f-strings to inject user SQL into guided queries; only use parameters.

### 3.4 Entrypoint `app.py`

- `st.set_page_config(page_title="IJMDB", layout="wide")`
- Sidebar: project blurb from DESIGN.md abstract (Wikidata jazz DB, limitations).
- Navigation: either `st.navigation` / multipage `pages/` or tabs `st.tabs(["Musicians", "Albums", "Stats", "Advanced SQL"])`.

---

## Phase 4 — Run and validate locally

```bash
cd /Users/milestanner/Desktop/CS50SQL_FP/frontend
source .venv/bin/activate
streamlit run app.py
```

Default URL: **http://localhost:8501**

**Validation script (mental checklist):**

1. App loads with no traceback.
2. One guided query returns known rows (e.g. Miles Davis albums).
3. Advanced SQL: valid `SELECT 1` works; `DELETE FROM musicians` fails (MySQL permission error).
4. Stop app: Ctrl+C in terminal.

**Optional `config.toml`** for demo on your machine:

```toml
[server]
headless = true
```

`headless` avoids Streamlit trying to open a second browser when you already opened one manually.

---

## Phase 5 — “Hand the laptop to someone” playbook

Technical setup is not enough for a smooth demo.

| Concern | What to do |
|---------|------------|
| Laptop sleeps | System Settings → disable sleep on battery while demoing; keep lid open or use clamshell settings you trust |
| MySQL stopped | Before handing over: `brew services start mysql` |
| Starting the app | Simple shell script `start_ijmdb.sh`: `cd frontend`, `source .venv/bin/activate`, `streamlit run app.py` — double-click or run from Terminal |
| Browser | Leave Safari/Chrome on `localhost:8501`; fullscreen (Cmd+Ctrl+F) |
| Account safety | Prefer macOS **Guest User** or a separate demo account so they do not read email/files; app only needs browser |
| Quit cleanly | Document: close tab, Ctrl+C in Terminal, or leave running until you reclaim the machine |

You are **not** sharing a link—you are sharing **hardware + a local URL**. That URL only works on your Mac while Streamlit and MySQL are running.

---

## Phase 6 — Learning milestones (suggested order)

1. **Hello DB:** minimal `app.py` that runs `SELECT COUNT(*) FROM musicians` and shows one number.
2. **Engine module:** move connection to `db.py`; add secrets.
3. **One guided query:** discography with `:musician_name` parameter.
4. **Views:** switch instrument stats to `instrument_count` view—compare to raw join in `queries.sql`.
5. **Advanced page:** SELECT-only guard + read-only user test.
6. **Polish:** sidebar help, empty-state messages, chart for albums-by-year.

Each milestone is independently testable—if something breaks, you know which layer failed (MySQL vs credentials vs SQL vs Streamlit widgets).

---

## Bridge to Option A (Streamlit Cloud later)

When you migrate to cloud MySQL, you will change **only configuration**:

- Same `db.py` URL builder, different `host` / `user` / `password` in Streamlit Cloud **Secrets**.
- Import `dump.sql` to the hosted instance.
- Deploy the same `frontend/` repo; no need to redesign guided queries.

Local development then uses `secrets.toml`; production uses Cloud secrets—same keys, different values.
