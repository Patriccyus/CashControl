import sqlite3
from typing import List

from app.models.forma_pagamento import FormaPagamento
from app.repositories.forma_pagamento_repository import FormaPagamentoRepository
from app.services.exceptions import ErroValidacao

TIPOS_VALIDOS = {"pix", "debito", "credito", "dinheiro", "boleto", "transferencia"}


class FormaPagamentoService:
    def __init__(self, conn: sqlite3.Connection):
        self.repo = FormaPagamentoRepository(conn)

    def criar(self, nome: str, tipo: str) -> int:
        nome = nome.strip()
        if not nome:
            raise ErroValidacao("Nome da forma de pagamento não pode ser vazio.")
        if tipo not in TIPOS_VALIDOS:
            raise ErroValidacao(f"Tipo de forma de pagamento inválido: {tipo!r}.")
        return self.repo.create(FormaPagamento(nome=nome, tipo=tipo))

    def listar(self) -> List[FormaPagamento]:
        return self.repo.list()

    def desativar(self, forma_pagamento_id: int) -> None:
        if self.repo.get_by_id(forma_pagamento_id) is None:
            raise ErroValidacao("Forma de pagamento não encontrada.")
        self.repo.desativar(forma_pagamento_id)
