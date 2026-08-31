import sqlite3
from typing import List, Optional

from app.models.cartao import Cartao


class CartaoRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, cartao: Cartao) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO cartoes (nome, limite, dia_fechamento, dia_vencimento, conta_id, ativo)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                cartao.nome,
                cartao.limite,
                cartao.dia_fechamento,
                cartao.dia_vencimento,
                cartao.conta_id,
                int(cartao.ativo),
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_by_id(self, cartao_id: int) -> Optional[Cartao]:
        row = self.conn.execute("SELECT * FROM cartoes WHERE id = ?", (cartao_id,)).fetchone()
        return self._row_to_model(row) if row else None

    def list(self, apenas_ativos: bool = True) -> List[Cartao]:
        query = "SELECT * FROM cartoes"
        if apenas_ativos:
            query += " WHERE ativo = 1"
        query += " ORDER BY nome"
        rows = self.conn.execute(query).fetchall()
        return [self._row_to_model(row) for row in rows]

    def desativar(self, cartao_id: int) -> None:
        self.conn.execute("UPDATE cartoes SET ativo = 0 WHERE id = ?", (cartao_id,))
        self.conn.commit()

    @staticmethod
    def _row_to_model(row: sqlite3.Row) -> Cartao:
        return Cartao(
            id=row["id"],
            nome=row["nome"],
            limite=row["limite"],
            dia_fechamento=row["dia_fechamento"],
            dia_vencimento=row["dia_vencimento"],
            conta_id=row["conta_id"],
            ativo=bool(row["ativo"]),
        )
