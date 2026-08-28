from app.models.categoria import Categoria
from app.models.conta import Conta
from app.models.forma_pagamento import FormaPagamento
from app.models.movimentacao import Movimentacao
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.conta_repository import ContaRepository
from app.repositories.forma_pagamento_repository import FormaPagamentoRepository
from app.repositories.movimentacao_repository import (
    FiltroMovimentacao,
    MovimentacaoRepository,
)


def _preparar_dependencias(conn):
    categoria_id = CategoriaRepository(conn).create(Categoria(nome="Salário", tipo="entrada"))
    conta_id = ContaRepository(conn).create(Conta(nome="Carteira", tipo="dinheiro"))
    forma_pagamento_id = FormaPagamentoRepository(conn).create(
        FormaPagamento(nome="Dinheiro", tipo="dinheiro")
    )
    return categoria_id, conta_id, forma_pagamento_id


def test_criar_e_buscar_movimentacao(conn):
    categoria_id, conta_id, forma_pagamento_id = _preparar_dependencias(conn)
    repo = MovimentacaoRepository(conn)

    mov_id = repo.create(
        Movimentacao(
            data="2026-08-01",
            tipo="entrada",
            descricao="Salário de agosto",
            valor=100000,
            categoria_id=categoria_id,
            conta_id=conta_id,
            forma_pagamento_id=forma_pagamento_id,
        )
    )

    mov = repo.get_by_id(mov_id)
    assert mov is not None
    assert mov.descricao == "Salário de agosto"
    assert mov.valor == 100000


def test_resultado_mensal_entrada_1000_saida_300(conn):
    categoria_id, conta_id, forma_pagamento_id = _preparar_dependencias(conn)
    repo = MovimentacaoRepository(conn)

    repo.create(
        Movimentacao(
            data="2026-08-01",
            tipo="entrada",
            descricao="Entrada",
            valor=100000,
            categoria_id=categoria_id,
            conta_id=conta_id,
            forma_pagamento_id=forma_pagamento_id,
        )
    )
    repo.create(
        Movimentacao(
            data="2026-08-02",
            tipo="saida",
            descricao="Saída",
            valor=30000,
            categoria_id=categoria_id,
            conta_id=conta_id,
            forma_pagamento_id=forma_pagamento_id,
        )
    )

    movimentacoes = repo.list()
    total_entradas = sum(m.valor for m in movimentacoes if m.tipo == "entrada")
    total_saidas = sum(m.valor for m in movimentacoes if m.tipo == "saida")
    resultado = total_entradas - total_saidas

    assert resultado == 70000


def test_filtro_por_tipo(conn):
    categoria_id, conta_id, forma_pagamento_id = _preparar_dependencias(conn)
    repo = MovimentacaoRepository(conn)

    repo.create(
        Movimentacao(
            data="2026-08-01",
            tipo="entrada",
            descricao="Entrada",
            valor=100000,
            categoria_id=categoria_id,
            conta_id=conta_id,
            forma_pagamento_id=forma_pagamento_id,
        )
    )
    repo.create(
        Movimentacao(
            data="2026-08-02",
            tipo="saida",
            descricao="Saída",
            valor=30000,
            categoria_id=categoria_id,
            conta_id=conta_id,
            forma_pagamento_id=forma_pagamento_id,
        )
    )

    apenas_saidas = repo.list(FiltroMovimentacao(tipo="saida"))
    assert len(apenas_saidas) == 1
    assert apenas_saidas[0].tipo == "saida"
