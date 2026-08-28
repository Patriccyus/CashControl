from datetime import date

from app.analytics.dashboard_analytics import (
    calcular_resumo_dashboard,
    entradas_saidas_por_mes,
    gastos_por_categoria_do_mes,
)
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
    categoria_saida = CategoriaRepository(conn).create(Categoria(nome="Supermercado", tipo="saida"))
    conta_id = ContaRepository(conn).create(Conta(nome="Carteira", tipo="dinheiro", saldo_inicial=10000))
    forma_pagamento_id = FormaPagamentoRepository(conn).create(FormaPagamento(nome="Dinheiro", tipo="dinheiro"))
    return categoria_entrada, categoria_saida, conta_id, forma_pagamento_id


def _registrar(conn, tipo, categoria_id, conta_id, forma_pagamento_id, data, valor, status="pago"):
    MovimentacaoRepository(conn).create(
        Movimentacao(
            data=data,
            tipo=tipo,
            descricao="teste",
            valor=valor,
            categoria_id=categoria_id,
            conta_id=conta_id,
            forma_pagamento_id=forma_pagamento_id,
            status=status,
        )
    )


def test_resumo_dashboard_calcula_saldo_e_totais_do_mes(conn):
    categoria_entrada, categoria_saida, conta_id, forma_pagamento_id = _preparar(conn)
    referencia = date(2026, 8, 15)

    _registrar(conn, "entrada", categoria_entrada, conta_id, forma_pagamento_id, "2026-08-01", 100000)
    _registrar(conn, "saida", categoria_saida, conta_id, forma_pagamento_id, "2026-08-05", 30000)
    _registrar(conn, "saida", categoria_saida, conta_id, forma_pagamento_id, "2026-07-01", 5000)
    _registrar(
        conn, "saida", categoria_saida, conta_id, forma_pagamento_id, "2026-08-10", 2000, status="pendente"
    )

    resumo = calcular_resumo_dashboard(conn, referencia)

    assert resumo.saldo_atual == 10000 + 100000 - 30000 - 5000
    assert resumo.entradas_mes == 100000
    assert resumo.saidas_mes == 30000
    assert resumo.resultado_mes == 70000
    assert resumo.quantidade_pendentes == 1
    assert resumo.valor_pendente == 2000
    assert resumo.percentual_renda_comprometida == 30.0


def test_entradas_saidas_por_mes_preenche_todos_os_periodos(conn):
    categoria_entrada, categoria_saida, conta_id, forma_pagamento_id = _preparar(conn)
    _registrar(conn, "entrada", categoria_entrada, conta_id, forma_pagamento_id, "2026-08-01", 50000)

    serie = entradas_saidas_por_mes(conn, meses=3, referencia=date(2026, 8, 15))

    assert [periodo for periodo, _, _ in serie] == ["2026-06", "2026-07", "2026-08"]
    assert serie[-1] == ("2026-08", 50000, 0)
    assert serie[0] == ("2026-06", 0, 0)


def test_gastos_por_categoria_do_mes_ordena_do_maior_para_o_menor(conn):
    categoria_entrada, categoria_saida, conta_id, forma_pagamento_id = _preparar(conn)
    outra_categoria = CategoriaRepository(conn).create(Categoria(nome="Lazer", tipo="saida"))

    _registrar(conn, "saida", categoria_saida, conta_id, forma_pagamento_id, "2026-08-05", 10000)
    _registrar(conn, "saida", outra_categoria, conta_id, forma_pagamento_id, "2026-08-06", 30000)

    resultado = gastos_por_categoria_do_mes(conn, referencia=date(2026, 8, 15))

    assert resultado[0] == ("Lazer", 30000)
    assert resultado[1] == ("Supermercado", 10000)
