import sqlite3
from dataclasses import dataclass
from typing import List

from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.movimentacao_repository import FiltroMovimentacao, MovimentacaoRepository
from app.repositories.orcamento_repository import OrcamentoRepository
from app.utils.datas import ultimo_dia_do_mes

LIMIAR_PROXIMO = 80.0


@dataclass
class ConsumoOrcamento:
    categoria_id: int
    categoria_nome: str
    limite: int
    gasto: int
    percentual: float
    restante: int
    situacao: str


def calcular_consumo_orcamento(conn: sqlite3.Connection, mes: int, ano: int) -> List[ConsumoOrcamento]:
    orcamentos = OrcamentoRepository(conn).list_por_mes(mes, ano)
    if not orcamentos:
        return []

    categorias_repo = CategoriaRepository(conn)
    movimentacao_repo = MovimentacaoRepository(conn)

    data_inicio = f"{ano:04d}-{mes:02d}-01"
    data_fim = f"{ano:04d}-{mes:02d}-{ultimo_dia_do_mes(mes, ano):02d}"

    resultado = []
    for orcamento in orcamentos:
        categoria = categorias_repo.get_by_id(orcamento.categoria_id)
        nome = categoria.nome if categoria else "?"

        movimentacoes = movimentacao_repo.list(
            FiltroMovimentacao(
                data_inicio=data_inicio,
                data_fim=data_fim,
                categoria_id=orcamento.categoria_id,
                tipo="saida",
            )
        )
        gasto = sum(m.valor for m in movimentacoes)
        percentual = (gasto / orcamento.limite * 100) if orcamento.limite > 0 else 0.0

        if percentual > 100:
            situacao = "ultrapassado"
        elif percentual >= LIMIAR_PROXIMO:
            situacao = "proximo"
        else:
            situacao = "dentro"

        resultado.append(
            ConsumoOrcamento(
                categoria_id=orcamento.categoria_id,
                categoria_nome=nome,
                limite=orcamento.limite,
                gasto=gasto,
                percentual=percentual,
                restante=orcamento.limite - gasto,
                situacao=situacao,
            )
        )

    return resultado
