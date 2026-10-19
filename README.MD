# IJMDB
(Or Internet Jazz Musician Database)

A small, searchable database of jazz musicians, records and labels built using Wikidata, Python and MySQL.
Complete with a nice prototype frontend for average users using the Streamlit Python library.

You can read more at ['/DESIGN.MD'](DESIGN.MD), but after populating the database in MySQL, you can start up the server first defining a 'user' that will be doing all of the app's querying at `frontend/.streamlit/secrets.toml` (see the example) and then using a short shell script at [frontend/start_ijmdb.sh](frontend/start_ijmdb.sh).

## Dependencies

- Python 3.10 or newer (developed on 3.14)
- MySQL, with the `ijmdb` database loaded from [`schema.sql`](schema.sql) and [`queries.sql`](queries.sql)

Python packages the project actually imports:

- `requests`, for the Wikidata calls in [`wiki_tools/web_queries.py`](wiki_tools/web_queries.py)
- `pandas` and `numpy`, for cleaning and loading in [`wiki_tools/data_insert.py`](wiki_tools/data_insert.py)
- `sqlalchemy` and `pymysql`, the database connection used by both the loader and the app
- `streamlit`, for the frontend

`pymysql` is not imported by name. The connection URLs use the `mysql+pymysql` driver, so it has to be installed. `frontend/requirements.txt` covers the app only (`streamlit`, `pandas`, `sqlalchemy`, `pymysql`) and does not include `requests` or `numpy`.

Install the whole set from the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests pandas numpy sqlalchemy pymysql streamlit
```

The notebooks also need Jupyter if you want to rerun them. The start script expects MySQL to be managed by Homebrew (`brew services`). 

I'll be developing this slowly, and eventually publish it so it!