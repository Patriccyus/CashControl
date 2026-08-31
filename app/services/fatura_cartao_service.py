import sqlite3
from datetime import date
from typing import List, Optional

from app.analytics.fatura_cartao import FaturaCartao, calcular_fatura, projecao_futura
from app.models.fatura_paga import FaturaPaga
from app.models.movimentacao import Movimentacao
from app.repositories.cartao_repository import CartaoRepository
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.fatura_paga_repository import FaturaPagaRepository
from app.repositories.forma_pagamento_repository import FormaPagamentoRepository
from app.repositories.movimentacao_repository import MovimentacaoRepository
from app.services.exceptions import ErroValidacao

NOME_CATEGORIA_FATURA = "Cartão de crédito"


class FaturaCartaoService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.cartoes = CartaoRepository(conn)
        self.categorias = CategoriaRepository(conn)
        self.formas_pagamento = FormaPagamentoRepository(conn)
        self.faturas_pagas = FaturaPagaRepository(conn)
        self.movimentacoes = MovimentacaoRepository(conn)

    def calcular(
        self, cartao_id: int, mes: int, ano: int, referencia: Optional[date] = None
    ) -> FaturaCartao:
        return calcular_fatura(self.conn, cartao_id, mes, ano, referencia)

    def projecao(self, cartao_id: int, meses: int = 6) -> List[FaturaCartao]:
        return projecao_futura(self.conn, cartao_id, meses)

    def pagar_fatura(
        self, cartao_id: int, mes: int, ano: int, data_pagamento: Optional[str] = None
    ) -> int:
        cartao = self.cartoes.get_by_id(cartao_id)
        if cartao is None:
            raise ErroValidacao("Cartão não encontrado.")

        if self.faturas_pagas.get(cartao_id, mes, ano) is not None:
            raise ErroValidacao("Esta fatura já foi paga.")

        fatura = calcular_fatura(self.conn, cartao_id, mes, ano)
        if fatura.valor_total <= 0:
            raise ErroValidacao("Não há parcelas nesta fatura.")

        categoria = self._categoria_fatura()
        forma_pagamento = self._forma_pagamento_padrao()
        data_pagamento = data_pagamento or date.today().isoformat()

        movimentacao_id = self.movimentacoes.create(
            Movimentacao(
                data=data_pagamento,
                tipo="saida",
                descricao=f"Fatura {cartao.nome} {mes:02d}/{ano}",
                valor=fatura.valor_total,
                categoria_id=categoria.id,
                conta_id=cartao.conta_id,
                forma_pagamento_id=forma_pagamento.id,
                status="pago",
                observacao="Pagamento de fatura de cartão de crédito.",
            )
        )

        return self.faturas_pagas.create(
            FaturaPaga(
                cartao_id=cartao_id,
                mes=mes,
                ano=ano,
                valor_pago=fatura.valor_total,
                data_pagamento=data_pagamento,
                movimentacao_id=movimentacao_id,
            )
        )

    def _categoria_fatura(self):
        for categoria in self.categorias.list(tipo="saida", apenas_ativas=True):
            if categoria.nome == NOME_CATEGORIA_FATURA:
                return categoria
        raise ErroValidacao(
            f"Categoria '{NOME_CATEGORIA_FATURA}' não encontrada. Cadastre-a antes de pagar faturas."
        )

    def _forma_pagamento_padrao(self):
        formas = self.formas_pagamento.list()
        if not formas:
            raise ErroValidacao("Nenhuma forma de pagamento cadastrada.")
        for forma in formas:
            if forma.nome == "Débito":
                return forma
        return formas[0]
