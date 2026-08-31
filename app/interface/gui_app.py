import sys

from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

from app.database.connection import get_connection, init_db
from app.database.perfis_connection import get_perfis_connection
from app.database.seed import seed_dados_iniciais
from app.interface.gui.login_window import LoginWindow
from app.interface.gui.main_window import MainWindow
from app.services.backup_service import BackupService
from app.services.perfil_service import PerfilService
from app.services.recorrencia_service import RecorrenciaService


def main() -> None:
    app = QApplication(sys.argv)

    conexao_perfis = get_perfis_connection()
    perfil_service = PerfilService(conexao_perfis)

    login = LoginWindow(perfil_service)
    if login.exec() != QDialog.DialogCode.Accepted:
        conexao_perfis.close()
        sys.exit(0)

    conexao_perfis.close()

    caminho_banco = login.caminho_banco
    init_db(caminho_banco)
    conn = get_connection(caminho_banco)
    seed_dados_iniciais(conn)

    backup_service = BackupService(caminho_banco, caminho_banco.parent / "backups" / caminho_banco.stem)
    if not backup_service.ja_existe_backup_hoje():
        backup_service.criar_backup()

    total_gerado = RecorrenciaService(conn).gerar_lancamentos_pendentes()

    janela = MainWindow(conn, caminho_banco)
    janela.setWindowTitle(f"Controle Financeiro — {login.perfil_autenticado.nome}")
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
