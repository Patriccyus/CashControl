"""Gera um banco de demonstração com dados fictícios e captura as telas da GUI.

Uso, a partir da raiz do projeto:

    python tools/gerar_screenshots.py

O banco de demonstração é criado em `data/demo.db` (ignorado pelo git) e não tem
relação com os perfis reais — ele não é registrado em `data/perfis.db`, então não
aparece na tela de login. As imagens são renderizadas pelo próprio Qt
(`QWidget.grab`), e não por captura de tela: nada do desktop entra nas fotos.
"""
import sqlite3
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

DB_DEMO = RAIZ / "data" / "demo.db"
SAIDA = RAIZ / "assets" / "screenshots"

from app.database.connection import get_connection, init_db  # noqa: E402
from app.database.seed import seed_dados_iniciais  # noqa: E402
from app.utils.money import reais_para_centavos  # noqa: E402

HOJE = date.today()

# Telas capturadas: (índice no menu lateral, nome do arquivo)
TELAS = [
    (0, "dashboard"),
    (2, "historico"),
    (3, "orcamento"),
    (6, "cartao"),
    (5, "recorrencias"),
    (1, "lancamento"),
]


def _categoria_id(conn: sqlite3.Connection, nome: str, tipo: str) -> int:
    linha = conn.execute(
        "SELECT id FROM categorias WHERE nome = ? AND tipo = ?", (nome, tipo)
    ).fetchone()
    return linha["id"]


def _mes_ano(deslocamento: int) -> tuple[int, int]:
    """Mês/ano `deslocamento` meses atrás (use negativo para meses à frente)."""
    mes = HOJE.month - deslocamento
    ano = HOJE.year
    while mes <= 0:
        mes += 12
        ano -= 1
    while mes > 12:
        mes -= 12
        ano += 1
    return mes, ano


def popular(conn: sqlite3.Connection) -> None:
    conn.execute(
        "INSERT INTO contas (nome, tipo, saldo_inicial) VALUES (?, ?, ?)",
        ("Conta Corrente", "conta_corrente", reais_para_centavos("3200.00")),
    )
    conta_id = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
    conn.execute(
        "INSERT INTO contas (nome, tipo, saldo_inicial) VALUES (?, ?, ?)",
        ("Poupança", "poupanca", reais_para_centavos("12500.00")),
    )
    conn.execute(
        "INSERT INTO contas (nome, tipo, saldo_inicial) VALUES (?, ?, ?)",
        ("Carteira Digital", "carteira_digital", reais_para_centavos("450.00")),
    )

    formas = {
        linha["nome"]: linha["id"]
        for linha in conn.execute("SELECT id, nome FROM formas_pagamento")
    }
    pix = formas["Pix"]
    debito = formas["Débito"]
    credito = formas["Crédito"]
    dinheiro = formas["Dinheiro"]

    salario = _categoria_id(conn, "Salário", "entrada")
    freelance = _categoria_id(conn, "Freelance", "entrada")
    rendimentos = _categoria_id(conn, "Rendimentos", "entrada")
    mercado = _categoria_id(conn, "Supermercado", "saida")
    alimentacao = _categoria_id(conn, "Alimentação", "saida")
    moradia = _categoria_id(conn, "Moradia", "saida")
    transporte = _categoria_id(conn, "Transporte", "saida")
    saude = _categoria_id(conn, "Saúde", "saida")
    educacao = _categoria_id(conn, "Educação", "saida")
    lazer = _categoria_id(conn, "Lazer", "saida")
    assinaturas = _categoria_id(conn, "Assinaturas", "saida")

    def inserir(
        dia: int,
        tipo: str,
        descricao: str,
        valor: str,
        categoria: int,
        forma: int,
        mes: int,
        ano: int,
        status: str = "pago",
    ) -> None:
        conn.execute(
            """INSERT INTO movimentacoes
               (data, tipo, descricao, valor, categoria_id, conta_id, forma_pagamento_id, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                f"{ano:04d}-{mes:02d}-{min(dia, 28):02d}",
                tipo,
                descricao,
                reais_para_centavos(valor),
                categoria,
                conta_id,
                forma,
                status,
            ),
        )

    # Lançamentos que se repetem em todos os meses do histórico.
    # (dia, tipo, descrição, valor, categoria, forma de pagamento)
    fixos = [
        (5, "entrada", "Salário", "6500.00", salario, pix),
        (2, "saida", "Aluguel", "1800.00", moradia, pix),
        (10, "saida", "Conta de luz", "182.40", moradia, debito),
        (12, "saida", "Internet", "119.90", moradia, debito),
        (15, "saida", "Plano de saúde", "420.00", saude, debito),
        (5, "saida", "Streaming", "55.90", assinaturas, credito),
        (8, "saida", "Academia", "129.00", lazer, debito),
    ]

    # Lançamentos específicos de cada mês, para o histórico não ficar idêntico.
    # (meses atrás, dia, tipo, descrição, valor, categoria, forma de pagamento)
    variaveis = [
        (5, 7, "saida", "Compra do mês", "812.30", mercado, debito),
        (5, 18, "saida", "Feira", "143.70", mercado, dinheiro),
        (5, 11, "saida", "Restaurante", "96.00", alimentacao, credito),
        (5, 22, "saida", "Combustível", "260.00", transporte, credito),
        (5, 25, "entrada", "Projeto freelance", "1200.00", freelance, pix),
        (4, 6, "saida", "Compra do mês", "878.90", mercado, debito),
        (4, 14, "saida", "Delivery", "127.40", alimentacao, credito),
        (4, 19, "saida", "Combustível", "245.00", transporte, credito),
        (4, 21, "saida", "Cinema", "88.00", lazer, credito),
        (3, 5, "saida", "Compra do mês", "935.20", mercado, debito),
        (3, 13, "saida", "Restaurante", "154.80", alimentacao, credito),
        (3, 17, "saida", "Combustível", "270.00", transporte, credito),
        (3, 24, "saida", "Curso online", "349.00", educacao, credito),
        (3, 28, "entrada", "Rendimento poupança", "86.40", rendimentos, pix),
        (2, 4, "saida", "Compra do mês", "902.10", mercado, debito),
        (2, 12, "saida", "Delivery", "168.50", alimentacao, credito),
        (2, 16, "saida", "Combustível", "255.00", transporte, credito),
        (2, 23, "saida", "Show", "180.00", lazer, credito),
        (2, 27, "entrada", "Projeto freelance", "2400.00", freelance, pix),
        (1, 6, "saida", "Compra do mês", "967.80", mercado, debito),
        (1, 15, "saida", "Restaurante", "142.00", alimentacao, credito),
        (1, 20, "saida", "Combustível", "288.00", transporte, credito),
        (1, 26, "saida", "Dentista", "320.00", saude, pix),
        # No mês atual os gastos de Supermercado e Transporte estouram o
        # orçamento de propósito, para o dashboard mostrar as três situações.
        (0, 3, "saida", "Compra do mês", "648.90", mercado, debito),
        (0, 11, "saida", "Feira", "212.40", mercado, dinheiro),
        (0, 18, "saida", "Supermercado (reposição)", "231.70", mercado, debito),
        (0, 8, "saida", "Restaurante", "186.00", alimentacao, credito),
        (0, 16, "saida", "Delivery", "194.30", alimentacao, credito),
        (0, 9, "saida", "Combustível", "178.00", transporte, credito),
        (0, 14, "saida", "Livraria", "132.00", educacao, credito),
        (0, 20, "saida", "Bar com amigos", "148.00", lazer, credito),
    ]

    for deslocamento in range(5, -1, -1):
        mes, ano = _mes_ano(deslocamento)
        for dia, tipo, descricao, valor, categoria, forma in fixos:
            inserir(dia, tipo, descricao, valor, categoria, forma, mes, ano)
        for desl, dia, tipo, descricao, valor, categoria, forma in variaveis:
            if desl == deslocamento:
                inserir(dia, tipo, descricao, valor, categoria, forma, mes, ano)

    mes_atual, ano_atual = _mes_ano(0)
    inserir(28, "saida", "IPTU (parcela)", "268.00", moradia, pix, mes_atual, ano_atual, "pendente")
    inserir(25, "saida", "Seguro do carro", "410.00", transporte, pix, mes_atual, ano_atual, "pendente")

    orcamentos = [
        (mercado, "900.00"),
        (alimentacao, "400.00"),
        (transporte, "500.00"),
        (lazer, "300.00"),
        (educacao, "250.00"),
    ]
    for categoria, limite in orcamentos:
        conn.execute(
            "INSERT INTO orcamentos (categoria_id, mes, ano, limite) VALUES (?, ?, ?, ?)",
            (categoria, mes_atual, ano_atual, reais_para_centavos(limite)),
        )

    mes_seguinte, ano_seguinte = _mes_ano(-1)
    recorrencias = [
        ("Aluguel", "1800.00", moradia, pix, 2),
        ("Plano de saúde", "420.00", saude, debito, 15),
        ("Streaming", "55.90", assinaturas, credito, 5),
        ("Academia", "129.00", lazer, debito, 8),
        ("Salário", "6500.00", salario, pix, 5),
    ]
    for descricao, valor, categoria, forma, dia in recorrencias:
        conn.execute(
            """INSERT INTO recorrencias
               (descricao, valor, categoria_id, conta_id, forma_pagamento_id, frequencia, proxima_data)
               VALUES (?, ?, ?, ?, ?, 'mensal', ?)""",
            (
                descricao,
                reais_para_centavos(valor),
                categoria,
                conta_id,
                forma,
                f"{ano_seguinte:04d}-{mes_seguinte:02d}-{dia:02d}",
            ),
        )

    conn.execute(
        """INSERT INTO cartoes (nome, limite, dia_fechamento, dia_vencimento, conta_id)
           VALUES (?, ?, ?, ?, ?)""",
        ("Cartão Principal", reais_para_centavos("8000.00"), 20, 28, conta_id),
    )
    cartao_id = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]

    # (descrição, valor total, parcelas, categoria, meses atrás, dia da compra)
    compras = [
        ("Notebook", "4800.00", 10, educacao, 2, 8),
        ("Geladeira", "3200.00", 8, moradia, 1, 12),
        ("Passagem aérea", "1890.00", 6, lazer, 0, 5),
    ]
    for descricao, total, parcelas, categoria, deslocamento, dia in compras:
        mes, ano = _mes_ano(deslocamento)
        conn.execute(
            """INSERT INTO compras_cartao
               (cartao_id, categoria_id, descricao, data_compra, valor_total, numero_parcelas)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                cartao_id,
                categoria,
                descricao,
                f"{ano:04d}-{mes:02d}-{dia:02d}",
                reais_para_centavos(total),
                parcelas,
            ),
        )
        compra_id = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]

        centavos = reais_para_centavos(total)
        base = centavos // parcelas
        resto = centavos - base * parcelas
        for numero in range(1, parcelas + 1):
            mes_fatura, ano_fatura = _mes_ano(deslocamento - (numero - 1))
            conn.execute(
                """INSERT INTO parcelas_cartao (compra_id, numero, valor, fatura_mes, fatura_ano)
                   VALUES (?, ?, ?, ?, ?)""",
                (compra_id, numero, base + (1 if numero <= resto else 0), mes_fatura, ano_fatura),
            )

    conn.commit()


def capturar(conn: sqlite3.Connection) -> None:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication

    from app.interface.gui.main_window import MainWindow

    app = QApplication.instance() or QApplication(sys.argv)
    SAIDA.mkdir(parents=True, exist_ok=True)

    janela = MainWindow(conn, DB_DEMO)
    janela.resize(1180, 740)
    # Monta o layout sem exibir a janela na tela de quem está rodando o script.
    janela.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
    janela.show()
    app.processEvents()

    for indice, nome in TELAS:
        janela.menu_lateral.setCurrentRow(indice)
        app.processEvents()
        caminho = SAIDA / f"{nome}.png"
        janela.grab().save(str(caminho))
        print(f"  {caminho.relative_to(RAIZ)}")

    janela.close()


def main() -> None:
    if DB_DEMO.exists():
        DB_DEMO.unlink()

    init_db(DB_DEMO)
    conn = get_connection(DB_DEMO)
    try:
        seed_dados_iniciais(conn)
        popular(conn)
        print(f"banco de demonstração criado em {DB_DEMO.relative_to(RAIZ)}")
        capturar(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
