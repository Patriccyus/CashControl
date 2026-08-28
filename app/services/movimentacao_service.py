import sqlite3
from datetime import date
from typing import List, Optional

from app.models.movimentacao import Movimentacao
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.conta_repository import ContaRepository
from app.repositories.forma_pagamento_repository import FormaPagamentoRepository
from app.repositories.movimentacao_repository import FiltroMovimentacao, MovimentacaoRepository
from app.services.exceptions import ErroValidacao
from app.services.sugestao_categoria import sugerir_categoria

TIPOS_VALIDOS = {"entrada", "saida"}
STATUS_VALIDOS = {"pago", "pendente"}


class MovimentacaoService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.repo = MovimentacaoRepository(conn)
        self.categorias = CategoriaRepository(conn)
        self.contas = ContaRepository(conn)
        self.formas_pagamento = FormaPagamentoRepository(conn)

    def registrar(
        self,
        data: str,
        tipo: str,
        descricao: str,
        valor: int,
        categoria_id: int,
        conta_id: int,
        forma_pagamento_id: int,
        subcategoria_id: Optional[int] = None,
        status: str = "pago",
        observacao: Optional[str] = None,
    ) -> int:
        self._validar(
            data=data,
            tipo=tipo,
            descricao=descricao,
            valor=valor,
            categoria_id=categoria_id,
            conta_id=conta_id,
            forma_pagamento_id=forma_pagamento_id,
            status=status,
        )
        return self.repo.create(
            Movimentacao(
                data=data,
                tipo=tipo,
                descricao=descricao.strip(),
                valor=valor,
                categoria_id=categoria_id,
                subcategoria_id=subcategoria_id,
                conta_id=conta_id,
                forma_pagamento_id=forma_pagamento_id,
                status=status,
                observacao=observacao,
            )
        )

    def atualizar(self, movimentacao: Movimentacao) -> None:
        if movimentacao.id is None:
            raise ErroValidacao("Movimentação sem id não pode ser atualizada.")
        if self.repo.get_by_id(movimentacao.id) is None:
            raise ErroValidacao("Movimentação não encontrada.")
        self._validar(
            data=movimentacao.data,
            tipo=movimentacao.tipo,
            descricao=movimentacao.descricao,
            valor=movimentacao.valor,
            categoria_id=movimentacao.categoria_id,
            conta_id=movimentacao.conta_id,
            forma_pagamento_id=movimentacao.forma_pagamento_id,
            status=movimentacao.status,
        )
        self.repo.update(movimentacao)

    def excluir(self, movimentacao_id: int) -> None:
        if self.repo.get_by_id(movimentacao_id) is None:
            raise ErroValidacao("Movimentação não encontrada.")
        self.repo.delete(movimentacao_id)

    def listar(self, filtro: Optional[FiltroMovimentacao] = None) -> List[Movimentacao]:
        return self.repo.list(filtro)

    def sugerir_categoria_por_descricao(self, descricao: str) -> Optional[int]:
        nome_categoria = sugerir_categoria(descricao)
        if nome_categoria is None:
            return None
        for categoria in self.categorias.list(apenas_ativas=True):
            if categoria.nome == nome_categoria:
                return categoria.id
        return None

    def _validar(
        self,
        data: str,
        tipo: str,
        descricao: str,
        valor: int,
        categoria_id: int,
        conta_id: int,
        forma_pagamento_id: int,
        status: str,
    ) -> None:
        if tipo not in TIPOS_VALIDOS:
            raise ErroValidacao(f"Tipo de movimentação inválido: {tipo!r}.")
        if status not in STATUS_VALIDOS:
            raise ErroValidacao(f"Status inválido: {status!r}.")
        if not descricao or not descricao.strip():
            raise ErroValidacao("Descrição não pode ser vazia.")
        if valor <= 0:
            raise ErroValidacao("Valor deve ser maior que zero.")
        self._validar_data(data)

        categoria = self.categorias.get_by_id(categoria_id)
        if categoria is None or not categoria.ativo:
            raise ErroValidacao("Categoria inválida ou inativa.")
        if categoria.tipo != tipo:
            raise ErroValidacao(
                f"Categoria '{categoria.nome}' é do tipo '{categoria.tipo}', "
                f"incompatível com movimentação do tipo '{tipo}'."
            )

        conta = self.contas.get_by_id(conta_id)
        if conta is None or not conta.ativo:
            raise ErroValidacao("Conta inválida ou inativa.")

        forma_pagamento = self.formas_pagamento.get_by_id(forma_pagamento_id)
        if forma_pagamento is None or not forma_pagamento.ativo:
            raise ErroValidacao("Forma de pagamento inválida ou inativa.")

    @staticmethod
    def _validar_data(data: str) -> None:
        try:
            date.fromisoformat(data)
        except ValueError as exc:
            raise ErroValidacao(f"Data inválida: {data!r}. Use o formato AAAA-MM-DD.") from exc
