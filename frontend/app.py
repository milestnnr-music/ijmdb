"""IJMDB — Streamlit app for the Internet Jazz Musician Database."""

import re
from typing import Literal

import streamlit as st

from db import run_query
from queries.guided import (
    ALBUM_COUNT,
    ALBUMS_BY_YEAR,
    ALBUMS_PER_YEAR,
    DISCOGRAPHY,
    LABEL_COUNT,
    INSTRUMENT_POPULARITY,
    INDIVIDUAL_ALBUMS_STATS,
    INSTRUMENTS_FOR_MUSICIAN,
    LABELS_FOR_MUSICIAN,
    MUSICIAN_COUNT,
    MUSICIAN_MATCH_COUNT,
    MUSICIANS_BY_NAME,
    RARE_INSTRUMENTS,
    SAXOPHONE_BREAKDOWN,
    KEYBOARD_BREAKDOWN,
    LEARN_MORE_ALBUMS,
    LEARN_MORE_LABELS,
    LEARN_MORE_MUSICIANS,
)

st.set_page_config(page_title="IJMDB", page_icon="🎷", layout="wide")

WIKIDATA_URL = "https://www.wikidata.org"
WIKIDATA_POWERED_BY_SVG = (
    "https://upload.wikimedia.org/wikipedia/commons/7/7f/"
    "Powered_by_WIKIDATA_%28plain%29.svg"
)

SIDEBAR_ABOUT = """
**IJMDB** (Internet Jazz Musician Database) is a searchable database of jazz
musicians, albums, labels, and instruments, built from Wikidata.

Common names (e.g. Bill Evans) may refer to more than one person — use
**birth year** when the app asks for it.

Data can be incomplete or duplicated where Wikidata is inconsistent.

This app was developed by Miles Tanner, for a final project for Harvard's CS50 SQL course.
Thanks to the CS50 staff for their help and guidance.

This app was developed in part with the help of Cursor.
"""


def render_wikidata_credit(compact: bool = False) -> None:
    """Wikidata attribution per https://www.wikidata.org/wiki/Wikidata:Data_access"""
    width = 200 if compact else 280
    st.markdown(
        f'<a href="{WIKIDATA_URL}" target="_blank" rel="noopener noreferrer">'
        f'<img src="{WIKIDATA_POWERED_BY_SVG}" alt="Powered by Wikidata" '
        f'width="{width}" style="max-width: 100%; height: auto; display: block;" />'
        f"</a>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Data from [Wikidata](https://www.wikidata.org) (CC0). "
        "This project is not endorsed by Wikidata or the Wikimedia Foundation."
    )


WIKIDATA_ITEM_URL = "https://www.wikidata.org/wiki/{entity_id}"
WIKIPEDIA_EN_VIA_WIKIDATA_URL = (
    "https://www.wikidata.org/wiki/Special:GoToLinkedPage/enwiki/{entity_id}"
)

EntityLinkTarget = Literal["wikidata", "wikipedia"]


def _entity_id_url(entity_id: str, target: EntityLinkTarget) -> str:
    if target == "wikipedia":
        return WIKIPEDIA_EN_VIA_WIKIDATA_URL.format(entity_id=entity_id)
    return WIKIDATA_ITEM_URL.format(entity_id=entity_id)


def _show_dataframe(df, *, entity_link: EntityLinkTarget | None = None) -> None:
    if df.empty:
        st.warning("No rows returned.")
        return
    column_config = None
    display_df = df
    if entity_link and "entity_id" in df.columns:
        display_df = df.copy()
        display_df["entity_id"] = display_df["entity_id"].astype(str).map(
            lambda eid: _entity_id_url(eid, entity_link)
        )
        if entity_link == "wikipedia":
            link_help = (
                "Open English Wikipedia via Wikidata (requires an enwiki sitelink)"
            )
            link_display_text = (
                r"https://www\.wikidata\.org/wiki/Special:GoToLinkedPage/enwiki/(Q\d+)"
            )
        else:
            link_help = "Open this item on Wikidata"
            link_display_text = r"https://www\.wikidata\.org/wiki/(Q\d+)"
        column_config = {
            "entity_id": st.column_config.LinkColumn(
                "Entity ID",
                help=link_help,
                display_text=link_display_text,
            ),
        }
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config=column_config,
    )


def _run_and_show(
    sql: str,
    params: dict | None = None,
    *,
    entity_link: EntityLinkTarget | None = None,
) -> None:
    try:
        df = run_query(sql, params)
    except Exception as exc:
        st.error(
            "Could not run query.")
        st.exception(exc)
        return
    _show_dataframe(df, entity_link=entity_link)


def _musician_name_inputs(
    key_prefix: str,
    name_placeholder: str = "e.g. Miles Davis",
) -> tuple[str, int | None]:
    name = st.text_input(
        "Musician name",
        value="",
        key=f"{key_prefix}_name",
        placeholder=name_placeholder,
    )
    use_year = st.checkbox(
        "Specify birth year (for duplicate names)",
        value=False,
        key=f"{key_prefix}_use_year",
    )
    birth_year: int | None = None
    if use_year:
        birth_year = st.number_input(
            "Birth year",
            min_value=1800,
            max_value=2100,
            value=1929,
            step=1,
            key=f"{key_prefix}_year",
        )
    return name.strip(), birth_year


def _run_for_musician(
    name: str,
    birth_year: int | None,
    sql: str,
    extra_params: dict | None = None,
) -> None:
    """Run a musician-scoped query after duplicate-name checks (same as discography)."""
    if not name:
        st.warning("Enter a musician name.")
        return
    matches = run_query(MUSICIAN_MATCH_COUNT, {"name": name})
    n = int(matches.iloc[0]["n"])
    if n == 0:
        st.warning(f"No musician named “{name}”.")
    elif n > 1 and birth_year is None:
        st.info(
            f"Found {n} musicians named “{name}”. "
            "Enable **Specify birth year (for duplicate names)** to pick one."
        )
        _run_and_show(MUSICIANS_BY_NAME, {"name": name})
    else:
        params = {"name": name, "birth_year": birth_year,
                  "musician_name": name}
        if extra_params:
            params.update(extra_params)
        _run_and_show(sql, params)


def render_musicians_tab() -> None:
    st.subheader("Musicians")

    st.markdown("#### Discography")
    st.caption(
        "Albums this musician is linked to on Wikidata (may be incomplete).")
    name, birth_year = _musician_name_inputs("disc", "e.g. Miles Davis")
    if st.button("Run discography", key="btn_disc"):
        _run_for_musician(name, birth_year, DISCOGRAPHY)

    st.divider()
    st.markdown("#### Record labels")
    st.caption("Labels from albums this musician was associated with.")
    label_name, label_birth_year = _musician_name_inputs(
        "labels", "e.g. Bill Evans")
    if st.button("Find labels", key="btn_labels"):
        _run_for_musician(label_name, label_birth_year, LABELS_FOR_MUSICIAN)

    st.divider()
    st.markdown("#### Instruments played")
    inst_name, inst_birth_year = _musician_name_inputs(
        "inst", "e.g. Herbie Hancock")
    if st.button("List instruments", key="btn_inst_mus"):
        _run_for_musician(inst_name, inst_birth_year, INSTRUMENTS_FOR_MUSICIAN)


def render_albums_tab() -> None:
    st.subheader("Albums")

    st.markdown("#### Individual album search")
    st.caption("Search for a specific album by name or any part of the name. (Use the 'Discography' search in the Musicians tab to find all performers for an album.)")
    album_name = st.text_input(
        "Album name",
        value="",
        key="album_name",
        placeholder="e.g. Kind of Blue",
    )
    if st.button("Search albums", key="btn_album_name"):
        _run_and_show(INDIVIDUAL_ALBUMS_STATS, {
                      "name_pattern": f"%{album_name}%"})

    st.markdown("#### Albums released in a year")
    year = st.number_input(
        "Release year",
        min_value=1900,
        max_value=2100,
        value=1959,
        step=1,
        key="album_year",
    )
    if st.button("List albums", key="btn_album_year"):
        _run_and_show(ALBUMS_BY_YEAR, {"year": int(year)})

    st.divider()
    st.markdown("#### Albums per year")
    st.caption("None means Wikidata had no release year for that album.")
    if st.button("Show counts by year", key="btn_album_counts"):
        df = run_query(ALBUMS_PER_YEAR)
        st.dataframe(df, use_container_width=True, hide_index=True)
        chart_df = df.dropna(subset=["release_year"]).copy()
        if not chart_df.empty:
            chart_df = chart_df.sort_values("release_year")
            st.bar_chart(chart_df, x="release_year", y="album_count")


def render_stats_tab() -> None:
    st.subheader("Instruments & stats")

    st.markdown("#### Instrument popularity ranking")
    st.caption("Which instruments are the most and least popular?")
    if st.button("Show instrument counts", key="btn_inst_pop"):
        _run_and_show(INSTRUMENT_POPULARITY)

    st.divider()
    st.markdown("#### Saxophones ranking")
    st.caption("Which saxophone is the most popular?")
    if st.button("Saxophone breakdown", key="btn_sax"):
        _run_and_show(SAXOPHONE_BREAKDOWN)

    st.divider()
    st.markdown("#### Keyboards and pianos ranking")
    st.caption("Which keyboard is the most popular?")
    if st.button("Keyboard breakdown", key="btn_keyboard"):
        _run_and_show(KEYBOARD_BREAKDOWN)

    st.divider()
    st.markdown("#### Rare instruments")
    max_count = st.slider(
        "Show instruments played by at most this many musicians",
        min_value=1,
        max_value=20,
        value=5,
        key="rare_max",
    )
    if st.button("Find rare instruments", key="btn_rare"):
        _run_and_show(RARE_INSTRUMENTS, {"max_count": max_count})


def _is_select_only(sql: str) -> bool:
    stripped = sql.strip().rstrip(";")
    if not stripped:
        return False
    # Allow a single SELECT (or WITH ... SELECT); reject obvious multi-statements.
    if ";" in stripped:
        return False
    upper = stripped.upper()
    if not (upper.startswith("SELECT") or upper.startswith("WITH")):
        return False
    forbidden = (
        "INSERT ",
        "UPDATE ",
        "DELETE ",
        "DROP ",
        "ALTER ",
        "CREATE ",
        "TRUNCATE ",
        "GRANT ",
        "REVOKE ",
    )
    return not any(tok in upper for tok in forbidden)


def _ensure_limit(sql: str, limit: int = 500) -> str:
    if re.search(r"\bLIMIT\b", sql, re.IGNORECASE):
        return sql
    return f"{sql.rstrip(';')} LIMIT {limit}"


def render_learn_more_tab() -> None:
    st.subheader("Learn more")
    st.caption(
        "Look up Wikidata entity IDs (Q-numbers) stored in IJMDB. "
        "Search matches any part of the name (up to 500 rows)."
    )
    entity_kind = st.radio(
        "Search for",
        options=["Musicians", "Albums", "Labels"],
        horizontal=True,
        key="learn_more_kind",
    )
    link_destination = st.radio(
        "Open entity ID links on",
        options=["Wikidata", "English Wikipedia"],
        horizontal=True,
        key="learn_more_link_dest",
    )
    entity_link: EntityLinkTarget = (
        "wikipedia" if link_destination == "English Wikipedia" else "wikidata"
    )
    name_query = st.text_input(
        "Name", value="", key="learn_more_name", placeholder="e.g. Davis")
    if st.button("Search", key="btn_learn_more"):
        term = name_query.strip()
        if not term:
            st.warning("Enter a name to search.")
            return
        params = {"name_pattern": f"%{term}%"}
        if entity_kind == "Musicians":
            _run_and_show(LEARN_MORE_MUSICIANS, params,
                          entity_link=entity_link)
        elif entity_kind == "Albums":
            _run_and_show(LEARN_MORE_ALBUMS, params, entity_link=entity_link)
        else:
            _run_and_show(LEARN_MORE_LABELS, params, entity_link=entity_link)


def render_advanced_tab() -> None:
    st.subheader("Advanced SQL")
    st.caption(
        "Read-only access: only SELECT (and WITH) queries are accepted. "
        "A LIMIT 500 is added if you omit LIMIT."
    )
    default = "SELECT name, year_of_birth FROM musicians ORDER BY name LIMIT 10"
    sql = st.text_area("SQL", value=default, height=160, key="advanced_sql")
    if st.button("Run SQL", key="btn_advanced"):
        query = sql.strip()
        if not _is_select_only(query):
            st.error("Only a single SELECT or WITH query is allowed.")
            return
        query = _ensure_limit(query)
        _run_and_show(query)


def main() -> None:
    with st.sidebar:
        st.title("IJMDB")
        st.markdown(SIDEBAR_ABOUT)
        try:
            musicians_df = run_query(MUSICIAN_COUNT)
            albums_df = run_query(ALBUM_COUNT)
            labels_df = run_query(LABEL_COUNT)
            st.metric("Musicians in database", int(musicians_df.iloc[0]["n"]))
            st.metric("Albums in database", int(albums_df.iloc[0]["n"]))
            st.metric("Labels in database", int(labels_df.iloc[0]["n"]))
        except Exception:
            st.error("Database unavailable")
        st.divider()
        render_wikidata_credit(compact=True)

    st.title("Internet Jazz Musician Database")
    tabs = st.tabs(["Musicians", "Albums", "Stats",
                   "Learn More", "Advanced SQL"])
    with tabs[0]:
        render_musicians_tab()
    with tabs[1]:
        render_albums_tab()
    with tabs[2]:
        render_stats_tab()
    with tabs[3]:
        render_learn_more_tab()
    with tabs[4]:
        render_advanced_tab()

    st.divider()
    render_wikidata_credit()


if __name__ == "__main__":
    main()
