"""SQLite connection helpers for the IJMDB Streamlit app."""

from __future__ import annotations

from typing import Any, Mapping

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from pathlib import Path


sqlite3_url = "sqlite:///../ijmdb.db"


@st.cache_resource
def get_engine() -> Engine:
    return create_engine(sqlite3_url, pool_pre_ping=True)


def run_query(sql: str, params: Mapping[str, Any] | None = None) -> pd.DataFrame:
    """Run a parameterized read query and return a DataFrame."""
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn, params=dict(params or {}))
