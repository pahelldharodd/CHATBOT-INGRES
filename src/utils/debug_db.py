import sys
from pathlib import Path
from sqlalchemy import create_engine


def list_views_and_columns(db_path: str, table: str | None = None):
    engine = create_engine(f"sqlite:///{db_path}")
    with engine.connect() as conn:
        rows = conn.exec_driver_sql(
            "SELECT name, type FROM sqlite_master WHERE (type='table' OR type='view') AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
        names = [r[0] for r in rows]
        views = [n for n in names if n.startswith("v_")]
        print("All objects:", names)
        print("Views:", views)
        target = f"v_{table}" if table else (views[0] if views else None)
        if target:
            cols = conn.exec_driver_sql(f'PRAGMA table_info("{target}")').fetchall()
            print(f"\nColumns in {target}:")
            for c in cols:
                print("-", c[1])
        else:
            print("No views found.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/utils/debug_db.py <path_to_sqlite_db> [base_table_name]")
        sys.exit(1)
    db_path = sys.argv[1]
    table = sys.argv[2] if len(sys.argv) > 2 else None
    list_views_and_columns(db_path, table)
