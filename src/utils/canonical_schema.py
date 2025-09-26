from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from sqlalchemy import text
from sqlalchemy.engine import Engine


NON_ALNUM = re.compile(r"[^A-Za-z0-9_]+")


def _snake(s: str) -> str:
    s = s.replace(" ", "_")
    s = NON_ALNUM.sub("_", s)
    s = re.sub(r"_+", "_", s)
    return s.strip("_")


def _normalize_key(k: str) -> str:
    # Case-insensitive and collapse punctuation for matching
    return _snake(k).lower()


def _load_canonical_map(path: str | Path) -> Dict[str, str]:
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    # Return a case-insensitive matcher map: original_key -> canonical_name
    norm_map: Dict[str, str] = {}
    for orig, canon in data.items():
        norm_map[_normalize_key(orig)] = canon
    return norm_map


def _load_canonical_map_with_labels(canon_path: str | Path, header_map_path: Optional[str | Path]) -> Dict[str, str]:
    """
    Build a canonical mapping that matches both coded headers (e.g., RR_C) and
    long human-readable headers (e.g., "Rainfall (mm) | C") to the same
    canonical alias. This allows creating views when base tables use either
    coding style.
    """
    canon = _load_canonical_map(canon_path)
    if header_map_path is None:
        return canon
    p = Path(header_map_path)
    if not p.exists():
        return canon
    try:
        header_data: Dict[str, str] = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return canon
    # header_data maps coded key -> long label; we normalize long label to map to canonical alias
    merged: Dict[str, str] = dict(canon)
    for code, label in header_data.items():
        norm_code = _normalize_key(code)
        alias = canon.get(norm_code)
        if not alias:
            continue
        merged[_normalize_key(label)] = alias
    return merged


def _load_header_labels(path: str | Path) -> Dict[str, str]:
    """Load original header -> human label (the verbose header_map values)."""
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    # Keep original keys as-is, but also allow normalized lookup
    labels: Dict[str, str] = {}
    for k, v in data.items():
        labels[k] = v
        labels[_normalize_key(k)] = v
    return labels


def _get_table_columns(engine: Engine, table_name: str) -> List[str]:
    # Use PRAGMA table_info to include views/tables uniformly if needed
    with engine.connect() as conn:
        res = conn.exec_driver_sql(f'PRAGMA table_info("{table_name}")')
        cols = [row[1] for row in res.fetchall()]
    return cols


def _map_columns_to_canonical(columns: List[str], canon_map: Dict[str, str]) -> List[Tuple[str, str]]:
    pairs: List[Tuple[str, str]] = []
    used_alias = set()
    for col in columns:
        key = _normalize_key(col)
        alias = canon_map.get(key)
        if not alias:
            # Fallback: deterministic snake_case of original
            alias = _snake(col).lower()
        # Ensure unique aliases per view
        base = alias
        i = 2
        while alias in used_alias:
            alias = f"{base}_{i}"
            i += 1
        used_alias.add(alias)
        pairs.append((col, alias))
    return pairs


def ensure_canonical_views(engine: Engine, canonical_map_path: str | Path, header_map_path: Optional[str | Path] = None) -> List[str]:
    """
    For each user table in the SQLite DB, create (or replace) a view named v_<table>
    that exposes the same data with canonical, machine-friendly column names.

    Returns the list of created view names.
    """
    # Support both coded headers and longheaders by merging label-based keys
    canon_map = _load_canonical_map_with_labels(canonical_map_path, header_map_path)

    # Fetch tables (exclude sqlite internal tables and existing v_ views)
    with engine.connect() as conn:
        res = conn.exec_driver_sql(
            "SELECT name, type FROM sqlite_master WHERE (type='table' OR type='view') AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        table_names = [r[0] for r in res if not r[0].startswith("v_")]  # don't re-wrap views

    created_views: List[str] = []

    for table in table_names:
        cols = _get_table_columns(engine, table)
        if not cols:
            continue
        pairs = _map_columns_to_canonical(cols, canon_map)
        select_items = ", ".join([f'"{c}" AS "{a}"' for c, a in pairs])
        view_name = f"v_{table}"
        ddl_drop = f'DROP VIEW IF EXISTS "{view_name}"'
        ddl_create = f'CREATE VIEW "{view_name}" AS SELECT {select_items} FROM "{table}"'
        with engine.begin() as conn:
            conn.exec_driver_sql(ddl_drop)
            conn.exec_driver_sql(ddl_create)
        created_views.append(view_name)

    return created_views


def build_schema_context(
    engine: Engine,
    canonical_map_path: str | Path,
    header_map_path: str | Path,
    include_views: bool = True,
    max_cols_per_table: int = 50,
) -> Dict[str, List[Dict[str, str]]]:
    """
    Build a schema context for prompt injection: for each base table (and optionally its view),
    return a list of dictionaries with canonical name, original column, and human label.

    Example entry:
    {
      "canonical": "rainfall_total_mm",
      "original": "RR_Tot",
      "label": "Rainfall (mm) | Total"
    }
    """
    canon_map = _load_canonical_map(canonical_map_path)  # normalized original -> canonical
    labels = _load_header_labels(header_map_path)        # original or normalized -> label

    with engine.connect() as conn:
        res = conn.exec_driver_sql(
            "SELECT name, type FROM sqlite_master WHERE (type='table' OR type='view') AND name NOT LIKE 'sqlite_%'"
        ).fetchall()

    all_names: List[str] = [r[0] for r in res]
    base_tables = [n for n in all_names if not n.startswith("v_")]
    views = [n for n in all_names if n.startswith("v_")]

    def table_schema(table: str) -> List[Dict[str, str]]:
        cols = _get_table_columns(engine, table)
        items: List[Dict[str, str]] = []
        for c in cols[:max_cols_per_table]:
            norm = _normalize_key(c)
            canonical = canon_map.get(norm)
            if not canonical:
                canonical = _snake(c).lower()
            # Prefer exact label by original name, else by normalized
            label = labels.get(c, labels.get(norm, c))
            items.append({"canonical": canonical, "original": c, "label": label})
        return items

    schema: Dict[str, List[Dict[str, str]]] = {}
    for t in base_tables:
        schema[t] = table_schema(t)
    if include_views:
        for v in views:
            schema[v] = table_schema(v)

    return schema
