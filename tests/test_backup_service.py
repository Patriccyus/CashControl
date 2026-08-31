import time

import pytest

from app.database.connection import get_connection, init_db
from app.models.categoria import Categoria
from app.models.conta import Conta
from app.models.forma_pagamento import FormaPagamento
from app.models.movimentacao import Movimentacao
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.conta_repository import ContaRepository
from app.repositories.forma_pagamento_repository import FormaPagamentoRepository
from app.repositories.movimentacao_repository import MovimentacaoRepository
from app.services.backup_service import BackupService
from app.services.exceptions import ErroValidacao


def _preparar_banco_com_dados(caminho_banco):
    init_db(caminho_banco)
    conn = get_connection(caminho_banco)
    categoria_id = CategoriaRepository(conn).create(Categoria(nome="Lazer", tipo="saida"))
    conta_id = ContaRepository(conn).create(Conta(nome="Carteira", tipo="dinheiro"))
    forma_id = FormaPagamentoRepository(conn).create(FormaPagamento(nome="Dinheiro", tipo="dinheiro"))
    MovimentacaoRepository(conn).create(
        Movimentacao(
            data="2026-08-10",
            tipo="saida",
            descricao="Cinema",
            valor=5000,
            categoria_id=categoria_id,
            conta_id=conta_id,
            forma_pagamento_id=forma_id,
        )
    )
    return conn


def test_criar_backup_copia_arquivo(tmp_path):
    caminho_banco = tmp_path / "banco.db"
    conn = _preparar_banco_com_dados(caminho_banco)
    conn.close()

    service = BackupService(caminho_banco, tmp_path / "backups")
    caminho_backup = service.criar_backup()

    assert caminho_backup.exists()
    assert caminho_backup.read_bytes() == caminho_banco.read_bytes()


def test_criar_backup_sem_banco_gera_erro(tmp_path):
    service = BackupService(tmp_path / "nao_existe.db", tmp_path / "backups")
    with pytest.raises(ErroValidacao):
        service.criar_backup()


def test_listar_backups_ordenado_do_mais_recente(tmp_path):
    caminho_banco = tmp_path / "banco.db"
    conn = _preparar_banco_com_dados(caminho_banco)
    conn.close()

    service = BackupService(caminho_banco, tmp_path / "backups")
    primeiro = service.criar_backup()
    time.sleep(1.1)
    segundo = service.criar_backup()

    backups = service.listar_backups()
    assert backups[0] == segundo
    assert backups[1] == primeiro


def test_ja_existe_backup_hoje(tmp_path):
    caminho_banco = tmp_path / "banco.db"
    conn = _preparar_banco_com_dados(caminho_banco)
    conn.close()

    service = BackupService(caminho_banco, tmp_path / "backups")
    assert not service.ja_existe_backup_hoje()

    service.criar_backup()
    assert service.ja_existe_backup_hoje()


def test_restaurar_backup(tmp_path):
    caminho_banco = tmp_path / "banco.db"
    conn = _preparar_banco_com_dados(caminho_banco)

    service = BackupService(caminho_banco, tmp_path / "backups")
    caminho_backup = service.criar_backup()

    MovimentacaoRepository(conn).create(
        Movimentacao(
            data="2026-08-11",
            tipo="saida",
            descricao="Lançamento pós-backup",
            valor=1000,
            categoria_id=1,
            conta_id=1,
            forma_pagamento_id=1,
        )
    )
    assert len(MovimentacaoRepository(conn).list()) == 2

    service.restaurar_backup(caminho_backup, conn)

    conn_restaurada = get_connection(caminho_banco)
    assert len(MovimentacaoRepository(conn_restaurada).list()) == 1
    conn_restaurada.close()


def test_restaurar_backup_inexistente_gera_erro(tmp_path):
    caminho_banco = tmp_path / "banco.db"
    conn = _preparar_banco_com_dados(caminho_banco)

    service = BackupService(caminho_banco, tmp_path / "backups")
    with pytest.raises(ErroValidacao):
        service.restaurar_backup(tmp_path / "backups" / "inexistente.db", conn)
    conn.close()


def test_exportar_csv(tmp_path):
    caminho_banco = tmp_path / "banco.db"
    conn = _preparar_banco_com_dados(caminho_banco)

    service = BackupService(caminho_banco, tmp_path / "backups")
    caminho_csv = service.exportar_csv(conn, tmp_path / "export" / "movimentacoes.csv")
    conn.close()

    assert caminho_csv.exists()
    conteudo = caminho_csv.read_text(encoding="utf-8-sig")
    assert "Cinema" in conteudo
    assert "Lazer" in conteudo
    assert "50,00" in conteudo
