import pytest

from app.models.categoria import Categoria
from app.repositories.categoria_repository import CategoriaRepository
from app.services.exceptions import ErroValidacao
from app.services.orcamento_service import OrcamentoService


def test_definir_limite_cria_orcamento(conn):
    categoria_id = CategoriaRepository(conn).create(Categoria(nome="Lazer", tipo="saida"))
    service = OrcamentoService(conn)

    orcamento_id = service.definir_limite(categoria_id, mes=8, ano=2026, limite=40000)
    orcamentos = service.listar_por_mes(8, 2026)

    assert len(orcamentos) == 1
    assert orcamentos[0].id == orcamento_id
    assert orcamentos[0].limite == 40000


def test_definir_limite_duas_vezes_atualiza_em_vez_de_duplicar(conn):
    categoria_id = CategoriaRepository(conn).create(Categoria(nome="Lazer", tipo="saida"))
    service = OrcamentoService(conn)

    service.definir_limite(categoria_id, mes=8, ano=2026, limite=40000)
    service.definir_limite(categoria_id, mes=8, ano=2026, limite=50000)

    orcamentos = service.listar_por_mes(8, 2026)
    assert len(orcamentos) == 1
    assert orcamentos[0].limite == 50000


def test_categoria_de_entrada_gera_erro(conn):
    categoria_id = CategoriaRepository(conn).create(Categoria(nome="Salário", tipo="entrada"))
    service = OrcamentoService(conn)

    with pytest.raises(ErroValidacao):
        service.definir_limite(categoria_id, mes=8, ano=2026, limite=1000)


def test_mes_invalido_gera_erro(conn):
    categoria_id = CategoriaRepository(conn).create(Categoria(nome="Lazer", tipo="saida"))
    service = OrcamentoService(conn)

    with pytest.raises(ErroValidacao):
        service.definir_limite(categoria_id, mes=13, ano=2026, limite=1000)
