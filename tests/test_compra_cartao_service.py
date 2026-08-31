import pytest

from app.models.categoria import Categoria
from app.models.conta import Conta
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.conta_repository import ContaRepository
from app.services.cartao_service import CartaoService
from app.services.compra_cartao_service import CompraCartaoService
from app.services.exceptions import ErroValidacao


def _preparar(conn, limite=500000):
    conta_id = ContaRepository(conn).create(Conta(nome="Conta corrente", tipo="conta_corrente"))
    categoria_id = CategoriaRepository(conn).create(Categoria(nome="Lazer", tipo="saida"))
    cartao_id = CartaoService(conn).criar(
        nome="Nubank", limite=limite, dia_fechamento=25, dia_vencimento=5, conta_id=conta_id
    )
    return cartao_id, categoria_id, conta_id


def test_compra_a_vista_cai_na_fatura_correta(conn):
    cartao_id, categoria_id, _ = _preparar(conn)
    service = CompraCartaoService(conn)

    service.registrar_compra(
        cartao_id=cartao_id,
        categoria_id=categoria_id,
        descricao="Cinema",
        data_compra="2026-08-10",
        valor_total=5000,
    )

    compras = service.listar_compras(cartao_id)
    assert len(compras) == 1
    assert len(compras[0].parcelas) == 1
    assert compras[0].parcelas[0].fatura_mes == 8
    assert compras[0].parcelas[0].fatura_ano == 2026
    assert compras[0].parcelas[0].valor == 5000


def test_compra_apos_fechamento_cai_na_fatura_seguinte(conn):
    cartao_id, categoria_id, _ = _preparar(conn)
    service = CompraCartaoService(conn)

    service.registrar_compra(
        cartao_id=cartao_id,
        categoria_id=categoria_id,
        descricao="Presente",
        data_compra="2026-08-25",
        valor_total=3000,
    )

    compra = service.listar_compras(cartao_id)[0]
    assert (compra.parcelas[0].fatura_mes, compra.parcelas[0].fatura_ano) == (9, 2026)


def test_compra_parcelada_distribui_parcelas_por_meses_seguintes(conn):
    cartao_id, categoria_id, _ = _preparar(conn)
    service = CompraCartaoService(conn)

    service.registrar_compra(
        cartao_id=cartao_id,
        categoria_id=categoria_id,
        descricao="Notebook",
        data_compra="2026-08-10",
        valor_total=100000,
        numero_parcelas=3,
    )

    compra = service.listar_compras(cartao_id)[0]
    periodos = [(p.fatura_mes, p.fatura_ano) for p in compra.parcelas]
    valores = [p.valor for p in compra.parcelas]

    assert periodos == [(8, 2026), (9, 2026), (10, 2026)]
    assert sum(valores) == 100000
    assert valores == [33334, 33333, 33333]


def test_compra_acima_do_limite_gera_erro(conn):
    cartao_id, categoria_id, _ = _preparar(conn, limite=50000)
    service = CompraCartaoService(conn)

    with pytest.raises(ErroValidacao):
        service.registrar_compra(
            cartao_id=cartao_id,
            categoria_id=categoria_id,
            descricao="TV",
            data_compra="2026-08-10",
            valor_total=60000,
        )


def test_limite_considera_compras_ja_registradas(conn):
    cartao_id, categoria_id, _ = _preparar(conn, limite=50000)
    service = CompraCartaoService(conn)

    service.registrar_compra(
        cartao_id=cartao_id,
        categoria_id=categoria_id,
        descricao="Compra 1",
        data_compra="2026-08-10",
        valor_total=40000,
    )

    with pytest.raises(ErroValidacao):
        service.registrar_compra(
            cartao_id=cartao_id,
            categoria_id=categoria_id,
            descricao="Compra 2",
            data_compra="2026-08-11",
            valor_total=20000,
        )

    service.registrar_compra(
        cartao_id=cartao_id,
        categoria_id=categoria_id,
        descricao="Compra 3",
        data_compra="2026-08-11",
        valor_total=10000,
    )
    assert len(service.listar_compras(cartao_id)) == 2


def test_categoria_de_entrada_gera_erro(conn):
    cartao_id, _, _ = _preparar(conn)
    categoria_entrada_id = CategoriaRepository(conn).create(Categoria(nome="Salário", tipo="entrada"))
    service = CompraCartaoService(conn)

    with pytest.raises(ErroValidacao):
        service.registrar_compra(
            cartao_id=cartao_id,
            categoria_id=categoria_entrada_id,
            descricao="Erro",
            data_compra="2026-08-10",
            valor_total=1000,
        )


def test_excluir_compra_sem_fatura_paga(conn):
    cartao_id, categoria_id, _ = _preparar(conn)
    service = CompraCartaoService(conn)

    compra_id = service.registrar_compra(
        cartao_id=cartao_id,
        categoria_id=categoria_id,
        descricao="Cinema",
        data_compra="2026-08-10",
        valor_total=5000,
    )

    service.excluir_compra(compra_id)
    assert service.listar_compras(cartao_id) == []
