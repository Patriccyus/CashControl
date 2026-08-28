import sqlite3
from typing import List

from app.models.conta import Conta
from app.repositories.conta_repository import ContaRepository
from app.services.exceptions import ErroValidacao

TIPOS_VALIDOS = {"banco", "conta_corrente", "poupanca", "dinheiro", "carteira_digital"}


class ContaService:
    def __init__(self, conn: sqlite3.Connection):
        self.repo = ContaRepository(conn)

    def criar(self, nome: str, tipo: str, saldo_inicial: int = 0) -> int:
        nome = nome.strip()
        if not nome:
            raise ErroValidacao("Nome da conta não pode ser vazio.")
        if tipo not in TIPOS_VALIDOS:
            raise ErroValidacao(f"Tipo de conta inválido: {tipo!r}.")
        return self.repo.create(Conta(nome=nome, tipo=tipo, saldo_inicial=saldo_inicial))

    def listar(self) -> List[Conta]:
        return self.repo.list()

    def desativar(self, conta_id: int) -> None:
        if self.repo.get_by_id(conta_id) is None:
            raise ErroValidacao("Conta não encontrada.")
        self.repo.desativar(conta_id)
