from app.analytics.insights import gerar_insights
from app.models.categoria import Categoria
from app.models.conta import Conta
from app.models.forma_pagamento import FormaPagamento
from app.models.movimentacao import Movimentacao
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.conta_repository import ContaRepository
from app.repositories.forma_pagamento_repository import FormaPagamentoRepository
from app.repositories.movimentacao_repository import MovimentacaoRepository
from app.services.orcamento_service import OrcamentoService


def _preparar_base(conn):
    categoria_entrada = CategoriaRepository(conn).create(Categoria(nome="Salário", tipo="entrada"))
    conta_id = ContaRepository(conn).create(Conta(nome="Carteira", tipo="dinheiro"))
    forma_pagamento_id = FormaPagamentoRepository(conn).create(FormaPagamento(nome="Dinheiro", tipo="dinheiro"))
    return categoria_entrada, conta_id, forma_pagamento_id


def _registrar(conn, tipo, categoria_id, conta_id, forma_pagamento_id, data, valor):
    MovimentacaoRepository(conn).create(
        Movimentacao(
            data=data,
            tipo=tipo,
            descricao="teste",
            valor=valor,
            categoria_id=categoria_id,
            conta_id=conta_id,
            forma_pagamento_id=forma_pagamento_id,
        )
    )


def test_insight_orcamento_estourado(conn):
    categoria_entrada, conta_id, forma_pagamento_id = _preparar_base(conn)
    lazer_id = CategoriaRepository(conn).create(Categoria(nome="Lazer", tipo="saida"))

    OrcamentoService(conn).definir_limite(lazer_id, 8, 2026, 40000)
    _registrar(conn, "saida", lazer_id, conta_id, forma_pagamento_id, "2026-08-10", 52000)

    insights = gerar_insights(conn, 8, 2026)
    assert any("ultrapassou o limite planejado em Lazer" in texto for texto in insights)


def test_insight_crescimento_categoria(conn):
    categoria_entrada, conta_id, forma_pagamento_id = _preparar_base(conn)
    lazer_id = CategoriaRepository(conn).create(Categoria(nome="Lazer", tipo="saida"))

    for mes in ("2026-05", "2026-06", "2026-07"):
        _registrar(conn, "saida", lazer_id, conta_id, forma_pagamento_id, f"{mes}-10", 10000)
    _registrar(conn, "saida", lazer_id, conta_id, forma_pagamento_id, "2026-08-10", 15000)

    insights = gerar_insights(conn, 8, 2026)
    assert any("Lazer aumentaram 50%" in texto for texto in insights)


def test_insight_categoria_representativa(conn):
    categoria_entrada, conta_id, forma_pagamento_id = _preparar_base(conn)
    supermercado_id = CategoriaRepository(conn).create(Categoria(nome="Supermercado", tipo="saida"))
    transporte_id = CategoriaRepository(conn).create(Categoria(nome="Transporte", tipo="saida"))

    _registrar(conn, "saida", supermercado_id, conta_id, forma_pagamento_id, "2026-08-05", 80000)
    _registrar(conn, "saida", transporte_id, conta_id, forma_pagamento_id, "2026-08-06", 20000)

    insights = gerar_insights(conn, 8, 2026)
    assert any("Supermercado representa 80%" in texto for texto in insights)


def test_insight_despesas_vs_receitas(conn):
    categoria_entrada, conta_id, forma_pagamento_id = _preparar_base(conn)
    lazer_id = CategoriaRepository(conn).create(Categoria(nome="Lazer", tipo="saida"))

    _registrar(conn, "entrada", categoria_entrada, conta_id, forma_pagamento_id, "2026-07-01", 100000)
    _registrar(conn, "saida", lazer_id, conta_id, forma_pagamento_id, "2026-07-05", 30000)

    _registrar(conn, "entrada", categoria_entrada, conta_id, forma_pagamento_id, "2026-08-01", 105000)
    _registrar(conn, "saida", lazer_id, conta_id, forma_pagamento_id, "2026-08-05", 60000)

    insights = gerar_insights(conn, 8, 2026)
    assert any("renda aumentou, mas suas despesas cresceram" in texto for texto in insights)


def test_sem_dados_nao_gera_insights(conn):
    assert gerar_insights(conn, 8, 2026) == []
