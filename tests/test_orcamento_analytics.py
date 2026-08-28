from app.analytics.orcamento_analytics import calcular_consumo_orcamento
from app.models.categoria import Categoria
from app.models.conta import Conta
from app.models.forma_pagamento import FormaPagamento
from app.models.movimentacao import Movimentacao
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.conta_repository import ContaRepository
from app.repositories.forma_pagamento_repository import FormaPagamentoRepository
from app.repositories.movimentacao_repository import MovimentacaoRepository
from app.services.orcamento_service import OrcamentoService


def _registrar_saida(conn, categoria_id, conta_id, forma_pagamento_id, data, valor):
    MovimentacaoRepository(conn).create(
        Movimentacao(
            data=data,
            tipo="saida",
            descricao="teste",
            valor=valor,
            categoria_id=categoria_id,
            conta_id=conta_id,
            forma_pagamento_id=forma_pagamento_id,
        )
    )


def test_consumo_orcamento_exemplo_da_especificacao(conn):
    categoria_repo = CategoriaRepository(conn)
    supermercado_id = categoria_repo.create(Categoria(nome="Supermercado", tipo="saida"))
    lazer_id = categoria_repo.create(Categoria(nome="Lazer", tipo="saida"))
    saude_id = categoria_repo.create(Categoria(nome="Saúde", tipo="saida"))

    conta_id = ContaRepository(conn).create(Conta(nome="Carteira", tipo="dinheiro"))
    forma_pagamento_id = FormaPagamentoRepository(conn).create(FormaPagamento(nome="Dinheiro", tipo="dinheiro"))

    orcamento_service = OrcamentoService(conn)
    orcamento_service.definir_limite(supermercado_id, 8, 2026, 120000)
    orcamento_service.definir_limite(lazer_id, 8, 2026, 40000)
    orcamento_service.definir_limite(saude_id, 8, 2026, 50000)

    _registrar_saida(conn, supermercado_id, conta_id, forma_pagamento_id, "2026-08-05", 95000)
    _registrar_saida(conn, lazer_id, conta_id, forma_pagamento_id, "2026-08-10", 52000)
    _registrar_saida(conn, saude_id, conta_id, forma_pagamento_id, "2026-08-15", 18000)

    consumo = {c.categoria_nome: c for c in calcular_consumo_orcamento(conn, 8, 2026)}

    assert round(consumo["Supermercado"].percentual) == 79
    assert consumo["Supermercado"].situacao == "dentro"

    assert round(consumo["Lazer"].percentual) == 130
    assert consumo["Lazer"].situacao == "ultrapassado"

    assert round(consumo["Saúde"].percentual) == 36
    assert consumo["Saúde"].situacao == "dentro"


def test_movimentacao_fora_do_mes_nao_conta(conn):
    categoria_id = CategoriaRepository(conn).create(Categoria(nome="Lazer", tipo="saida"))
    conta_id = ContaRepository(conn).create(Conta(nome="Carteira", tipo="dinheiro"))
    forma_pagamento_id = FormaPagamentoRepository(conn).create(FormaPagamento(nome="Dinheiro", tipo="dinheiro"))

    OrcamentoService(conn).definir_limite(categoria_id, 8, 2026, 40000)
    _registrar_saida(conn, categoria_id, conta_id, forma_pagamento_id, "2026-07-31", 10000)
    _registrar_saida(conn, categoria_id, conta_id, forma_pagamento_id, "2026-09-01", 10000)

    consumo = calcular_consumo_orcamento(conn, 8, 2026)
    assert consumo[0].gasto == 0
