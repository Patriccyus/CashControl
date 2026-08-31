import sqlite3

from PySide6.QtWidgets import QHBoxLayout, QListWidget, QMainWindow, QStackedWidget, QWidget

from app.interface.gui.dashboard_page import DashboardPage
from app.interface.gui.historico_page import HistoricoPage
from app.interface.gui.lancamento_page import LancamentoPage
from app.interface.gui.orcamento_page import OrcamentoPage
from app.interface.gui.recorrencia_page import RecorrenciaPage
from app.interface.gui.relatorio_page import RelatorioPage


class MainWindow(QMainWindow):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__()
        self.conn = conn
        self.setWindowTitle("Controle Financeiro")
        self.resize(1100, 700)

        widget_central = QWidget()
        layout = QHBoxLayout(widget_central)

        self.menu_lateral = QListWidget()
        self.menu_lateral.setFixedWidth(180)
        self.menu_lateral.addItems(
            ["Dashboard", "Novo lançamento", "Histórico", "Orçamento", "Relatório", "Recorrências"]
        )
        self.menu_lateral.currentRowChanged.connect(self._trocar_pagina)
        layout.addWidget(self.menu_lateral)

        self.paginas = QStackedWidget()
        self.pagina_dashboard = DashboardPage(conn)
        self.pagina_lancamento = LancamentoPage(conn, ao_salvar=self._apos_novo_lancamento)
        self.pagina_historico = HistoricoPage(conn)
        self.pagina_orcamento = OrcamentoPage(conn)
        self.pagina_relatorio = RelatorioPage(conn)
        self.pagina_recorrencia = RecorrenciaPage(conn)

        for pagina in (
            self.pagina_dashboard,
            self.pagina_lancamento,
            self.pagina_historico,
            self.pagina_orcamento,
            self.pagina_relatorio,
            self.pagina_recorrencia,
        ):
            self.paginas.addWidget(pagina)

        layout.addWidget(self.paginas)
        self.setCentralWidget(widget_central)

        self.menu_lateral.setCurrentRow(0)

    def _trocar_pagina(self, indice: int) -> None:
        self.paginas.setCurrentIndex(indice)
        pagina_atual = self.paginas.currentWidget()
        if hasattr(pagina_atual, "atualizar"):
            pagina_atual.atualizar()

    def _apos_novo_lancamento(self) -> None:
        self.pagina_dashboard.atualizar()
        self.pagina_historico.atualizar()
        self.pagina_orcamento.atualizar()
