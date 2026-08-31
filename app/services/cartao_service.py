import sqlite3
from typing import List

from app.models.cartao import Cartao
from app.repositories.cartao_repository import CartaoRepository
from app.repositories.conta_repository import ContaRepository
from app.services.exceptions import ErroValidacao


class CartaoService:
    def __init__(self, conn: sqlite3.Connection):
        self.repo = CartaoRepository(conn)
        self.contas = ContaRepository(conn)

    def criar(self, nome: str, limite: int, dia_fechamento: int, dia_vencimento: int, conta_id: int) -> int:
        nome = nome.strip()
        if not nome:
            raise ErroValidacao("Nome do cartão não pode ser vazio.")
        if limite < 0:
            raise ErroValidacao("Limite não pode ser negativo.")
        if not (1 <= dia_fechamento <= 28):
            raise ErroValidacao("Dia de fechamento deve estar entre 1 e 28.")
        if not (1 <= dia_vencimento <= 28):
            raise ErroValidacao("Dia de vencimento deve estar entre 1 e 28.")

        conta = self.contas.get_by_id(conta_id)
        if conta is None or not conta.ativo:
            raise ErroValidacao("Conta inválida ou inativa.")

        return self.repo.create(
            Cartao(
                nome=nome,
                limite=limite,
                dia_fechamento=dia_fechamento,
                dia_vencimento=dia_vencimento,
                conta_id=conta_id,
            )
        )

    def listar(self, apenas_ativos: bool = True) -> List[Cartao]:
        return self.repo.list(apenas_ativos=apenas_ativos)

    def desativar(self, cartao_id: int) -> None:
        if self.repo.get_by_id(cartao_id) is None:
            raise ErroValidacao("Cartão não encontrado.")
        self.repo.desativar(cartao_id)
