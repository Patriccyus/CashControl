import sqlite3
from datetime import date

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

from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.conta_repository import ContaRepository
from app.repositories.forma_pagamento_repository import FormaPagamentoRepository
from app.services.exceptions import ErroValidacao
from app.services.recorrencia_service import FREQUENCIAS_VALIDAS, RecorrenciaService
from app.utils.money import formatar_moeda, reais_para_centavos

COLUNAS = ["Descrição", "Valor", "Categoria", "Frequência", "Próxima data", "Até", "Ações"]


class RecorrenciaPage(QWidget):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__()
        self.conn = conn

        layout = QVBoxLayout(self)

        titulo = QLabel("Recorrências")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(titulo)

        formulario = QGridLayout()

        self.campo_descricao = QLineEdit()
        self.campo_descricao.setPlaceholderText("Ex: Aluguel")
        formulario.addWidget(QLabel("Descrição"), 0, 0)
        formulario.addWidget(self.campo_descricao, 1, 0)

        self.campo_valor = QLineEdit()
        self.campo_valor.setPlaceholderText("Ex: 1500,00")
        formulario.addWidget(QLabel("Valor"), 0, 1)
        formulario.addWidget(self.campo_valor, 1, 1)

        self.combo_categoria = QComboBox()
        for categoria in CategoriaRepository(conn).list():
            self.combo_categoria.addItem(f"{categoria.nome} ({categoria.tipo})", categoria.id)
        formulario.addWidget(QLabel("Categoria"), 0, 2)
        formulario.addWidget(self.combo_categoria, 1, 2)

        self.combo_conta = QComboBox()
        for conta in ContaRepository(conn).list():
            self.combo_conta.addItem(conta.nome, conta.id)
        formulario.addWidget(QLabel("Conta"), 0, 3)
        formulario.addWidget(self.combo_conta, 1, 3)

        self.combo_forma_pagamento = QComboBox()
        for forma in FormaPagamentoRepository(conn).list():
            self.combo_forma_pagamento.addItem(forma.nome, forma.id)
        formulario.addWidget(QLabel("Forma de pagamento"), 0, 4)
        formulario.addWidget(self.combo_forma_pagamento, 1, 4)

        self.combo_frequencia = QComboBox()
        for frequencia in sorted(FREQUENCIAS_VALIDAS):
            self.combo_frequencia.addItem(frequencia.capitalize(), frequencia)
        formulario.addWidget(QLabel("Frequência"), 0, 5)
        formulario.addWidget(self.combo_frequencia, 1, 5)

        self.campo_data_inicio = QLineEdit(date.today().isoformat())
        formulario.addWidget(QLabel("Data de início"), 0, 6)
        formulario.addWidget(self.campo_data_inicio, 1, 6)

        self.campo_data_fim = QLineEdit()
        self.campo_data_fim.setPlaceholderText("Opcional (AAAA-MM-DD)")
        formulario.addWidget(QLabel("Data de término"), 0, 7)
        formulario.addWidget(self.campo_data_fim, 1, 7)

        layout.addLayout(formulario)

        linha_botao = QHBoxLayout()
        self.botao_criar = QPushButton("Criar recorrência")
        self.botao_criar.clicked.connect(self._criar)
        linha_botao.addWidget(self.botao_criar)
        linha_botao.addStretch()
        layout.addLayout(linha_botao)

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
        try:
            valor = reais_para_centavos(self.campo_valor.text())
        except ValueError as exc:
            self._mostrar_erro(str(exc))
            return

        categoria_id = self.combo_categoria.currentData()
        conta_id = self.combo_conta.currentData()
        forma_pagamento_id = self.combo_forma_pagamento.currentData()
        if categoria_id is None or conta_id is None or forma_pagamento_id is None:
            self._mostrar_erro("Cadastre ao menos uma categoria, conta e forma de pagamento.")
            return

        try:
            RecorrenciaService(self.conn).criar(
                descricao=self.campo_descricao.text(),
                valor=valor,
                categoria_id=categoria_id,
                conta_id=conta_id,
                forma_pagamento_id=forma_pagamento_id,
                frequencia=self.combo_frequencia.currentData(),
                data_inicio=self.campo_data_inicio.text().strip(),
                data_fim=self.campo_data_fim.text().strip() or None,
            )
        except ErroValidacao as exc:
            self._mostrar_erro(str(exc))
            return

        self.rotulo_status.setStyleSheet("color: #1a7a3c;")
        self.rotulo_status.setText("Recorrência criada com sucesso.")
        self.campo_descricao.clear()
        self.campo_valor.clear()
        self.campo_data_fim.clear()
        self.atualizar()

    def _mostrar_erro(self, mensagem: str) -> None:
        self.rotulo_status.setStyleSheet("color: #b3261e;")
        self.rotulo_status.setText(mensagem)

    def _desativar(self, recorrencia_id: int) -> None:
        RecorrenciaService(self.conn).desativar(recorrencia_id)
        self.atualizar()

    def atualizar(self) -> None:
        recorrencias = RecorrenciaService(self.conn).listar()
        categorias = {c.id: c.nome for c in CategoriaRepository(self.conn).list(apenas_ativas=False)}

        self.tabela.setRowCount(len(recorrencias))
        for linha, rec in enumerate(recorrencias):
            valores = [
                rec.descricao,
                formatar_moeda(rec.valor),
                categorias.get(rec.categoria_id, "?"),
                rec.frequencia,
                rec.proxima_data,
                rec.data_fim or "—",
            ]
            for coluna, texto in enumerate(valores):
                item = QTableWidgetItem(texto)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tabela.setItem(linha, coluna, item)

            botao_desativar = QPushButton("Desativar")
            botao_desativar.clicked.connect(lambda _checked=False, rid=rec.id: self._desativar(rid))
            self.tabela.setCellWidget(linha, len(valores), botao_desativar)
