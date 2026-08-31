import pytest

from app.database.connection import get_connection, init_db
from app.database.perfis_connection import get_perfis_connection
from app.models.categoria import Categoria
from app.repositories.categoria_repository import CategoriaRepository
from app.services.exceptions import ErroValidacao
from app.services.perfil_service import PerfilService


@pytest.fixture
def perfis_conn(tmp_path):
    conn = get_perfis_connection(tmp_path / "perfis.db")
    yield conn
    conn.close()


def _service(perfis_conn, tmp_path, legado_db_path=None):
    return PerfilService(
        perfis_conn,
        perfis_dir=tmp_path / "perfis",
        legado_db_path=legado_db_path or (tmp_path / "inexistente.db"),
    )


def test_criar_e_autenticar_perfil(perfis_conn, tmp_path):
    service = _service(perfis_conn, tmp_path)
    service.criar_perfil("Tiago", "1234")

    perfil = service.autenticar("Tiago", "1234")
    assert perfil.nome == "Tiago"


def test_autenticar_com_senha_errada_gera_erro(perfis_conn, tmp_path):
    service = _service(perfis_conn, tmp_path)
    service.criar_perfil("Tiago", "1234")

    with pytest.raises(ErroValidacao):
        service.autenticar("Tiago", "senha-errada")


def test_autenticar_perfil_inexistente_gera_erro(perfis_conn, tmp_path):
    service = _service(perfis_conn, tmp_path)
    with pytest.raises(ErroValidacao):
        service.autenticar("Ninguem", "1234")


def test_criar_perfil_duplicado_gera_erro(perfis_conn, tmp_path):
    service = _service(perfis_conn, tmp_path)
    service.criar_perfil("Tiago", "1234")

    with pytest.raises(ErroValidacao):
        service.criar_perfil("Tiago", "outra-senha")


def test_criar_perfil_sem_nome_ou_senha_gera_erro(perfis_conn, tmp_path):
    service = _service(perfis_conn, tmp_path)

    with pytest.raises(ErroValidacao):
        service.criar_perfil("  ", "1234")

    with pytest.raises(ErroValidacao):
        service.criar_perfil("Tiago", "")


def test_cada_perfil_tem_banco_proprio_e_isolado(perfis_conn, tmp_path):
    service = _service(perfis_conn, tmp_path)
    service.criar_perfil("Tiago", "1234")
    service.criar_perfil("Debora", "5678")

    caminho_tiago = service.caminho_banco_do_perfil("Tiago")
    caminho_debora = service.caminho_banco_do_perfil("Debora")
    assert caminho_tiago.exists()
    assert caminho_debora.exists()
    assert caminho_tiago != caminho_debora

    conn_tiago = get_connection(caminho_tiago)
    CategoriaRepository(conn_tiago).create(Categoria(nome="Só do Tiago", tipo="saida"))
    conn_tiago.close()

    conn_debora = get_connection(caminho_debora)
    nomes_debora = [c.nome for c in CategoriaRepository(conn_debora).list(apenas_ativas=False)]
    conn_debora.close()

    assert "Só do Tiago" not in nomes_debora


def test_primeiro_perfil_adota_banco_legado_se_existir(perfis_conn, tmp_path):
    legado = tmp_path / "legado.db"
    init_db(legado)
    conn_legado = get_connection(legado)
    CategoriaRepository(conn_legado).create(Categoria(nome="Dado antigo do Tiago", tipo="saida"))
    conn_legado.close()

    service = _service(perfis_conn, tmp_path, legado_db_path=legado)
    service.criar_perfil("Tiago", "1234")

    conn_perfil = get_connection(service.caminho_banco_do_perfil("Tiago"))
    nomes = [c.nome for c in CategoriaRepository(conn_perfil).list(apenas_ativas=False)]
    conn_perfil.close()

    assert "Dado antigo do Tiago" in nomes


def test_segundo_perfil_nao_adota_banco_legado(perfis_conn, tmp_path):
    legado = tmp_path / "legado.db"
    init_db(legado)
    conn_legado = get_connection(legado)
    CategoriaRepository(conn_legado).create(Categoria(nome="Dado antigo do Tiago", tipo="saida"))
    conn_legado.close()

    service = _service(perfis_conn, tmp_path, legado_db_path=legado)
    service.criar_perfil("Tiago", "1234")
    service.criar_perfil("Debora", "5678")

    conn_debora = get_connection(service.caminho_banco_do_perfil("Debora"))
    nomes = [c.nome for c in CategoriaRepository(conn_debora).list(apenas_ativas=False)]
    conn_debora.close()

    assert "Dado antigo do Tiago" not in nomes
