from app.analytics.fatura_cartao import total_despesas_futuras_cartoes
from app.models.categoria import Categoria
from app.models.conta import Conta
from app.models.forma_pagamento import FormaPagamento
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.conta_repository import ContaRepository
from app.repositories.forma_pagamento_repository import FormaPagamentoRepository
from app.services.cartao_service import CartaoService
from app.services.compra_cartao_service import CompraCartaoService
from app.services.fatura_cartao_service import FaturaCartaoService


def test_total_despesas_futuras_soma_parcelas_nao_pagas(conn):
    conta_id = ContaRepository(conn).create(Conta(nome="Conta corrente", tipo="conta_corrente"))
    categoria_id = CategoriaRepository(conn).create(Categoria(nome="Lazer", tipo="saida"))
    cartao_id = CartaoService(conn).criar(
        nome="Nubank", limite=500000, dia_fechamento=25, dia_vencimento=5, conta_id=conta_id
    )

    CompraCartaoService(conn).registrar_compra(
        cartao_id=cartao_id,
        categoria_id=categoria_id,
        descricao="Notebook",
        data_compra="2026-08-10",
        valor_total=90000,
        numero_parcelas=3,
    )

    assert total_despesas_futuras_cartoes(conn) == 90000


def test_total_despesas_futuras_exclui_faturas_pagas(conn):
    conta_id = ContaRepository(conn).create(Conta(nome="Conta corrente", tipo="conta_corrente"))
    CategoriaRepository(conn).create(Categoria(nome="Cartão de crédito", tipo="saida"))
    categoria_id = CategoriaRepository(conn).create(Categoria(nome="Lazer", tipo="saida"))
    FormaPagamentoRepository(conn).create(FormaPagamento(nome="Débito", tipo="debito"))
    cartao_id = CartaoService(conn).criar(
        nome="Nubank", limite=500000, dia_fechamento=25, dia_vencimento=5, conta_id=conta_id
    )

    CompraCartaoService(conn).registrar_compra(
        cartao_id=cartao_id,
        categoria_id=categoria_id,
        descricao="Notebook",
        data_compra="2026-08-10",
        valor_total=90000,
        numero_parcelas=3,
    )
    FaturaCartaoService(conn).pagar_fatura(cartao_id, 8, 2026)

    assert total_despesas_futuras_cartoes(conn) == 60000
