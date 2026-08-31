import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.repositories.conta_repository import ContaRepository
from app.services.conta_service import TIPOS_VALIDOS, ContaService
from app.services.exceptions import ErroValidacao
from app.utils.money import formatar_moeda, reais_para_centavos

ROTULOS_TIPO = {
    "banco": "Banco",
    "conta_corrente": "Conta corrente",
    "poupanca": "Poupança",
    "dinheiro": "Dinheiro",
    "carteira_digital": "Carteira digital",
}

COLUNAS = ["Nome", "Tipo", "Saldo inicial", "Ações"]


class ContaPage(QWidget):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__()
        self.conn = conn

        layout = QVBoxLayout(self)

        titulo = QLabel("Contas")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(titulo)

        formulario = QGridLayout()

        self.campo_nome = QLineEdit()
        self.campo_nome.setPlaceholderText("Ex: Banco Bradesco")
        formulario.addWidget(QLabel("Nome"), 0, 0)
        formulario.addWidget(self.campo_nome, 1, 0)

        self.combo_tipo = QComboBox()
        for tipo in sorted(TIPOS_VALIDOS):
            self.combo_tipo.addItem(ROTULOS_TIPO.get(tipo, tipo), tipo)
        formulario.addWidget(QLabel("Tipo"), 0, 1)
        formulario.addWidget(self.combo_tipo, 1, 1)

        self.campo_saldo_inicial = QLineEdit()
        self.campo_saldo_inicial.setPlaceholderText("Ex: 0,00")
        formulario.addWidget(QLabel("Saldo inicial"), 0, 2)
        formulario.addWidget(self.campo_saldo_inicial, 1, 2)

        botao_criar = QPushButton("Criar conta")
        botao_criar.clicked.connect(self._criar)
        formulario.addWidget(botao_criar, 1, 3)

        layout.addLayout(formulario)

        self.rotulo_status = QLabel("")
        layout.addWidget(self.rotulo_status)

        self.tabela = QTableWidget(0, len(COLUNAS))
        self.tabela.setHorizontalHeaderLabels(COLUNAS)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabela)

        self.atualizar()

    def _criar(self) -> None:
        self.rotulo_status.setText("")
        saldo_inicial_texto = self.campo_saldo_inicial.text().strip() or "0"
        try:
            saldo_inicial = reais_para_centavos(saldo_inicial_texto)
        except ValueError as exc:
            self._mostrar_erro(str(exc))
            return

        try:
            ContaService(self.conn).criar(
                nome=self.campo_nome.text(),
                tipo=self.combo_tipo.currentData(),
                saldo_inicial=saldo_inicial,
            )
        except ErroValidacao as exc:
            self._mostrar_erro(str(exc))
            return

        self.rotulo_status.setStyleSheet("color: #1a7a3c;")
        self.rotulo_status.setText("Conta criada com sucesso.")
        self.campo_nome.clear()
        self.campo_saldo_inicial.clear()
        self.atualizar()

    def _mostrar_erro(self, mensagem: str) -> None:
        self.rotulo_status.setStyleSheet("color: #b3261e;")
        self.rotulo_status.setText(mensagem)

    def _desativar(self, conta_id: int) -> None:
        ContaService(self.conn).desativar(conta_id)
        self.atualizar()

    def atualizar(self) -> None:
        contas = ContaRepository(self.conn).list()
        self.tabela.setRowCount(len(contas))
        for linha, conta in enumerate(contas):
            valores = [conta.nome, ROTULOS_TIPO.get(conta.tipo, conta.tipo), formatar_moeda(conta.saldo_inicial)]
            for coluna, texto in enumerate(valores):
                item = QTableWidgetItem(texto)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tabela.setItem(linha, coluna, item)

            botao_desativar = QPushButton("Desativar")
            botao_desativar.clicked.connect(lambda _checked=False, cid=conta.id: self._desativar(cid))
            self.tabela.setCellWidget(linha, len(valores), botao_desativar)
