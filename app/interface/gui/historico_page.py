import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
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

from app.interface.gui.combos import preencher_combo_contas
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.forma_pagamento_repository import FormaPagamentoRepository
from app.repositories.movimentacao_repository import FiltroMovimentacao, MovimentacaoRepository
from app.utils.money import formatar_moeda

COLUNAS = ["Data", "Tipo", "Valor", "Categoria", "Forma de pagamento", "Status", "Descrição"]


class HistoricoPage(QWidget):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__()
        self.conn = conn

        layout = QVBoxLayout(self)

        titulo = QLabel("Histórico financeiro")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(titulo)

        filtros_layout = QHBoxLayout()

        self.campo_data_inicio = QLineEdit()
        self.campo_data_inicio.setPlaceholderText("Data início (AAAA-MM-DD)")
        self.campo_data_inicio.setMinimumWidth(150)
        filtros_layout.addWidget(self.campo_data_inicio)

        self.campo_data_fim = QLineEdit()
        self.campo_data_fim.setPlaceholderText("Data fim (AAAA-MM-DD)")
        self.campo_data_fim.setMinimumWidth(150)
        filtros_layout.addWidget(self.campo_data_fim)

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItem("Todos os tipos", None)
        self.combo_tipo.addItem("Entrada", "entrada")
        self.combo_tipo.addItem("Saída", "saida")
        filtros_layout.addWidget(self.combo_tipo)

        self.combo_categoria = QComboBox()
        self._preencher_categorias()
        filtros_layout.addWidget(self.combo_categoria)

        self.combo_conta = QComboBox()
        preencher_combo_contas(self.combo_conta, conn, incluir_todas=True, apenas_ativas=False)
        filtros_layout.addWidget(self.combo_conta)

        self.combo_forma_pagamento = QComboBox()
        self.combo_forma_pagamento.addItem("Todas as formas", None)
        for forma in FormaPagamentoRepository(conn).list(apenas_ativas=False):
            self.combo_forma_pagamento.addItem(forma.nome, forma.id)
        filtros_layout.addWidget(self.combo_forma_pagamento)

        self.combo_status = QComboBox()
        self.combo_status.addItem("Todos os status", None)
        self.combo_status.addItem("Pago/Recebido", "pago")
        self.combo_status.addItem("Pendente", "pendente")
        filtros_layout.addWidget(self.combo_status)

        layout.addLayout(filtros_layout)

        busca_layout = QHBoxLayout()
        self.campo_busca = QLineEdit()
        self.campo_busca.setPlaceholderText("Buscar por texto na descrição")
        busca_layout.addWidget(self.campo_busca)

        botao_filtrar = QPushButton("Filtrar")
        botao_filtrar.clicked.connect(self.atualizar)
        busca_layout.addWidget(botao_filtrar)

        botao_limpar = QPushButton("Limpar filtros")
        botao_limpar.clicked.connect(self._limpar_filtros)
        busca_layout.addWidget(botao_limpar)

        layout.addLayout(busca_layout)

        self.tabela = QTableWidget(0, len(COLUNAS))
        self.tabela.setHorizontalHeaderLabels(COLUNAS)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabela)

        self.atualizar()

    def _preencher_categorias(self) -> None:
        self.combo_categoria.clear()
        self.combo_categoria.addItem("Todas as categorias", None)
        for categoria in CategoriaRepository(self.conn).list(apenas_ativas=False):
            self.combo_categoria.addItem(categoria.nome, categoria.id)

    def _limpar_filtros(self) -> None:
        self.campo_data_inicio.clear()
        self.campo_data_fim.clear()
        self.campo_busca.clear()
        self.combo_tipo.setCurrentIndex(0)
        self.combo_categoria.setCurrentIndex(0)
        self.combo_conta.setCurrentIndex(0)
        self.combo_forma_pagamento.setCurrentIndex(0)
        self.combo_status.setCurrentIndex(0)
        self.atualizar()

    def atualizar(self) -> None:
        preencher_combo_contas(self.combo_conta, self.conn, incluir_todas=True, apenas_ativas=False)

        filtro = FiltroMovimentacao(
            data_inicio=self.campo_data_inicio.text().strip() or None,
            data_fim=self.campo_data_fim.text().strip() or None,
            tipo=self.combo_tipo.currentData(),
            categoria_id=self.combo_categoria.currentData(),
            conta_id=self.combo_conta.currentData(),
            forma_pagamento_id=self.combo_forma_pagamento.currentData(),
            status=self.combo_status.currentData(),
            busca_texto=self.campo_busca.text().strip() or None,
        )
        movimentacoes = MovimentacaoRepository(self.conn).list(filtro)

        categorias = {c.id: c.nome for c in CategoriaRepository(self.conn).list(apenas_ativas=False)}
        formas_pagamento = {f.id: f.nome for f in FormaPagamentoRepository(self.conn).list(apenas_ativas=False)}

        self.tabela.setRowCount(len(movimentacoes))
        for linha, mov in enumerate(movimentacoes):
            valores = [
                mov.data,
                "Entrada" if mov.tipo == "entrada" else "Saída",
                formatar_moeda(mov.valor),
                categorias.get(mov.categoria_id, "?"),
                formas_pagamento.get(mov.forma_pagamento_id, "?"),
                "Pago/Recebido" if mov.status == "pago" else "Pendente",
                mov.descricao,
            ]
            for coluna, texto in enumerate(valores):
                item = QTableWidgetItem(texto)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tabela.setItem(linha, coluna, item)
