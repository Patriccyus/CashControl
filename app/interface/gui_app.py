import sys

from PySide6.QtWidgets import QApplication

from app.database.connection import get_connection, init_db
from app.database.seed import seed_dados_iniciais
from app.interface.gui.main_window import MainWindow


def main() -> None:
    init_db()
    conn = get_connection()
    seed_dados_iniciais(conn)

    app = QApplication(sys.argv)
    janela = MainWindow(conn)
    janela.show()
    codigo_saida = app.exec()

    conn.close()
    sys.exit(codigo_saida)


if __name__ == "__main__":
    main()
