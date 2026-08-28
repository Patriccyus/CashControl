import sqlite3
from typing import List, Optional

from app.models.recorrencia import Recorrencia


class RecorrenciaRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, recorrencia: Recorrencia) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO recorrencias (descricao, valor, categoria_id, frequencia, proxima_data, ativo)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                recorrencia.descricao,
                recorrencia.valor,
                recorrencia.categoria_id,
                recorrencia.frequencia,
                recorrencia.proxima_data,
                int(recorrencia.ativo),
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_by_id(self, recorrencia_id: int) -> Optional[Recorrencia]:
        row = self.conn.execute(
            "SELECT * FROM recorrencias WHERE id = ?", (recorrencia_id,)
        ).fetchone()
        return self._row_to_model(row) if row else None

    def list(self, apenas_ativas: bool = True) -> List[Recorrencia]:
        query = "SELECT * FROM recorrencias"
        if apenas_ativas:
            query += " WHERE ativo = 1"
        query += " ORDER BY proxima_data"
        rows = self.conn.execute(query).fetchall()
        return [self._row_to_model(row) for row in rows]

    def update(self, recorrencia: Recorrencia) -> None:
        self.conn.execute(
            """
            UPDATE recorrencias SET
                descricao = ?, valor = ?, categoria_id = ?, frequencia = ?,
                proxima_data = ?, ativo = ?
            WHERE id = ?
            """,
            (
                recorrencia.descricao,
                recorrencia.valor,
                recorrencia.categoria_id,
                recorrencia.frequencia,
                recorrencia.proxima_data,
                int(recorrencia.ativo),
                recorrencia.id,
            ),
        )
        self.conn.commit()

    def desativar(self, recorrencia_id: int) -> None:
        self.conn.execute("UPDATE recorrencias SET ativo = 0 WHERE id = ?", (recorrencia_id,))
        self.conn.commit()

    @staticmethod
    def _row_to_model(row: sqlite3.Row) -> Recorrencia:
        return Recorrencia(
            id=row["id"],
            descricao=row["descricao"],
            valor=row["valor"],
            categoria_id=row["categoria_id"],
            frequencia=row["frequencia"],
            proxima_data=row["proxima_data"],
            ativo=bool(row["ativo"]),
        )
