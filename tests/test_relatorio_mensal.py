from app.analytics.relatorio_mensal import gerar_relatorio_mensal
from app.models.categoria import Categoria
from app.models.conta import Conta
from app.models.forma_pagamento import FormaPagamento
from app.models.movimentacao import Movimentacao
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.conta_repository import ContaRepository
from app.repositories.forma_pagamento_repository import FormaPagamentoRepository
from app.repositories.movimentacao_repository import MovimentacaoRepository


def _preparar(conn):
    categoria_entrada = CategoriaRepository(conn).create(Categoria(nome="Salário", tipo="entrada"))
    supermercado_id = CategoriaRepository(conn).create(Categoria(nome="Supermercado", tipo="saida"))
    lazer_id = CategoriaRepository(conn).create(Categoria(nome="Lazer", tipo="saida"))
    conta_id = ContaRepository(conn).create(Conta(nome="Carteira", tipo="dinheiro"))
    forma_pagamento_id = FormaPagamentoRepository(conn).create(FormaPagamento(nome="Dinheiro", tipo="dinheiro"))
    return categoria_entrada, supermercado_id, lazer_id, conta_id, forma_pagamento_id


def _registrar(conn, tipo, categoria_id, conta_id, forma_pagamento_id, data, valor, descricao="teste"):
    MovimentacaoRepository(conn).create(
        Movimentacao(
            data=data,
            tipo=tipo,
            descricao=descricao,
            valor=valor,
            categoria_id=categoria_id,
            conta_id=conta_id,
            forma_pagamento_id=forma_pagamento_id,
        )
    )


def test_resumo_do_relatorio(conn):
    categoria_entrada, supermercado_id, lazer_id, conta_id, forma_pagamento_id = _preparar(conn)

    _registrar(conn, "entrada", categoria_entrada, conta_id, forma_pagamento_id, "2026-08-01", 500000)
    _registrar(conn, "saida", supermercado_id, conta_id, forma_pagamento_id, "2026-08-05", 95000, "Compra no Carrefour")
    _registrar(conn, "saida", lazer_id, conta_id, forma_pagamento_id, "2026-08-10", 52000, "Cinema")

    relatorio = gerar_relatorio_mensal(conn, 8, 2026)

    assert relatorio.resumo.total_entradas == 500000
    assert relatorio.resumo.total_saidas == 147000
    assert relatorio.resumo.resultado == 353000
    assert round(relatorio.resumo.taxa_economia) == 71
    assert relatorio.resumo.maior_categoria_gasto.nome == "Supermercado"
    assert relatorio.resumo.maior_despesa_individual.descricao == "Compra no Carrefour"

    nomes_categorias = [item.nome for item in relatorio.gastos_por_categoria]
    assert nomes_categorias == ["Supermercado", "Lazer"]


def test_comparacao_historica(conn):
    categoria_entrada, supermercado_id, lazer_id, conta_id, forma_pagamento_id = _preparar(conn)

    _registrar(conn, "saida", supermercado_id, conta_id, forma_pagamento_id, "2026-07-05", 10000)
    _registrar(conn, "saida", supermercado_id, conta_id, forma_pagamento_id, "2026-08-05", 20000)

    relatorio = gerar_relatorio_mensal(conn, 8, 2026)

    assert relatorio.comparacao_historica.mes_anterior.saidas == 10000
    assert relatorio.comparacao_historica.media_3_meses.saidas == round(10000 / 3)


def test_relatorio_sem_movimentacoes(conn):
    relatorio = gerar_relatorio_mensal(conn, 8, 2026)

    assert relatorio.resumo.total_entradas == 0
    assert relatorio.resumo.taxa_economia == 0.0
    assert relatorio.gastos_por_categoria == []
    assert relatorio.resumo.maior_categoria_gasto.nome is None
    assert relatorio.insights == []
