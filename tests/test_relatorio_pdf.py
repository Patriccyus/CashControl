from pathlib import Path

from app.analytics.relatorio_mensal import gerar_relatorio_mensal
from app.models.categoria import Categoria
from app.models.conta import Conta
from app.models.forma_pagamento import FormaPagamento
from app.models.movimentacao import Movimentacao
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.conta_repository import ContaRepository
from app.repositories.forma_pagamento_repository import FormaPagamentoRepository
from app.repositories.movimentacao_repository import MovimentacaoRepository
from app.reports.relatorio_pdf import gerar_pdf_relatorio_mensal


def test_gerar_pdf_relatorio_mensal(conn, tmp_path):
    categoria_entrada = CategoriaRepository(conn).create(Categoria(nome="Salário", tipo="entrada"))
    supermercado_id = CategoriaRepository(conn).create(Categoria(nome="Supermercado", tipo="saida"))
    conta_id = ContaRepository(conn).create(Conta(nome="Carteira", tipo="dinheiro"))
    forma_pagamento_id = FormaPagamentoRepository(conn).create(FormaPagamento(nome="Dinheiro", tipo="dinheiro"))

    MovimentacaoRepository(conn).create(
        Movimentacao(
            data="2026-08-01",
            tipo="entrada",
            descricao="Salário",
            valor=500000,
            categoria_id=categoria_entrada,
            conta_id=conta_id,
            forma_pagamento_id=forma_pagamento_id,
        )
    )
    MovimentacaoRepository(conn).create(
        Movimentacao(
            data="2026-08-05",
            tipo="saida",
            descricao="Compra no Carrefour",
            valor=95000,
            categoria_id=supermercado_id,
            conta_id=conta_id,
            forma_pagamento_id=forma_pagamento_id,
        )
    )

    relatorio = gerar_relatorio_mensal(conn, 8, 2026)
    caminho_saida = tmp_path / "relatorio_2026_08.pdf"

    resultado = gerar_pdf_relatorio_mensal(relatorio, caminho_saida)

    assert resultado == caminho_saida
    assert caminho_saida.exists()
    assert caminho_saida.stat().st_size > 1000
    assert caminho_saida.read_bytes().startswith(b"%PDF")


def test_gerar_pdf_sem_dados_nao_falha(conn, tmp_path):
    relatorio = gerar_relatorio_mensal(conn, 8, 2026)
    caminho_saida = tmp_path / "relatorio_vazio.pdf"

    gerar_pdf_relatorio_mensal(relatorio, caminho_saida)

    assert caminho_saida.exists()
