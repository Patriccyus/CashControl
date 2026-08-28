from app.database.connection import get_connection, init_db
from app.database.seed import seed_dados_iniciais


def main() -> None:
    init_db()
    conn = get_connection()
    try:
        seed_dados_iniciais(conn)
    finally:
        conn.close()
    print("Banco de dados pronto em data/controle_financeiro.db")


if __name__ == "__main__":
    main()
