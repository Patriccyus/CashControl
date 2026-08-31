import sqlite3
from typing import Optional

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

from app.interface.gui.combos import preencher_combo_contas
from app.models.movimentacao import Movimentacao
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.forma_pagamento_repository import FormaPagamentoRepository
from app.services.exceptions import ErroValidacao
from app.services.movimentacao_service import MovimentacaoService
from app.utils.money import centavos_para_reais, reais_para_centavos


class EditarMovimentacaoDialog(QDialog):
    def __init__(self, conn: sqlite3.Connection, movimentacao: Movimentacao, parent=None):
        super().__init__(parent)
        self.conn = conn
        self.movimentacao = movimentacao
        self.setWindowTitle("Editar movimentação")

        layout = QVBoxLayout(self)
        formulario = QFormLayout()

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItem("Saída", "saida")
        self.combo_tipo.addItem("Entrada", "entrada")
        self.combo_tipo.setCurrentIndex(0 if movimentacao.tipo == "saida" else 1)
        self.combo_tipo.currentIndexChanged.connect(self._recarregar_categorias)
        formulario.addRow("Tipo", self.combo_tipo)

        valor_decimal = centavos_para_reais(movimentacao.valor)
        self.campo_valor = QLineEdit(f"{valor_decimal:.2f}".replace(".", ","))
        formulario.addRow("Valor", self.campo_valor)

        self.campo_descricao = QLineEdit(movimentacao.descricao)
        formulario.addRow("Descrição", self.campo_descricao)

        self.combo_categoria = QComboBox()
        formulario.addRow("Categoria", self.combo_categoria)

        self.combo_conta = QComboBox()
        preencher_combo_contas(self.combo_conta, conn)
        indice_conta = self.combo_conta.findData(movimentacao.conta_id)
        if indice_conta >= 0:
            self.combo_conta.setCurrentIndex(indice_conta)
        formulario.addRow("Conta", self.combo_conta)

        self.combo_forma_pagamento = QComboBox()
        for forma in FormaPagamentoRepository(conn).list():
            self.combo_forma_pagamento.addItem(forma.nome, forma.id)
        indice_forma = self.combo_forma_pagamento.findData(movimentacao.forma_pagamento_id)
        if indice_forma >= 0:
            self.combo_forma_pagamento.setCurrentIndex(indice_forma)
        formulario.addRow("Forma de pagamento", self.combo_forma_pagamento)

        self.combo_status = QComboBox()
        self.combo_status.addItem("Pago/Recebido", "pago")
        self.combo_status.addItem("Pendente", "pendente")
        self.combo_status.setCurrentIndex(0 if movimentacao.status == "pago" else 1)
        formulario.addRow("Status", self.combo_status)

        layout.addLayout(formulario)

        self.rotulo_erro = QLabel("")
        self.rotulo_erro.setStyleSheet("color: #b3261e;")
        layout.addWidget(self.rotulo_erro)

        botoes = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        botoes.accepted.connect(self._salvar)
        botoes.rejected.connect(self.reject)
        layout.addWidget(botoes)

        self._recarregar_categorias(selecionar_id=movimentacao.categoria_id)

    def _recarregar_categorias(self, _indice=None, selecionar_id: Optional[int] = None) -> None:
        tipo = self.combo_tipo.currentData()
        categoria_id_atual = selecionar_id if selecionar_id is not None else self.combo_categoria.currentData()
        self.combo_categoria.clear()
        for categoria in CategoriaRepository(self.conn).list(tipo=tipo):
            self.combo_categoria.addItem(categoria.nome, categoria.id)
        indice = self.combo_categoria.findData(categoria_id_atual)
        if indice >= 0:
            self.combo_categoria.setCurrentIndex(indice)

    def _salvar(self) -> None:
        self.rotulo_erro.setText("")
        try:
            valor = reais_para_centavos(self.campo_valor.text())
        except ValueError as exc:
            self.rotulo_erro.setText(str(exc))
            return

        self.movimentacao.tipo = self.combo_tipo.currentData()
        self.movimentacao.valor = valor
        self.movimentacao.descricao = self.campo_descricao.text()
        self.movimentacao.categoria_id = self.combo_categoria.currentData()
        self.movimentacao.conta_id = self.combo_conta.currentData()
        self.movimentacao.forma_pagamento_id = self.combo_forma_pagamento.currentData()
        self.movimentacao.status = self.combo_status.currentData()

        try:
            MovimentacaoService(self.conn).atualizar(self.movimentacao)
        except ErroValidacao as exc:
            self.rotulo_erro.setText(str(exc))
            return

        self.accept()
