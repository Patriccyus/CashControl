from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
)

from app.models.perfil import Perfil
from app.services.exceptions import ErroValidacao
from app.services.perfil_service import PerfilService


class LoginWindow(QDialog):
    def __init__(self, perfil_service: PerfilService, parent=None):
        super().__init__(parent)
        self.perfil_service = perfil_service
        self.perfil_autenticado: Optional[Perfil] = None
        self.caminho_banco: Optional[Path] = None

        self.setWindowTitle("Controle Financeiro — Entrar")
        self.resize(360, 460)

        layout = QVBoxLayout(self)

        titulo = QLabel("Quem é você?")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(titulo)

        self.lista_perfis = QListWidget()
        self._recarregar_lista()
        self.lista_perfis.itemDoubleClicked.connect(lambda _item: self._tentar_entrar())
        layout.addWidget(self.lista_perfis)

        self.campo_senha = QLineEdit()
        self.campo_senha.setPlaceholderText("Senha")
        self.campo_senha.setEchoMode(QLineEdit.EchoMode.Password)
        self.campo_senha.returnPressed.connect(self._tentar_entrar)
        layout.addWidget(self.campo_senha)

        botao_entrar = QPushButton("Entrar")
        botao_entrar.clicked.connect(self._tentar_entrar)
        layout.addWidget(botao_entrar)

        self.rotulo_erro = QLabel("")
        self.rotulo_erro.setStyleSheet("color: #b3261e;")
        layout.addWidget(self.rotulo_erro)

        separador = QLabel("——— ou crie um novo perfil ———")
        separador.setStyleSheet("color: #666; margin-top: 10px;")
        layout.addWidget(separador)

        formulario_novo = QFormLayout()
        self.campo_novo_nome = QLineEdit()
        formulario_novo.addRow("Nome", self.campo_novo_nome)

        self.campo_nova_senha = QLineEdit()
        self.campo_nova_senha.setEchoMode(QLineEdit.EchoMode.Password)
        formulario_novo.addRow("Senha", self.campo_nova_senha)

        self.campo_confirmar_senha = QLineEdit()
        self.campo_confirmar_senha.setEchoMode(QLineEdit.EchoMode.Password)
        formulario_novo.addRow("Confirmar senha", self.campo_confirmar_senha)
        layout.addLayout(formulario_novo)

        botao_criar = QPushButton("Criar perfil")
        botao_criar.clicked.connect(self._criar_perfil)
        layout.addWidget(botao_criar)

    def _recarregar_lista(self) -> None:
        self.lista_perfis.clear()
        for perfil in self.perfil_service.listar_perfis():
            self.lista_perfis.addItem(perfil.nome)

    def _tentar_entrar(self) -> None:
        self.rotulo_erro.setText("")
        item_selecionado = self.lista_perfis.currentItem()
        if item_selecionado is None:
            self.rotulo_erro.setText("Selecione um perfil na lista.")
            return

        try:
            perfil = self.perfil_service.autenticar(item_selecionado.text(), self.campo_senha.text())
        except ErroValidacao as exc:
            self.rotulo_erro.setText(str(exc))
            return

        self._concluir_login(perfil)

    def _criar_perfil(self) -> None:
        self.rotulo_erro.setText("")
        senha = self.campo_nova_senha.text()
        if senha != self.campo_confirmar_senha.text():
            self.rotulo_erro.setText("As senhas não coincidem.")
            return

        try:
            perfil = self.perfil_service.criar_perfil(self.campo_novo_nome.text(), senha)
        except ErroValidacao as exc:
            self.rotulo_erro.setText(str(exc))
            return

        self._concluir_login(perfil)

    def _concluir_login(self, perfil: Perfil) -> None:
        self.perfil_autenticado = perfil
        self.caminho_banco = self.perfil_service.caminho_banco_do_perfil(perfil.nome)
        self.accept()
