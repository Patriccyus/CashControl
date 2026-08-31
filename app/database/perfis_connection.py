import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
PERFIS_DB_PATH = BASE_DIR / "data" / "perfis.db"

SCHEMA_PERFIS = """
CREATE TABLE IF NOT EXISTS perfis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    criado_em TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def get_perfis_connection(db_path: Path = PERFIS_DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_PERFIS)
    conn.commit()
    return conn
