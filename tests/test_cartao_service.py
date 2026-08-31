import pytest

from app.models.conta import Conta
from app.repositories.conta_repository import ContaRepository
from app.services.cartao_service import CartaoService
from app.services.exceptions import ErroValidacao


def _preparar_conta(conn):
    return ContaRepository(conn).create(Conta(nome="Conta corrente", tipo="conta_corrente"))


def test_criar_cartao_valido(conn):
    conta_id = _preparar_conta(conn)
    service = CartaoService(conn)

    cartao_id = service.criar(
        nome="Nubank", limite=500000, dia_fechamento=25, dia_vencimento=5, conta_id=conta_id
    )

    cartoes = service.listar()
    assert len(cartoes) == 1
    assert cartoes[0].id == cartao_id
    assert cartoes[0].limite == 500000


def test_dia_fechamento_invalido_gera_erro(conn):
    conta_id = _preparar_conta(conn)
    service = CartaoService(conn)

    with pytest.raises(ErroValidacao):
        service.criar(nome="Nubank", limite=500000, dia_fechamento=31, dia_vencimento=5, conta_id=conta_id)


def test_desativar_cartao(conn):
    conta_id = _preparar_conta(conn)
    service = CartaoService(conn)
    cartao_id = service.criar(
        nome="Nubank", limite=500000, dia_fechamento=25, dia_vencimento=5, conta_id=conta_id
    )

    service.desativar(cartao_id)

    assert service.listar() == []
    assert service.listar(apenas_ativos=False)[0].ativo is False
