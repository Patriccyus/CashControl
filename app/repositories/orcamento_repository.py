import sqlite3
from typing import List, Optional

from app.models.orcamento import Orcamento


class OrcamentoRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, orcamento: Orcamento) -> int:
        cursor = self.conn.execute(
            "INSERT INTO orcamentos (categoria_id, mes, ano, limite) VALUES (?, ?, ?, ?)",
            (orcamento.categoria_id, orcamento.mes, orcamento.ano, orcamento.limite),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_by_id(self, orcamento_id: int) -> Optional[Orcamento]:
        row = self.conn.execute(
            "SELECT * FROM orcamentos WHERE id = ?", (orcamento_id,)
        ).fetchone()
        return self._row_to_model(row) if row else None

    def list_por_mes(self, mes: int, ano: int) -> List[Orcamento]:
        rows = self.conn.execute(
            "SELECT * FROM orcamentos WHERE mes = ? AND ano = ?", (mes, ano)
        ).fetchall()
        return [self._row_to_model(row) for row in rows]

    def update(self, orcamento: Orcamento) -> None:
        self.conn.execute(
            "UPDATE orcamentos SET categoria_id = ?, mes = ?, ano = ?, limite = ? WHERE id = ?",
            (orcamento.categoria_id, orcamento.mes, orcamento.ano, orcamento.limite, orcamento.id),
        )
        self.conn.commit()

    def delete(self, orcamento_id: int) -> None:
        self.conn.execute("DELETE FROM orcamentos WHERE id = ?", (orcamento_id,))
        self.conn.commit()

    @staticmethod
    def _row_to_model(row: sqlite3.Row) -> Orcamento:
        return Orcamento(
            id=row["id"],
            categoria_id=row["categoria_id"],
            mes=row["mes"],
            ano=row["ano"],
            limite=row["limite"],
        )
