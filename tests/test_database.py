def test_init_db_cria_todas_as_tabelas(conn):
    tabelas = {
        row["name"]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }
    esperadas = {
        "categorias",
        "contas",
        "formas_pagamento",
        "movimentacoes",
        "orcamentos",
        "recorrencias",
    }
    assert esperadas.issubset(tabelas)


def test_foreign_keys_habilitadas(conn):
    row = conn.execute("PRAGMA foreign_keys").fetchone()
    assert row[0] == 1
