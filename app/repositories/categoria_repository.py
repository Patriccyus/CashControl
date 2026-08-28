import sqlite3
from typing import List, Optional

from app.models.categoria import Categoria


class CategoriaRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, categoria: Categoria) -> int:
        cursor = self.conn.execute(
            "INSERT INTO categorias (nome, tipo, ativo, categoria_pai_id) VALUES (?, ?, ?, ?)",
            (categoria.nome, categoria.tipo, int(categoria.ativo), categoria.categoria_pai_id),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_by_id(self, categoria_id: int) -> Optional[Categoria]:
        row = self.conn.execute(
            "SELECT * FROM categorias WHERE id = ?", (categoria_id,)
        ).fetchone()
        return self._row_to_model(row) if row else None

    def list(self, tipo: Optional[str] = None, apenas_ativas: bool = True) -> List[Categoria]:
        query = "SELECT * FROM categorias WHERE 1=1"
        params: list = []
        if tipo:
            query += " AND tipo = ?"
            params.append(tipo)
        if apenas_ativas:
            query += " AND ativo = 1"
        query += " ORDER BY nome"
        rows = self.conn.execute(query, params).fetchall()
        return [self._row_to_model(row) for row in rows]

    def update(self, categoria: Categoria) -> None:
        self.conn.execute(
            "UPDATE categorias SET nome = ?, tipo = ?, ativo = ?, categoria_pai_id = ? WHERE id = ?",
            (categoria.nome, categoria.tipo, int(categoria.ativo), categoria.categoria_pai_id, categoria.id),
        )
        self.conn.commit()

    def desativar(self, categoria_id: int) -> None:
        self.conn.execute("UPDATE categorias SET ativo = 0 WHERE id = ?", (categoria_id,))
        self.conn.commit()

    @staticmethod
    def _row_to_model(row: sqlite3.Row) -> Categoria:
        return Categoria(
            id=row["id"],
            nome=row["nome"],
            tipo=row["tipo"],
            ativo=bool(row["ativo"]),
            categoria_pai_id=row["categoria_pai_id"],
        )
