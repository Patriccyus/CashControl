import sqlite3
from typing import List

from app.models.orcamento import Orcamento
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.orcamento_repository import OrcamentoRepository
from app.services.exceptions import ErroValidacao


class OrcamentoService:
    def __init__(self, conn: sqlite3.Connection):
        self.repo = OrcamentoRepository(conn)
        self.categorias = CategoriaRepository(conn)

    def definir_limite(self, categoria_id: int, mes: int, ano: int, limite: int) -> int:
        categoria = self.categorias.get_by_id(categoria_id)
        if categoria is None or not categoria.ativo:
            raise ErroValidacao("Categoria inválida ou inativa.")
        if categoria.tipo != "saida":
            raise ErroValidacao("Orçamento só pode ser definido para categorias de saída.")
        if not (1 <= mes <= 12):
            raise ErroValidacao(f"Mês inválido: {mes!r}.")
        if limite < 0:
            raise ErroValidacao("Limite não pode ser negativo.")

        existentes = self.repo.list_por_mes(mes, ano)
        existente = next((o for o in existentes if o.categoria_id == categoria_id), None)
        if existente:
            existente.limite = limite
            self.repo.update(existente)
            return existente.id
        return self.repo.create(Orcamento(categoria_id=categoria_id, mes=mes, ano=ano, limite=limite))

    def listar_por_mes(self, mes: int, ano: int) -> List[Orcamento]:
        return self.repo.list_por_mes(mes, ano)
