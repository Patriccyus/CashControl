import sqlite3
from datetime import date

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.interface.gui.combos import preencher_combo_contas
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.forma_pagamento_repository import FormaPagamentoRepository
from app.services.exceptions import ErroValidacao
from app.services.movimentacao_service import MovimentacaoService
from app.services.sugestao_categoria import sugerir_categoria
from app.utils.money import reais_para_centavos


class LancamentoPage(QWidget):
    def __init__(self, conn: sqlite3.Connection, ao_salvar=None):
        super().__init__()
        self.conn = conn
        self._ao_salvar = ao_salvar
        self._categoria_sugerida_id = None

        layout = QVBoxLayout(self)

        titulo = QLabel("Novo lançamento")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(titulo)

        formulario = QFormLayout()

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItem("Saída", "saida")
        self.combo_tipo.addItem("Entrada", "entrada")
        self.combo_tipo.currentIndexChanged.connect(self._recarregar_categorias)
        formulario.addRow("Tipo", self.combo_tipo)

        self.campo_valor = QLineEdit()
        self.campo_valor.setPlaceholderText("Ex: 25,90")
        formulario.addRow("Valor", self.campo_valor)

        self.campo_descricao = QLineEdit()
        self.campo_descricao.setPlaceholderText("Ex: Compra no Carrefour")
        self.campo_descricao.textChanged.connect(self._verificar_sugestao)
        formulario.addRow("Descrição", self.campo_descricao)

        self.rotulo_sugestao = QLabel("")
        self.rotulo_sugestao.setStyleSheet("color: #3b6fb6; font-size: 11px;")
        formulario.addRow("", self.rotulo_sugestao)

        self.combo_categoria = QComboBox()
        formulario.addRow("Categoria", self.combo_categoria)

        self.combo_conta = QComboBox()
        preencher_combo_contas(self.combo_conta, conn)
        formulario.addRow("Conta", self.combo_conta)

        self.combo_forma_pagamento = QComboBox()
        for forma in FormaPagamentoRepository(conn).list():
            self.combo_forma_pagamento.addItem(forma.nome, forma.id)
        formulario.addRow("Forma de pagamento", self.combo_forma_pagamento)

        layout.addLayout(formulario)

        self.botao_salvar = QPushButton("Salvar")
        self.botao_salvar.clicked.connect(self._salvar)
        layout.addWidget(self.botao_salvar)

        self.rotulo_status = QLabel("")
        layout.addWidget(self.rotulo_status)

        layout.addStretch()

        self._recarregar_categorias()

    def atualizar(self) -> None:
        preencher_combo_contas(self.combo_conta, self.conn)

    def _recarregar_categorias(self) -> None:
        tipo = self.combo_tipo.currentData()
        self.combo_categoria.clear()
        for categoria in CategoriaRepository(self.conn).list(tipo=tipo):
            self.combo_categoria.addItem(categoria.nome, categoria.id)

    def _verificar_sugestao(self) -> None:
        nome_sugerido = sugerir_categoria(self.campo_descricao.text())
        if not nome_sugerido:
            self.rotulo_sugestao.setText("")
            self._categoria_sugerida_id = None
            return

        indice = self.combo_categoria.findText(nome_sugerido)
        if indice == -1:
            self.rotulo_sugestao.setText("")
            self._categoria_sugerida_id = None
            return

        self._categoria_sugerida_id = self.combo_categoria.itemData(indice)
        self.rotulo_sugestao.setText(f"Sugestão: {nome_sugerido} (clique para aplicar)")
        self.rotulo_sugestao.mousePressEvent = lambda _evento: self.combo_categoria.setCurrentIndex(indice)

    def _salvar(self) -> None:
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

        service = MovimentacaoService(self.conn)
        try:
            service.registrar(
                data=date.today().isoformat(),
                tipo=self.combo_tipo.currentData(),
                descricao=self.campo_descricao.text(),
                valor=valor,
                categoria_id=categoria_id,
                conta_id=conta_id,
                forma_pagamento_id=forma_pagamento_id,
            )
        except ErroValidacao as exc:
            self._mostrar_erro(str(exc))
            return

        self.rotulo_status.setStyleSheet("color: #1a7a3c;")
        self.rotulo_status.setText("Movimentação registrada com sucesso.")
        self.campo_valor.clear()
        self.campo_descricao.clear()

        if self._ao_salvar:
            self._ao_salvar()

    def _mostrar_erro(self, mensagem: str) -> None:
        self.rotulo_status.setStyleSheet("color: #b3261e;")
        self.rotulo_status.setText(mensagem)
