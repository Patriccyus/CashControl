import sqlite3
from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.analytics.orcamento_analytics import calcular_consumo_orcamento
from app.repositories.categoria_repository import CategoriaRepository
from app.services.exceptions import ErroValidacao
from app.services.orcamento_service import OrcamentoService
from app.utils.money import formatar_moeda, reais_para_centavos

ROTULOS_SITUACAO = {
    "dentro": "Dentro do limite",
    "proximo": "Próximo do limite",
    "ultrapassado": "Limite ultrapassado",
}
CORES_SITUACAO = {
    "dentro": "#1a7a3c",
    "proximo": "#d4a017",
    "ultrapassado": "#b3261e",
}
COLUNAS = ["Categoria", "Limite", "Gasto", "Consumo", "Situação"]


class OrcamentoPage(QWidget):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__()
        self.conn = conn

        layout = QVBoxLayout(self)

        titulo = QLabel("Orçamento mensal")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(titulo)

        formulario = QHBoxLayout()

        self.combo_categoria = QComboBox()
        for categoria in CategoriaRepository(conn).list(tipo="saida"):
            self.combo_categoria.addItem(categoria.nome, categoria.id)
        formulario.addWidget(self.combo_categoria)

        hoje = date.today()
        self.spin_mes = QSpinBox()
        self.spin_mes.setRange(1, 12)
        self.spin_mes.setValue(hoje.month)
        formulario.addWidget(self.spin_mes)

        self.spin_ano = QSpinBox()
        self.spin_ano.setRange(2000, 2100)
        self.spin_ano.setValue(hoje.year)
        formulario.addWidget(self.spin_ano)

        self.campo_limite = QLineEdit()
        self.campo_limite.setPlaceholderText("Limite (ex: 500,00)")
        formulario.addWidget(self.campo_limite)

        botao_definir = QPushButton("Definir limite")
        botao_definir.clicked.connect(self._definir_limite)
        formulario.addWidget(botao_definir)

        layout.addLayout(formulario)

        self.rotulo_status = QLabel("")
        layout.addWidget(self.rotulo_status)

        self.tabela = QTableWidget(0, len(COLUNAS))
        self.tabela.setHorizontalHeaderLabels(COLUNAS)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabela)

        self.atualizar()

    def _definir_limite(self) -> None:
        self.rotulo_status.setText("")
        categoria_id = self.combo_categoria.currentData()
        if categoria_id is None:
            self._mostrar_erro("Cadastre ao menos uma categoria de saída.")
            return

        try:
            limite = reais_para_centavos(self.campo_limite.text())
        except ValueError as exc:
            self._mostrar_erro(str(exc))
            return

        try:
            OrcamentoService(self.conn).definir_limite(
                categoria_id, self.spin_mes.value(), self.spin_ano.value(), limite
            )
        except ErroValidacao as exc:
            self._mostrar_erro(str(exc))
            return

        self.rotulo_status.setStyleSheet("color: #1a7a3c;")
        self.rotulo_status.setText("Orçamento definido com sucesso.")
        self.campo_limite.clear()
        self.atualizar()

    def _mostrar_erro(self, mensagem: str) -> None:
        self.rotulo_status.setStyleSheet("color: #b3261e;")
        self.rotulo_status.setText(mensagem)

    def atualizar(self) -> None:
        hoje = date.today()
        consumo = calcular_consumo_orcamento(self.conn, hoje.month, hoje.year)
        self.tabela.setRowCount(len(consumo))
        for linha, item in enumerate(consumo):
            valores = [
                item.categoria_nome,
                formatar_moeda(item.limite),
                formatar_moeda(item.gasto),
                f"{item.percentual:.0f}%",
                ROTULOS_SITUACAO[item.situacao],
            ]
            for coluna, texto in enumerate(valores):
                celula = QTableWidgetItem(texto)
                celula.setFlags(celula.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if coluna == 4:
                    celula.setForeground(Qt.GlobalColor.white)
                    celula.setBackground(QColor(CORES_SITUACAO[item.situacao]))
                self.tabela.setItem(linha, coluna, celula)
