import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from app.database.connection import get_connection, init_db
from app.database.seed import seed_dados_iniciais
from app.interface.gui.main_window import MainWindow
from app.services.recorrencia_service import RecorrenciaService


def main() -> None:
    init_db()
    conn = get_connection()
    seed_dados_iniciais(conn)

    total_gerado = RecorrenciaService(conn).gerar_lancamentos_pendentes()

    app = QApplication(sys.argv)
    janela = MainWindow(conn)
    janela.show()

    if total_gerado:
        plural = "s" if total_gerado > 1 else ""
        QMessageBox.information(
            janela,
            "Lançamentos recorrentes",
            f"{total_gerado} lançamento{plural} recorrente{plural} gerado{plural} "
            "automaticamente com status pendente.",
        )

    codigo_saida = app.exec()

    conn.close()
    sys.exit(codigo_saida)


if __name__ == "__main__":
    main()
