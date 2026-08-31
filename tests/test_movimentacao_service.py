import pytest

from app.models.categoria import Categoria
from app.models.conta import Conta
from app.models.forma_pagamento import FormaPagamento
from app.models.movimentacao import Movimentacao
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.conta_repository import ContaRepository
from app.repositories.forma_pagamento_repository import FormaPagamentoRepository
from app.services.exceptions import ErroValidacao
from app.services.movimentacao_service import MovimentacaoService


def _preparar(conn):
    categoria_entrada = CategoriaRepository(conn).create(Categoria(nome="Salário", tipo="entrada"))
    categoria_saida = CategoriaRepository(conn).create(Categoria(nome="Supermercado", tipo="saida"))
    conta_id = ContaRepository(conn).create(Conta(nome="Carteira", tipo="dinheiro"))
    forma_pagamento_id = FormaPagamentoRepository(conn).create(FormaPagamento(nome="Dinheiro", tipo="dinheiro"))
    return categoria_entrada, categoria_saida, conta_id, forma_pagamento_id


def test_registrar_movimentacao_valida(conn):
    categoria_entrada, _, conta_id, forma_pagamento_id = _preparar(conn)
    service = MovimentacaoService(conn)

    mov_id = service.registrar(
        data="2026-08-01",
        tipo="entrada",
        descricao="Salário",
        valor=100000,
        categoria_id=categoria_entrada,
        conta_id=conta_id,
        forma_pagamento_id=forma_pagamento_id,
    )

    mov = service.repo.get_by_id(mov_id)
    assert mov.valor == 100000


def test_valor_zero_ou_negativo_gera_erro(conn):
    categoria_entrada, _, conta_id, forma_pagamento_id = _preparar(conn)
    service = MovimentacaoService(conn)

    with pytest.raises(ErroValidacao):
        service.registrar(
            data="2026-08-01",
            tipo="entrada",
            descricao="Salário",
            valor=0,
            categoria_id=categoria_entrada,
            conta_id=conta_id,
            forma_pagamento_id=forma_pagamento_id,
        )


def test_categoria_de_tipo_incompativel_gera_erro(conn):
    _, categoria_saida, conta_id, forma_pagamento_id = _preparar(conn)
    service = MovimentacaoService(conn)

    with pytest.raises(ErroValidacao):
        service.registrar(
            data="2026-08-01",
            tipo="entrada",
            descricao="Salário",
            valor=1000,
            categoria_id=categoria_saida,
            conta_id=conta_id,
            forma_pagamento_id=forma_pagamento_id,
        )


def test_data_invalida_gera_erro(conn):
    categoria_entrada, _, conta_id, forma_pagamento_id = _preparar(conn)
    service = MovimentacaoService(conn)

    with pytest.raises(ErroValidacao):
        service.registrar(
            data="01/08/2026",
            tipo="entrada",
            descricao="Salário",
            valor=1000,
            categoria_id=categoria_entrada,
            conta_id=conta_id,
            forma_pagamento_id=forma_pagamento_id,
        )


def test_categoria_inativa_gera_erro(conn):
    categoria_entrada, _, conta_id, forma_pagamento_id = _preparar(conn)
    CategoriaRepository(conn).desativar(categoria_entrada)
    service = MovimentacaoService(conn)

    with pytest.raises(ErroValidacao):
        service.registrar(
            data="2026-08-01",
            tipo="entrada",
            descricao="Salário",
            valor=1000,
            categoria_id=categoria_entrada,
            conta_id=conta_id,
            forma_pagamento_id=forma_pagamento_id,
        )


def test_sugerir_categoria_por_descricao(conn):
    _, categoria_saida, _, _ = _preparar(conn)
    service = MovimentacaoService(conn)

    categoria_id = service.sugerir_categoria_por_descricao("Compra no Carrefour")
    assert categoria_id == categoria_saida


def test_excluir_movimentacao_inexistente_gera_erro(conn):
    service = MovimentacaoService(conn)
    with pytest.raises(ErroValidacao):
        service.excluir(999)


def test_atualizar_movimentacao_altera_valor_e_descricao(conn):
    categoria_entrada, _, conta_id, forma_pagamento_id = _preparar(conn)
    service = MovimentacaoService(conn)

    mov_id = service.registrar(
        data="2026-08-01",
        tipo="entrada",
        descricao="Salário",
        valor=100000,
        categoria_id=categoria_entrada,
        conta_id=conta_id,
        forma_pagamento_id=forma_pagamento_id,
    )

    movimentacao = service.repo.get_by_id(mov_id)
    movimentacao.valor = 150000
    movimentacao.descricao = "Salário corrigido"
    service.atualizar(movimentacao)

    atualizada = service.repo.get_by_id(mov_id)
    assert atualizada.valor == 150000
    assert atualizada.descricao == "Salário corrigido"


def test_atualizar_movimentacao_inexistente_gera_erro(conn):
    categoria_entrada, _, conta_id, forma_pagamento_id = _preparar(conn)
    service = MovimentacaoService(conn)

    movimentacao = Movimentacao(
        id=999,
        data="2026-08-01",
        tipo="entrada",
        descricao="Fantasma",
        valor=1000,
        categoria_id=categoria_entrada,
        conta_id=conta_id,
        forma_pagamento_id=forma_pagamento_id,
    )
    with pytest.raises(ErroValidacao):
        service.atualizar(movimentacao)


def test_excluir_movimentacao_existente_remove_do_historico(conn):
    categoria_entrada, _, conta_id, forma_pagamento_id = _preparar(conn)
    service = MovimentacaoService(conn)

    mov_id = service.registrar(
        data="2026-08-01",
        tipo="entrada",
        descricao="Salário",
        valor=100000,
        categoria_id=categoria_entrada,
        conta_id=conta_id,
        forma_pagamento_id=forma_pagamento_id,
    )

    service.excluir(mov_id)

    assert service.repo.get_by_id(mov_id) is None
    assert service.listar() == []
