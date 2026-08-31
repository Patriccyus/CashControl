from datetime import date

import pytest

from app.analytics.fatura_cartao import calcular_fatura
from app.models.categoria import Categoria
from app.models.conta import Conta
from app.models.forma_pagamento import FormaPagamento
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.conta_repository import ContaRepository
from app.repositories.forma_pagamento_repository import FormaPagamentoRepository
from app.repositories.movimentacao_repository import MovimentacaoRepository
from app.services.cartao_service import CartaoService
from app.services.compra_cartao_service import CompraCartaoService
from app.services.exceptions import ErroValidacao
from app.services.fatura_cartao_service import FaturaCartaoService


def _preparar(conn, limite=500000):
    conta_id = ContaRepository(conn).create(Conta(nome="Conta corrente", tipo="conta_corrente"))
    CategoriaRepository(conn).create(Categoria(nome="Cartão de crédito", tipo="saida"))
    categoria_id = CategoriaRepository(conn).create(Categoria(nome="Lazer", tipo="saida"))
    FormaPagamentoRepository(conn).create(FormaPagamento(nome="Débito", tipo="debito"))
    cartao_id = CartaoService(conn).criar(
        nome="Nubank", limite=limite, dia_fechamento=25, dia_vencimento=5, conta_id=conta_id
    )
    return cartao_id, categoria_id, conta_id


def test_calcular_fatura_soma_itens_e_status_aberta(conn):
    cartao_id, categoria_id, _ = _preparar(conn)
    CompraCartaoService(conn).registrar_compra(
        cartao_id=cartao_id,
        categoria_id=categoria_id,
        descricao="Cinema",
        data_compra="2026-08-10",
        valor_total=5000,
    )

    fatura = FaturaCartaoService(conn).calcular(cartao_id, 8, 2026, referencia=date(2026, 8, 15))

    assert fatura.valor_total == 5000
    assert len(fatura.itens) == 1
    assert fatura.itens[0].descricao == "Cinema"
    assert fatura.data_fechamento == "2026-08-25"
    assert fatura.data_vencimento == "2026-09-05"
    assert fatura.status == "aberta"


def test_status_fechada_apos_data_de_fechamento(conn):
    cartao_id, categoria_id, _ = _preparar(conn)
    CompraCartaoService(conn).registrar_compra(
        cartao_id=cartao_id,
        categoria_id=categoria_id,
        descricao="Cinema",
        data_compra="2026-08-10",
        valor_total=5000,
    )

    fatura = calcular_fatura(conn, cartao_id, 8, 2026, referencia=date(2026, 8, 26))
    assert fatura.status == "fechada"


def test_pagar_fatura_gera_movimentacao_e_marca_como_paga(conn):
    cartao_id, categoria_id, conta_id = _preparar(conn)
    CompraCartaoService(conn).registrar_compra(
        cartao_id=cartao_id,
        categoria_id=categoria_id,
        descricao="Cinema",
        data_compra="2026-08-10",
        valor_total=5000,
    )

    FaturaCartaoService(conn).pagar_fatura(cartao_id, 8, 2026, data_pagamento="2026-09-05")

    movimentacoes = MovimentacaoRepository(conn).list()
    assert len(movimentacoes) == 1
    assert movimentacoes[0].valor == 5000
    assert movimentacoes[0].conta_id == conta_id
    assert movimentacoes[0].status == "pago"

    fatura = FaturaCartaoService(conn).calcular(cartao_id, 8, 2026)
    assert fatura.status == "paga"


def test_pagar_fatura_duas_vezes_gera_erro(conn):
    cartao_id, categoria_id, _ = _preparar(conn)
    CompraCartaoService(conn).registrar_compra(
        cartao_id=cartao_id,
        categoria_id=categoria_id,
        descricao="Cinema",
        data_compra="2026-08-10",
        valor_total=5000,
    )
    service = FaturaCartaoService(conn)
    service.pagar_fatura(cartao_id, 8, 2026)

    with pytest.raises(ErroValidacao):
        service.pagar_fatura(cartao_id, 8, 2026)


def test_pagar_fatura_sem_parcelas_gera_erro(conn):
    cartao_id, _, _ = _preparar(conn)
    with pytest.raises(ErroValidacao):
        FaturaCartaoService(conn).pagar_fatura(cartao_id, 8, 2026)


def test_pagamento_libera_limite_para_novas_compras(conn):
    cartao_id, categoria_id, _ = _preparar(conn, limite=50000)
    compras = CompraCartaoService(conn)
    compras.registrar_compra(
        cartao_id=cartao_id,
        categoria_id=categoria_id,
        descricao="Compra 1",
        data_compra="2026-08-10",
        valor_total=50000,
    )

    with pytest.raises(ErroValidacao):
        compras.registrar_compra(
            cartao_id=cartao_id,
            categoria_id=categoria_id,
            descricao="Compra 2",
            data_compra="2026-08-11",
            valor_total=1000,
        )

    FaturaCartaoService(conn).pagar_fatura(cartao_id, 8, 2026)

    compras.registrar_compra(
        cartao_id=cartao_id,
        categoria_id=categoria_id,
        descricao="Compra 2",
        data_compra="2026-08-11",
        valor_total=1000,
    )
    assert len(compras.listar_compras(cartao_id)) == 2


def test_projecao_futura_retorna_periodos_em_aberto_ordenados(conn):
    cartao_id, categoria_id, _ = _preparar(conn)
    CompraCartaoService(conn).registrar_compra(
        cartao_id=cartao_id,
        categoria_id=categoria_id,
        descricao="Notebook",
        data_compra="2026-08-10",
        valor_total=90000,
        numero_parcelas=3,
    )

    projecao = FaturaCartaoService(conn).projecao(cartao_id, meses=6)

    periodos = [(f.mes, f.ano) for f in projecao]
    assert periodos == [(8, 2026), (9, 2026), (10, 2026)]
    assert all(f.valor_total == 30000 for f in projecao)
