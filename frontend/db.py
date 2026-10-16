"""MySQL connection helpers for the IJMDB Streamlit app."""

from __future__ import annotations

from typing import Any, Mapping

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def _mysql_url() -> str:
    cfg = st.secrets["mysql"]
    user = cfg["user"]
    password = cfg["password"]
    host = cfg["host"]
    port = cfg.get("port", 3306)
    database = cfg["database"]
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"


@st.cache_resource
def get_engine() -> Engine:
    return create_engine(_mysql_url(), pool_pre_ping=True)


def run_query(sql: str, params: Mapping[str, Any] | None = None) -> pd.DataFrame:
    """Run a parameterized read query and return a DataFrame."""
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn, params=dict(params or {}))
