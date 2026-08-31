import sqlite3
from typing import List, Optional, Set, Tuple

from app.models.compra_cartao import CompraCartao, ItemParcelaFatura, ParcelaCartao


class CompraCartaoRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, compra: CompraCartao) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO compras_cartao (cartao_id, categoria_id, descricao, data_compra, valor_total, numero_parcelas)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                compra.cartao_id,
                compra.categoria_id,
                compra.descricao,
                compra.data_compra,
                compra.valor_total,
                compra.numero_parcelas,
            ),
        )
        compra_id = cursor.lastrowid

        self.conn.executemany(
            "INSERT INTO parcelas_cartao (compra_id, numero, valor, fatura_mes, fatura_ano) VALUES (?, ?, ?, ?, ?)",
            [
                (compra_id, parcela.numero, parcela.valor, parcela.fatura_mes, parcela.fatura_ano)
                for parcela in compra.parcelas
            ],
        )
        self.conn.commit()
        return compra_id

    def get_by_id(self, compra_id: int) -> Optional[CompraCartao]:
        row = self.conn.execute("SELECT * FROM compras_cartao WHERE id = ?", (compra_id,)).fetchone()
        if row is None:
            return None
        compra = self._row_to_model(row)
        compra.parcelas = self._parcelas_da_compra(compra_id)
        return compra

    def list_por_cartao(self, cartao_id: int) -> List[CompraCartao]:
        rows = self.conn.execute(
            "SELECT * FROM compras_cartao WHERE cartao_id = ? ORDER BY data_compra DESC", (cartao_id,)
        ).fetchall()
        compras = [self._row_to_model(row) for row in rows]
        for compra in compras:
            compra.parcelas = self._parcelas_da_compra(compra.id)
        return compras

    def delete(self, compra_id: int) -> None:
        self.conn.execute("DELETE FROM parcelas_cartao WHERE compra_id = ?", (compra_id,))
        self.conn.execute("DELETE FROM compras_cartao WHERE id = ?", (compra_id,))
        self.conn.commit()

    def parcelas_por_fatura(self, cartao_id: int, mes: int, ano: int) -> List[ItemParcelaFatura]:
        rows = self.conn.execute(
            """
            SELECT p.id AS parcela_id, p.compra_id, c.descricao, c.categoria_id,
                   p.numero, c.numero_parcelas, p.valor
            FROM parcelas_cartao p
            JOIN compras_cartao c ON c.id = p.compra_id
            WHERE c.cartao_id = ? AND p.fatura_mes = ? AND p.fatura_ano = ?
            ORDER BY c.descricao
            """,
            (cartao_id, mes, ano),
        ).fetchall()
        return [
            ItemParcelaFatura(
                parcela_id=row["parcela_id"],
                compra_id=row["compra_id"],
                descricao=row["descricao"],
                categoria_id=row["categoria_id"],
                numero=row["numero"],
                numero_parcelas=row["numero_parcelas"],
                valor=row["valor"],
            )
            for row in rows
        ]

    def parcelas_futuras_por_periodo(self, cartao_id: int) -> List[Tuple[int, int, int]]:
        rows = self.conn.execute(
            """
            SELECT p.fatura_mes, p.fatura_ano, SUM(p.valor) AS total
            FROM parcelas_cartao p
            JOIN compras_cartao c ON c.id = p.compra_id
            WHERE c.cartao_id = ?
            GROUP BY p.fatura_mes, p.fatura_ano
            """,
            (cartao_id,),
        ).fetchall()
        return [(row["fatura_mes"], row["fatura_ano"], row["total"]) for row in rows]

    def total_em_aberto(self, cartao_id: int, periodos_pagos: Set[Tuple[int, int]]) -> int:
        return sum(
            total
            for mes, ano, total in self.parcelas_futuras_por_periodo(cartao_id)
            if (mes, ano) not in periodos_pagos
        )

    def _parcelas_da_compra(self, compra_id: int) -> List[ParcelaCartao]:
        rows = self.conn.execute(
            "SELECT * FROM parcelas_cartao WHERE compra_id = ? ORDER BY numero", (compra_id,)
        ).fetchall()
        return [
            ParcelaCartao(
                id=row["id"],
                compra_id=row["compra_id"],
                numero=row["numero"],
                valor=row["valor"],
                fatura_mes=row["fatura_mes"],
                fatura_ano=row["fatura_ano"],
            )
            for row in rows
        ]

    @staticmethod
    def _row_to_model(row: sqlite3.Row) -> CompraCartao:
        return CompraCartao(
            id=row["id"],
            cartao_id=row["cartao_id"],
            categoria_id=row["categoria_id"],
            descricao=row["descricao"],
            data_compra=row["data_compra"],
            valor_total=row["valor_total"],
            numero_parcelas=row["numero_parcelas"],
            criado_em=row["criado_em"],
        )
