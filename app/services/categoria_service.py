import sqlite3
from typing import List, Optional

from app.models.categoria import Categoria
from app.repositories.categoria_repository import CategoriaRepository
from app.services.exceptions import ErroValidacao

TIPOS_VALIDOS = {"entrada", "saida"}


class CategoriaService:
    def __init__(self, conn: sqlite3.Connection):
        self.repo = CategoriaRepository(conn)

    def criar(self, nome: str, tipo: str, categoria_pai_id: Optional[int] = None) -> int:
        nome = nome.strip()
        if not nome:
            raise ErroValidacao("Nome da categoria não pode ser vazio.")
        if tipo not in TIPOS_VALIDOS:
            raise ErroValidacao(f"Tipo de categoria inválido: {tipo!r}.")
        if categoria_pai_id is not None and self.repo.get_by_id(categoria_pai_id) is None:
            raise ErroValidacao("Categoria pai não encontrada.")
        return self.repo.create(Categoria(nome=nome, tipo=tipo, categoria_pai_id=categoria_pai_id))

    def listar(self, tipo: Optional[str] = None) -> List[Categoria]:
        return self.repo.list(tipo=tipo)

    def desativar(self, categoria_id: int) -> None:
        if self.repo.get_by_id(categoria_id) is None:
            raise ErroValidacao("Categoria não encontrada.")
        self.repo.desativar(categoria_id)
