import sqlite3
from typing import List, Optional

from app.models.forma_pagamento import FormaPagamento


class FormaPagamentoRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, forma_pagamento: FormaPagamento) -> int:
        cursor = self.conn.execute(
            "INSERT INTO formas_pagamento (nome, tipo, ativo) VALUES (?, ?, ?)",
            (forma_pagamento.nome, forma_pagamento.tipo, int(forma_pagamento.ativo)),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_by_id(self, forma_pagamento_id: int) -> Optional[FormaPagamento]:
        row = self.conn.execute(
            "SELECT * FROM formas_pagamento WHERE id = ?", (forma_pagamento_id,)
        ).fetchone()
        return self._row_to_model(row) if row else None

    def list(self, apenas_ativas: bool = True) -> List[FormaPagamento]:
        query = "SELECT * FROM formas_pagamento"
        if apenas_ativas:
            query += " WHERE ativo = 1"
        query += " ORDER BY nome"
        rows = self.conn.execute(query).fetchall()
        return [self._row_to_model(row) for row in rows]

    def update(self, forma_pagamento: FormaPagamento) -> None:
        self.conn.execute(
            "UPDATE formas_pagamento SET nome = ?, tipo = ?, ativo = ? WHERE id = ?",
            (forma_pagamento.nome, forma_pagamento.tipo, int(forma_pagamento.ativo), forma_pagamento.id),
        )
        self.conn.commit()

    def desativar(self, forma_pagamento_id: int) -> None:
        self.conn.execute("UPDATE formas_pagamento SET ativo = 0 WHERE id = ?", (forma_pagamento_id,))
        self.conn.commit()

    @staticmethod
    def _row_to_model(row: sqlite3.Row) -> FormaPagamento:
        return FormaPagamento(
            id=row["id"],
            nome=row["nome"],
            tipo=row["tipo"],
            ativo=bool(row["ativo"]),
        )
