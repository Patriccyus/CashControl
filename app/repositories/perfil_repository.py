import sqlite3
from typing import List, Optional

from app.models.perfil import Perfil


class PerfilRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, perfil: Perfil) -> Perfil:
        cursor = self.conn.execute(
            "INSERT INTO perfis (nome, senha_hash, salt) VALUES (?, ?, ?)",
            (perfil.nome, perfil.senha_hash, perfil.salt),
        )
        self.conn.commit()
        perfil.id = cursor.lastrowid
        return perfil

    def get_by_nome(self, nome: str) -> Optional[Perfil]:
        row = self.conn.execute("SELECT * FROM perfis WHERE nome = ?", (nome,)).fetchone()
        return self._row_to_model(row) if row else None

    def list(self) -> List[Perfil]:
        rows = self.conn.execute("SELECT * FROM perfis ORDER BY nome").fetchall()
        return [self._row_to_model(row) for row in rows]

    @staticmethod
    def _row_to_model(row: sqlite3.Row) -> Perfil:
        return Perfil(
            id=row["id"],
            nome=row["nome"],
            senha_hash=row["senha_hash"],
            salt=row["salt"],
            criado_em=row["criado_em"],
        )
