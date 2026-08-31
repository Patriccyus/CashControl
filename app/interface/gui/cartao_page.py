import sqlite3
from datetime import date

from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
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

from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.compra_cartao_repository import CompraCartaoRepository
from app.repositories.conta_repository import ContaRepository
from app.repositories.fatura_paga_repository import FaturaPagaRepository
from app.services.cartao_service import CartaoService
from app.services.compra_cartao_service import CompraCartaoService
from app.services.exceptions import ErroValidacao
from app.services.fatura_cartao_service import FaturaCartaoService
from app.utils.money import formatar_moeda, reais_para_centavos

ROTULOS_STATUS = {"aberta": "Aberta", "fechada": "Fechada (aguardando pagamento)", "paga": "Paga"}


class CartaoPage(QWidget):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__()
        self.conn = conn

        layout = QVBoxLayout(self)

        titulo = QLabel("Cartão de crédito")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(titulo)

        layout.addLayout(self._construir_formulario_cartao())

        self.rotulo_status_cartao = QLabel("")
        layout.addWidget(self.rotulo_status_cartao)

        selecao_layout = QHBoxLayout()
        selecao_layout.addWidget(QLabel("Cartão selecionado:"))
        self.combo_cartao = QComboBox()
        self.combo_cartao.setMinimumWidth(160)
        self.combo_cartao.currentIndexChanged.connect(self._atualizar_faturas)
        selecao_layout.addWidget(self.combo_cartao)
        selecao_layout.addStretch()
        layout.addLayout(selecao_layout)

        layout.addLayout(self._construir_formulario_compra())

        self.rotulo_status_compra = QLabel("")
        layout.addWidget(self.rotulo_status_compra)

        layout.addWidget(QLabel("Faturas"))
        self.tabela_faturas = QTableWidget(0, 5)
        self.tabela_faturas.setHorizontalHeaderLabels(["Mês/Ano", "Valor", "Vencimento", "Status", "Ação"])
        self.tabela_faturas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela_faturas.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabela_faturas)

        self.atualizar()

    def _construir_formulario_cartao(self) -> QGridLayout:
        form = QGridLayout()

        self.campo_nome_cartao = QLineEdit()
        self.campo_nome_cartao.setPlaceholderText("Ex: Nubank")
        form.addWidget(QLabel("Nome do cartão"), 0, 0)
        form.addWidget(self.campo_nome_cartao, 1, 0)

        self.campo_limite_cartao = QLineEdit()
        self.campo_limite_cartao.setPlaceholderText("Ex: 5000,00")
        form.addWidget(QLabel("Limite"), 0, 1)
        form.addWidget(self.campo_limite_cartao, 1, 1)

        self.spin_dia_fechamento = QSpinBox()
        self.spin_dia_fechamento.setRange(1, 28)
        self.spin_dia_fechamento.setValue(25)
        form.addWidget(QLabel("Dia de fechamento"), 0, 2)
        form.addWidget(self.spin_dia_fechamento, 1, 2)

        self.spin_dia_vencimento = QSpinBox()
        self.spin_dia_vencimento.setRange(1, 28)
        self.spin_dia_vencimento.setValue(5)
        form.addWidget(QLabel("Dia de vencimento"), 0, 3)
        form.addWidget(self.spin_dia_vencimento, 1, 3)

        self.combo_conta_cartao = QComboBox()
        for conta in ContaRepository(self.conn).list():
            self.combo_conta_cartao.addItem(conta.nome, conta.id)
        form.addWidget(QLabel("Conta de pagamento"), 0, 4)
        form.addWidget(self.combo_conta_cartao, 1, 4)

        botao_criar_cartao = QPushButton("Criar cartão")
        botao_criar_cartao.clicked.connect(self._criar_cartao)
        form.addWidget(botao_criar_cartao, 1, 5)

        return form

    def _construir_formulario_compra(self) -> QGridLayout:
        form = QGridLayout()

        self.campo_descricao_compra = QLineEdit()
        self.campo_descricao_compra.setPlaceholderText("Ex: Notebook")
        form.addWidget(QLabel("Descrição"), 0, 0)
        form.addWidget(self.campo_descricao_compra, 1, 0)

        self.campo_valor_compra = QLineEdit()
        self.campo_valor_compra.setPlaceholderText("Ex: 3000,00")
        form.addWidget(QLabel("Valor"), 0, 1)
        form.addWidget(self.campo_valor_compra, 1, 1)

        self.combo_categoria_compra = QComboBox()
        for categoria in CategoriaRepository(self.conn).list(tipo="saida"):
            self.combo_categoria_compra.addItem(categoria.nome, categoria.id)
        form.addWidget(QLabel("Categoria"), 0, 2)
        form.addWidget(self.combo_categoria_compra, 1, 2)

        self.campo_data_compra = QLineEdit(date.today().isoformat())
        form.addWidget(QLabel("Data da compra"), 0, 3)
        form.addWidget(self.campo_data_compra, 1, 3)

        self.spin_parcelas = QSpinBox()
        self.spin_parcelas.setRange(1, 48)
        self.spin_parcelas.setValue(1)
        form.addWidget(QLabel("Parcelas"), 0, 4)
        form.addWidget(self.spin_parcelas, 1, 4)

        botao_registrar_compra = QPushButton("Registrar compra")
        botao_registrar_compra.clicked.connect(self._registrar_compra)
        form.addWidget(botao_registrar_compra, 1, 5)

        return form

    def _recarregar_combo_cartoes(self) -> None:
        cartao_id_atual = self.combo_cartao.currentData()
        self.combo_cartao.blockSignals(True)
        self.combo_cartao.clear()
        for cartao in CartaoService(self.conn).listar():
            self.combo_cartao.addItem(cartao.nome, cartao.id)
        indice = self.combo_cartao.findData(cartao_id_atual)
        self.combo_cartao.setCurrentIndex(indice if indice >= 0 else 0)
        self.combo_cartao.blockSignals(False)

    def _criar_cartao(self) -> None:
        self.rotulo_status_cartao.setText("")
        try:
            limite = reais_para_centavos(self.campo_limite_cartao.text())
        except ValueError as exc:
            self._erro_cartao(str(exc))
            return

        conta_id = self.combo_conta_cartao.currentData()
        if conta_id is None:
            self._erro_cartao("Cadastre ao menos uma conta.")
            return

        try:
            CartaoService(self.conn).criar(
                nome=self.campo_nome_cartao.text(),
                limite=limite,
                dia_fechamento=self.spin_dia_fechamento.value(),
                dia_vencimento=self.spin_dia_vencimento.value(),
                conta_id=conta_id,
            )
        except ErroValidacao as exc:
            self._erro_cartao(str(exc))
            return

        self.rotulo_status_cartao.setStyleSheet("color: #1a7a3c;")
        self.rotulo_status_cartao.setText("Cartão criado com sucesso.")
        self.campo_nome_cartao.clear()
        self.campo_limite_cartao.clear()
        self.atualizar()

    def _erro_cartao(self, mensagem: str) -> None:
        self.rotulo_status_cartao.setStyleSheet("color: #b3261e;")
        self.rotulo_status_cartao.setText(mensagem)

    def _registrar_compra(self) -> None:
        self.rotulo_status_compra.setText("")
        cartao_id = self.combo_cartao.currentData()
        if cartao_id is None:
            self._erro_compra("Cadastre um cartão primeiro.")
            return

        try:
            valor = reais_para_centavos(self.campo_valor_compra.text())
        except ValueError as exc:
            self._erro_compra(str(exc))
            return

        categoria_id = self.combo_categoria_compra.currentData()
        if categoria_id is None:
            self._erro_compra("Cadastre ao menos uma categoria de saída.")
            return

        try:
            CompraCartaoService(self.conn).registrar_compra(
                cartao_id=cartao_id,
                categoria_id=categoria_id,
                descricao=self.campo_descricao_compra.text(),
                data_compra=self.campo_data_compra.text().strip(),
                valor_total=valor,
                numero_parcelas=self.spin_parcelas.value(),
            )
        except ErroValidacao as exc:
            self._erro_compra(str(exc))
            return

        self.rotulo_status_compra.setStyleSheet("color: #1a7a3c;")
        self.rotulo_status_compra.setText("Compra registrada com sucesso.")
        self.campo_descricao_compra.clear()
        self.campo_valor_compra.clear()
        self.spin_parcelas.setValue(1)
        self._atualizar_faturas()

    def _erro_compra(self, mensagem: str) -> None:
        self.rotulo_status_compra.setStyleSheet("color: #b3261e;")
        self.rotulo_status_compra.setText(mensagem)

    def _pagar_fatura(self, cartao_id: int, mes: int, ano: int) -> None:
        try:
            FaturaCartaoService(self.conn).pagar_fatura(cartao_id, mes, ano)
        except ErroValidacao as exc:
            self._erro_compra(str(exc))
            return
        self.rotulo_status_compra.setStyleSheet("color: #1a7a3c;")
        self.rotulo_status_compra.setText(f"Fatura {mes:02d}/{ano} paga com sucesso.")
        self._atualizar_faturas()

    def atualizar(self) -> None:
        self._recarregar_combo_cartoes()
        self._atualizar_faturas()

    def _atualizar_faturas(self) -> None:
        cartao_id = self.combo_cartao.currentData()
        self.tabela_faturas.setRowCount(0)
        if cartao_id is None:
            return

        service = FaturaCartaoService(self.conn)
        periodos = self._periodos_relevantes(cartao_id)

        self.tabela_faturas.setRowCount(len(periodos))
        for linha, (mes, ano) in enumerate(periodos):
            fatura = service.calcular(cartao_id, mes, ano)
            self.tabela_faturas.setItem(linha, 0, QTableWidgetItem(f"{mes:02d}/{ano}"))
            self.tabela_faturas.setItem(linha, 1, QTableWidgetItem(formatar_moeda(fatura.valor_total)))
            self.tabela_faturas.setItem(linha, 2, QTableWidgetItem(fatura.data_vencimento))
            self.tabela_faturas.setItem(linha, 3, QTableWidgetItem(ROTULOS_STATUS[fatura.status]))

            if fatura.status == "paga" or fatura.valor_total == 0:
                self.tabela_faturas.setCellWidget(linha, 4, QLabel("—"))
            else:
                botao = QPushButton("Pagar")
                botao.clicked.connect(
                    lambda _checked=False, m=mes, a=ano, c=cartao_id: self._pagar_fatura(c, m, a)
                )
                self.tabela_faturas.setCellWidget(linha, 4, botao)

    def _periodos_relevantes(self, cartao_id: int):
        periodos_com_compras = {
            (mes, ano)
            for mes, ano, _ in CompraCartaoRepository(self.conn).parcelas_futuras_por_periodo(cartao_id)
        }
        periodos_pagos = FaturaPagaRepository(self.conn).periodos_pagos(cartao_id)
        return sorted(periodos_com_compras | periodos_pagos, key=lambda periodo: (periodo[1], periodo[0]))
