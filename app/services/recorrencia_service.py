import sqlite3
from datetime import date
from typing import List, Optional

from app.models.movimentacao import Movimentacao
from app.models.recorrencia import Recorrencia
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.conta_repository import ContaRepository
from app.repositories.forma_pagamento_repository import FormaPagamentoRepository
from app.repositories.movimentacao_repository import MovimentacaoRepository
from app.repositories.recorrencia_repository import RecorrenciaRepository
from app.services.exceptions import ErroValidacao
from app.utils.datas import avancar_data

FREQUENCIAS_VALIDAS = {"diaria", "semanal", "mensal", "anual"}


class RecorrenciaService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.repo = RecorrenciaRepository(conn)
        self.categorias = CategoriaRepository(conn)
        self.contas = ContaRepository(conn)
        self.formas_pagamento = FormaPagamentoRepository(conn)
        self.movimentacoes = MovimentacaoRepository(conn)

    def criar(
        self,
        descricao: str,
        valor: int,
        categoria_id: int,
        conta_id: int,
        forma_pagamento_id: int,
        frequencia: str,
        data_inicio: str,
        data_fim: Optional[str] = None,
    ) -> int:
        if not descricao or not descricao.strip():
            raise ErroValidacao("Descrição não pode ser vazia.")
        if valor <= 0:
            raise ErroValidacao("Valor deve ser maior que zero.")
        if frequencia not in FREQUENCIAS_VALIDAS:
            raise ErroValidacao(f"Frequência inválida: {frequencia!r}.")

        categoria = self.categorias.get_by_id(categoria_id)
        if categoria is None or not categoria.ativo:
            raise ErroValidacao("Categoria inválida ou inativa.")

        conta = self.contas.get_by_id(conta_id)
        if conta is None or not conta.ativo:
            raise ErroValidacao("Conta inválida ou inativa.")

        forma_pagamento = self.formas_pagamento.get_by_id(forma_pagamento_id)
        if forma_pagamento is None or not forma_pagamento.ativo:
            raise ErroValidacao("Forma de pagamento inválida ou inativa.")

        try:
            data_inicio_convertida = date.fromisoformat(data_inicio)
        except ValueError as exc:
            raise ErroValidacao(f"Data de início inválida: {data_inicio!r}.") from exc

        if data_fim:
            try:
                data_fim_convertida = date.fromisoformat(data_fim)
            except ValueError as exc:
                raise ErroValidacao(f"Data de término inválida: {data_fim!r}.") from exc
            if data_fim_convertida < data_inicio_convertida:
                raise ErroValidacao("Data de término não pode ser anterior à data de início.")

        return self.repo.create(
            Recorrencia(
                descricao=descricao.strip(),
                valor=valor,
                categoria_id=categoria_id,
                conta_id=conta_id,
                forma_pagamento_id=forma_pagamento_id,
                frequencia=frequencia,
                proxima_data=data_inicio,
                data_fim=data_fim,
            )
        )

    def listar(self, apenas_ativas: bool = True) -> List[Recorrencia]:
        return self.repo.list(apenas_ativas=apenas_ativas)

    def desativar(self, recorrencia_id: int) -> None:
        if self.repo.get_by_id(recorrencia_id) is None:
            raise ErroValidacao("Recorrência não encontrada.")
        self.repo.desativar(recorrencia_id)

    def gerar_lancamentos_pendentes(self, referencia: Optional[date] = None) -> int:
        referencia = referencia or date.today()
        total_gerado = 0

        for recorrencia in self.repo.list(apenas_ativas=True):
            categoria = self.categorias.get_by_id(recorrencia.categoria_id)
            if categoria is None or not categoria.ativo:
                continue

            gerou_algum = False
            while date.fromisoformat(recorrencia.proxima_data) <= referencia:
                if recorrencia.data_fim and recorrencia.proxima_data > recorrencia.data_fim:
                    break

                self.movimentacoes.create(
                    Movimentacao(
                        data=recorrencia.proxima_data,
                        tipo=categoria.tipo,
                        descricao=recorrencia.descricao,
                        valor=recorrencia.valor,
                        categoria_id=recorrencia.categoria_id,
                        conta_id=recorrencia.conta_id,
                        forma_pagamento_id=recorrencia.forma_pagamento_id,
                        status="pendente",
                        observacao="Gerado automaticamente por recorrência.",
                    )
                )
                total_gerado += 1
                gerou_algum = True
                recorrencia.proxima_data = avancar_data(recorrencia.proxima_data, recorrencia.frequencia)

            if recorrencia.data_fim and recorrencia.proxima_data > recorrencia.data_fim:
                recorrencia.ativo = False

            if gerou_algum or not recorrencia.ativo:
                self.repo.update(recorrencia)

        return total_gerado
