import sqlite3
from pathlib import Path

from app.utils.paths import base_dir, recurso_dir

BASE_DIR = base_dir()
DB_PATH = BASE_DIR / "data" / "controle_financeiro.db"
SCHEMA_PATH = recurso_dir() / "app" / "database" / "schema.sql"


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path = DB_PATH) -> None:
    conn = get_connection(db_path)
    try:
        schema = SCHEMA_PATH.read_text(encoding="utf-8")
        conn.executescript(schema)
        conn.commit()
    finally:
        conn.close()
