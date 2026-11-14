"""SQLite connection helpers for the IJMDB Streamlit app."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine

_REPO_ROOT = Path(__file__).resolve().parent.parent


def _database_path() -> Path:
    """Resolve path to ijmdb.db (repo root by default)."""
    if "sqlite" in st.secrets and "database_path" in st.secrets["sqlite"]:
        raw = st.secrets["sqlite"]["database_path"]
        path = Path(raw)
        if not path.is_absolute():
            path = _REPO_ROOT / path
        return path
    return _REPO_ROOT / "ijmdb.db"


def _sqlite_url() -> str:
    return f"sqlite:///{_database_path()}"


@st.cache_resource
def get_engine() -> Engine:
    engine = create_engine(_sqlite_url(), pool_pre_ping=True)

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_conn, _connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def run_query(sql: str, params: Mapping[str, Any] | None = None) -> pd.DataFrame:
    """Run a parameterized read query and return a DataFrame."""
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn, params=dict(params or {}))