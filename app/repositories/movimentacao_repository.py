import sqlite3
from dataclasses import dataclass
from typing import List, Optional

from app.models.movimentacao import Movimentacao


@dataclass
class FiltroMovimentacao:
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None
    categoria_id: Optional[int] = None
    tipo: Optional[str] = None
    forma_pagamento_id: Optional[int] = None
    conta_id: Optional[int] = None
    status: Optional[str] = None
    busca_texto: Optional[str] = None


class MovimentacaoRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, mov: Movimentacao) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO movimentacoes (
                data, tipo, descricao, valor, categoria_id, subcategoria_id,
                conta_id, forma_pagamento_id, status, observacao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                mov.data,
                mov.tipo,
                mov.descricao,
                mov.valor,
                mov.categoria_id,
                mov.subcategoria_id,
                mov.conta_id,
                mov.forma_pagamento_id,
                mov.status,
                mov.observacao,
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_by_id(self, movimentacao_id: int) -> Optional[Movimentacao]:
        row = self.conn.execute(
            "SELECT * FROM movimentacoes WHERE id = ?", (movimentacao_id,)
        ).fetchone()
        return self._row_to_model(row) if row else None

    def list(self, filtro: Optional[FiltroMovimentacao] = None) -> List[Movimentacao]:
        query = "SELECT * FROM movimentacoes WHERE 1=1"
        params: list = []

        if filtro:
            if filtro.data_inicio:
                query += " AND data >= ?"
                params.append(filtro.data_inicio)
            if filtro.data_fim:
                query += " AND data <= ?"
                params.append(filtro.data_fim)
            if filtro.categoria_id:
                query += " AND categoria_id = ?"
                params.append(filtro.categoria_id)
            if filtro.tipo:
                query += " AND tipo = ?"
                params.append(filtro.tipo)
            if filtro.forma_pagamento_id:
                query += " AND forma_pagamento_id = ?"
                params.append(filtro.forma_pagamento_id)
            if filtro.conta_id:
                query += " AND conta_id = ?"
                params.append(filtro.conta_id)
            if filtro.status:
                query += " AND status = ?"
                params.append(filtro.status)
            if filtro.busca_texto:
                query += " AND (descricao LIKE ? OR observacao LIKE ?)"
                termo = f"%{filtro.busca_texto}%"
                params.extend([termo, termo])

        query += " ORDER BY data DESC, id DESC"
        rows = self.conn.execute(query, params).fetchall()
        return [self._row_to_model(row) for row in rows]

    def update(self, mov: Movimentacao) -> None:
        self.conn.execute(
            """
            UPDATE movimentacoes SET
                data = ?, tipo = ?, descricao = ?, valor = ?, categoria_id = ?,
                subcategoria_id = ?, conta_id = ?, forma_pagamento_id = ?,
                status = ?, observacao = ?, atualizado_em = datetime('now')
            WHERE id = ?
            """,
            (
                mov.data,
                mov.tipo,
                mov.descricao,
                mov.valor,
                mov.categoria_id,
                mov.subcategoria_id,
                mov.conta_id,
                mov.forma_pagamento_id,
                mov.status,
                mov.observacao,
                mov.id,
            ),
        )
        self.conn.commit()

    def delete(self, movimentacao_id: int) -> None:
        self.conn.execute("DELETE FROM movimentacoes WHERE id = ?", (movimentacao_id,))
        self.conn.commit()

    @staticmethod
    def _row_to_model(row: sqlite3.Row) -> Movimentacao:
        return Movimentacao(
            id=row["id"],
            data=row["data"],
            tipo=row["tipo"],
            descricao=row["descricao"],
            valor=row["valor"],
            categoria_id=row["categoria_id"],
            subcategoria_id=row["subcategoria_id"],
            conta_id=row["conta_id"],
            forma_pagamento_id=row["forma_pagamento_id"],
            status=row["status"],
            observacao=row["observacao"],
            criado_em=row["criado_em"],
            atualizado_em=row["atualizado_em"],
        )
