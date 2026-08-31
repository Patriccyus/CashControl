import sqlite3
from typing import List, Optional, Set, Tuple

from app.models.fatura_paga import FaturaPaga


class FaturaPagaRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, fatura: FaturaPaga) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO faturas_pagas (cartao_id, mes, ano, valor_pago, data_pagamento, movimentacao_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                fatura.cartao_id,
                fatura.mes,
                fatura.ano,
                fatura.valor_pago,
                fatura.data_pagamento,
                fatura.movimentacao_id,
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get(self, cartao_id: int, mes: int, ano: int) -> Optional[FaturaPaga]:
        row = self.conn.execute(
            "SELECT * FROM faturas_pagas WHERE cartao_id = ? AND mes = ? AND ano = ?",
            (cartao_id, mes, ano),
        ).fetchone()
        return self._row_to_model(row) if row else None

    def periodos_pagos(self, cartao_id: int) -> Set[Tuple[int, int]]:
        rows = self.conn.execute(
            "SELECT mes, ano FROM faturas_pagas WHERE cartao_id = ?", (cartao_id,)
        ).fetchall()
        return {(row["mes"], row["ano"]) for row in rows}

    def list_por_cartao(self, cartao_id: int) -> List[FaturaPaga]:
        rows = self.conn.execute(
            "SELECT * FROM faturas_pagas WHERE cartao_id = ? ORDER BY ano, mes", (cartao_id,)
        ).fetchall()
        return [self._row_to_model(row) for row in rows]

    @staticmethod
    def _row_to_model(row: sqlite3.Row) -> FaturaPaga:
        return FaturaPaga(
            id=row["id"],
            cartao_id=row["cartao_id"],
            mes=row["mes"],
            ano=row["ano"],
            valor_pago=row["valor_pago"],
            data_pagamento=row["data_pagamento"],
            movimentacao_id=row["movimentacao_id"],
        )
