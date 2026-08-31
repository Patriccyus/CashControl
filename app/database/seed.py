import sqlite3

CATEGORIAS_PADRAO = [
    ("Salário", "entrada"),
    ("Freelance", "entrada"),
    ("Venda", "entrada"),
    ("Rendimentos", "entrada"),
    ("Outros", "entrada"),
    ("Supermercado", "saida"),
    ("Alimentação", "saida"),
    ("Moradia", "saida"),
    ("Transporte", "saida"),
    ("Saúde", "saida"),
    ("Educação", "saida"),
    ("Lazer", "saida"),
    ("Assinaturas", "saida"),
    ("Compras", "saida"),
    ("Serviços", "saida"),
    ("Impostos", "saida"),
    ("Cartão de crédito", "saida"),
    ("Outros", "saida"),
]

CONTAS_PADRAO = [
    ("Carteira", "dinheiro"),
]

FORMAS_PAGAMENTO_PADRAO = [
    ("Dinheiro", "dinheiro"),
    ("Pix", "pix"),
    ("Débito", "debito"),
    ("Crédito", "credito"),
]


def seed_dados_iniciais(conn: sqlite3.Connection) -> None:
    if conn.execute("SELECT COUNT(*) FROM categorias").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO categorias (nome, tipo) VALUES (?, ?)", CATEGORIAS_PADRAO
        )

    if conn.execute("SELECT COUNT(*) FROM contas").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO contas (nome, tipo) VALUES (?, ?)", CONTAS_PADRAO
        )

    if conn.execute("SELECT COUNT(*) FROM formas_pagamento").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO formas_pagamento (nome, tipo) VALUES (?, ?)",
            FORMAS_PAGAMENTO_PADRAO,
        )

    conn.commit()
