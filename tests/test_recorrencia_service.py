from datetime import date

import pytest

from app.models.categoria import Categoria
from app.models.conta import Conta
from app.models.forma_pagamento import FormaPagamento
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.conta_repository import ContaRepository
from app.repositories.forma_pagamento_repository import FormaPagamentoRepository
from app.repositories.movimentacao_repository import MovimentacaoRepository
from app.services.exceptions import ErroValidacao
from app.services.recorrencia_service import RecorrenciaService


def _preparar(conn):
    categoria_id = CategoriaRepository(conn).create(Categoria(nome="Moradia", tipo="saida"))
    conta_id = ContaRepository(conn).create(Conta(nome="Carteira", tipo="dinheiro"))
    forma_pagamento_id = FormaPagamentoRepository(conn).create(FormaPagamento(nome="Débito", tipo="debito"))
    return categoria_id, conta_id, forma_pagamento_id


def test_criar_recorrencia_valida(conn):
    categoria_id, conta_id, forma_pagamento_id = _preparar(conn)
    service = RecorrenciaService(conn)

    recorrencia_id = service.criar(
        descricao="Aluguel",
        valor=150000,
        categoria_id=categoria_id,
        conta_id=conta_id,
        forma_pagamento_id=forma_pagamento_id,
        frequencia="mensal",
        data_inicio="2026-08-05",
    )

    recorrencias = service.listar()
    assert len(recorrencias) == 1
    assert recorrencias[0].id == recorrencia_id
    assert recorrencias[0].proxima_data == "2026-08-05"


def test_data_fim_anterior_ao_inicio_gera_erro(conn):
    categoria_id, conta_id, forma_pagamento_id = _preparar(conn)
    service = RecorrenciaService(conn)

    with pytest.raises(ErroValidacao):
        service.criar(
            descricao="Aluguel",
            valor=150000,
            categoria_id=categoria_id,
            conta_id=conta_id,
            forma_pagamento_id=forma_pagamento_id,
            frequencia="mensal",
            data_inicio="2026-08-05",
            data_fim="2026-07-01",
        )


def test_frequencia_invalida_gera_erro(conn):
    categoria_id, conta_id, forma_pagamento_id = _preparar(conn)
    service = RecorrenciaService(conn)

    with pytest.raises(ErroValidacao):
        service.criar(
            descricao="Aluguel",
            valor=150000,
            categoria_id=categoria_id,
            conta_id=conta_id,
            forma_pagamento_id=forma_pagamento_id,
            frequencia="quinzenal",
            data_inicio="2026-08-05",
        )


def test_gerar_lancamentos_pendentes_cria_movimentacao_e_avanca_data(conn):
    categoria_id, conta_id, forma_pagamento_id = _preparar(conn)
    service = RecorrenciaService(conn)

    service.criar(
        descricao="Aluguel",
        valor=150000,
        categoria_id=categoria_id,
        conta_id=conta_id,
        forma_pagamento_id=forma_pagamento_id,
        frequencia="mensal",
        data_inicio="2026-08-05",
    )

    total_gerado = service.gerar_lancamentos_pendentes(referencia=date(2026, 8, 10))

    assert total_gerado == 1
    movimentacoes = MovimentacaoRepository(conn).list()
    assert len(movimentacoes) == 1
    assert movimentacoes[0].descricao == "Aluguel"
    assert movimentacoes[0].status == "pendente"
    assert movimentacoes[0].data == "2026-08-05"

    recorrencia_atualizada = service.listar()[0]
    assert recorrencia_atualizada.proxima_data == "2026-09-05"


def test_gerar_lancamentos_pendentes_cobre_varios_periodos_atrasados(conn):
    categoria_id, conta_id, forma_pagamento_id = _preparar(conn)
    service = RecorrenciaService(conn)

    service.criar(
        descricao="Internet",
        valor=10000,
        categoria_id=categoria_id,
        conta_id=conta_id,
        forma_pagamento_id=forma_pagamento_id,
        frequencia="mensal",
        data_inicio="2026-06-10",
    )

    total_gerado = service.gerar_lancamentos_pendentes(referencia=date(2026, 8, 15))

    assert total_gerado == 3
    datas_geradas = sorted(m.data for m in MovimentacaoRepository(conn).list())
    assert datas_geradas == ["2026-06-10", "2026-07-10", "2026-08-10"]


def test_recorrencia_com_data_fim_e_desativada_apos_ultimo_lancamento(conn):
    categoria_id, conta_id, forma_pagamento_id = _preparar(conn)
    service = RecorrenciaService(conn)

    service.criar(
        descricao="Assinatura",
        valor=5000,
        categoria_id=categoria_id,
        conta_id=conta_id,
        forma_pagamento_id=forma_pagamento_id,
        frequencia="mensal",
        data_inicio="2026-08-01",
        data_fim="2026-08-31",
    )

    total_gerado = service.gerar_lancamentos_pendentes(referencia=date(2026, 10, 1))

    assert total_gerado == 1
    assert service.listar() == []
    assert service.listar(apenas_ativas=False)[0].ativo is False


def test_recorrencia_nao_gera_antes_da_data_de_inicio(conn):
    categoria_id, conta_id, forma_pagamento_id = _preparar(conn)
    service = RecorrenciaService(conn)

    service.criar(
        descricao="Academia",
        valor=8000,
        categoria_id=categoria_id,
        conta_id=conta_id,
        forma_pagamento_id=forma_pagamento_id,
        frequencia="mensal",
        data_inicio="2026-09-01",
    )

    total_gerado = service.gerar_lancamentos_pendentes(referencia=date(2026, 8, 15))

    assert total_gerado == 0
    assert MovimentacaoRepository(conn).list() == []
