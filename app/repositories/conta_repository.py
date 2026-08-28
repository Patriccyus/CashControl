import sqlite3
from typing import List, Optional

from app.models.conta import Conta


class ContaRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, conta: Conta) -> int:
        cursor = self.conn.execute(
            "INSERT INTO contas (nome, tipo, saldo_inicial, ativo) VALUES (?, ?, ?, ?)",
            (conta.nome, conta.tipo, conta.saldo_inicial, int(conta.ativo)),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_by_id(self, conta_id: int) -> Optional[Conta]:
        row = self.conn.execute("SELECT * FROM contas WHERE id = ?", (conta_id,)).fetchone()
        return self._row_to_model(row) if row else None

    def list(self, apenas_ativas: bool = True) -> List[Conta]:
        query = "SELECT * FROM contas"
        if apenas_ativas:
            query += " WHERE ativo = 1"
        query += " ORDER BY nome"
        rows = self.conn.execute(query).fetchall()
        return [self._row_to_model(row) for row in rows]

    def update(self, conta: Conta) -> None:
        self.conn.execute(
            "UPDATE contas SET nome = ?, tipo = ?, saldo_inicial = ?, ativo = ? WHERE id = ?",
            (conta.nome, conta.tipo, conta.saldo_inicial, int(conta.ativo), conta.id),
        )
        self.conn.commit()

    def desativar(self, conta_id: int) -> None:
        self.conn.execute("UPDATE contas SET ativo = 0 WHERE id = ?", (conta_id,))
        self.conn.commit()

    @staticmethod
    def _row_to_model(row: sqlite3.Row) -> Conta:
        return Conta(
            id=row["id"],
            nome=row["nome"],
            tipo=row["tipo"],
            saldo_inicial=row["saldo_inicial"],
            ativo=bool(row["ativo"]),
        )
