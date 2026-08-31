import sqlite3
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.services.backup_service import BackupService
from app.services.exceptions import ErroValidacao

COLUNAS = ["Arquivo", "Data", "Tamanho", "Ação"]


class BackupPage(QWidget):
    def __init__(self, conn: sqlite3.Connection, caminho_banco: Path):
        super().__init__()
        self.conn = conn
        self.caminho_banco = Path(caminho_banco)
        self.backup_service = BackupService(
            self.caminho_banco, self.caminho_banco.parent / "backups" / self.caminho_banco.stem
        )

        layout = QVBoxLayout(self)

        titulo = QLabel("Backup e exportação")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(titulo)

        botoes = QHBoxLayout()

        botao_backup = QPushButton("Criar backup agora")
        botao_backup.clicked.connect(self._criar_backup)
        botoes.addWidget(botao_backup)

        botao_exportar = QPushButton("Exportar movimentações (CSV)")
        botao_exportar.clicked.connect(self._exportar_csv)
        botoes.addWidget(botao_exportar)

        botoes.addStretch()
        layout.addLayout(botoes)

        self.rotulo_status = QLabel("")
        layout.addWidget(self.rotulo_status)

        layout.addWidget(QLabel("Backups existentes"))
        self.tabela = QTableWidget(0, len(COLUNAS))
        self.tabela.setHorizontalHeaderLabels(COLUNAS)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabela)

        self.atualizar()

    def _criar_backup(self) -> None:
        try:
            caminho = self.backup_service.criar_backup()
        except ErroValidacao as exc:
            self._mostrar_erro(str(exc))
            return

        self.rotulo_status.setStyleSheet("color: #1a7a3c;")
        self.rotulo_status.setText(f"Backup criado: {caminho.name}")
        self.atualizar()

    def _exportar_csv(self) -> None:
        sugestao = str(Path.home() / "movimentacoes.csv")
        caminho_texto, _filtro = QFileDialog.getSaveFileName(
            self, "Exportar movimentações", sugestao, "CSV (*.csv)"
        )
        if not caminho_texto:
            return

        caminho = self.backup_service.exportar_csv(self.conn, Path(caminho_texto))
        self.rotulo_status.setStyleSheet("color: #1a7a3c;")
        self.rotulo_status.setText(f"Movimentações exportadas para {caminho}")

    def _restaurar(self, caminho_backup: Path) -> None:
        resposta = QMessageBox.question(
            self,
            "Restaurar backup",
            f"Restaurar o backup de {caminho_backup.name}? Isso substitui os dados atuais "
            "deste perfil pelos dados do backup, e o aplicativo será fechado em seguida.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return

        try:
            self.backup_service.restaurar_backup(caminho_backup, self.conn)
        except ErroValidacao as exc:
            self._mostrar_erro(str(exc))
            return

        QMessageBox.information(
            self,
            "Restauração concluída",
            "Os dados foram restaurados. O aplicativo será fechado — abra novamente para continuar.",
        )
        QApplication.quit()

    def _mostrar_erro(self, mensagem: str) -> None:
        self.rotulo_status.setStyleSheet("color: #b3261e;")
        self.rotulo_status.setText(mensagem)

    def atualizar(self) -> None:
        backups = self.backup_service.listar_backups()
        self.tabela.setRowCount(len(backups))
        for linha, caminho in enumerate(backups):
            estatisticas = caminho.stat()
            data_criacao = datetime.fromtimestamp(estatisticas.st_mtime).strftime("%d/%m/%Y %H:%M")
            tamanho_kb = estatisticas.st_size / 1024

            self.tabela.setItem(linha, 0, QTableWidgetItem(caminho.name))
            self.tabela.setItem(linha, 1, QTableWidgetItem(data_criacao))
            self.tabela.setItem(linha, 2, QTableWidgetItem(f"{tamanho_kb:.0f} KB"))

            botao_restaurar = QPushButton("Restaurar")
            botao_restaurar.clicked.connect(
                lambda _checked=False, c=caminho: self._restaurar(c)
            )
            self.tabela.setCellWidget(linha, 3, botao_restaurar)
