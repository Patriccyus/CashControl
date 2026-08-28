import sqlite3
from dataclasses import dataclass
from typing import Callable, List, Optional

from app.analytics.insights import gerar_insights
from app.analytics.orcamento_analytics import ConsumoOrcamento, calcular_consumo_orcamento
from app.models.movimentacao import Movimentacao
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.forma_pagamento_repository import FormaPagamentoRepository
from app.repositories.movimentacao_repository import FiltroMovimentacao, MovimentacaoRepository
from app.utils.datas import mes_anterior, meses_anteriores, ultimo_dia_do_mes


@dataclass
class ItemGasto:
    nome: str
    valor: int
    percentual: float


@dataclass
class MaiorCategoriaGasto:
    nome: Optional[str]
    valor: int


@dataclass
class MaiorDespesaIndividual:
    descricao: Optional[str]
    valor: int
    data: Optional[str]


@dataclass
class ResumoMensal:
    total_entradas: int
    total_saidas: int
    resultado: int
    taxa_economia: float
    maior_categoria_gasto: MaiorCategoriaGasto
    maior_despesa_individual: MaiorDespesaIndividual


@dataclass
class ComparacaoPeriodo:
    entradas: int
    saidas: int
    resultado: int


@dataclass
class ComparacaoHistorica:
    mes_anterior: ComparacaoPeriodo
    media_3_meses: ComparacaoPeriodo
    media_6_meses: ComparacaoPeriodo


@dataclass
class RelatorioMensal:
    mes: int
    ano: int
    resumo: ResumoMensal
    gastos_por_categoria: List[ItemGasto]
    gastos_por_forma_pagamento: List[ItemGasto]
    orcamento: List[ConsumoOrcamento]
    comparacao_historica: ComparacaoHistorica
    insights: List[str]


def _movimentacoes_do_mes(
    conn: sqlite3.Connection, mes: int, ano: int, tipo: Optional[str] = None
) -> List[Movimentacao]:
    data_inicio = f"{ano:04d}-{mes:02d}-01"
    data_fim = f"{ano:04d}-{mes:02d}-{ultimo_dia_do_mes(mes, ano):02d}"
    return MovimentacaoRepository(conn).list(
        FiltroMovimentacao(data_inicio=data_inicio, data_fim=data_fim, tipo=tipo, status="pago")
    )


def _totais_periodo(conn: sqlite3.Connection, mes: int, ano: int) -> ComparacaoPeriodo:
    movimentacoes = _movimentacoes_do_mes(conn, mes, ano)
    entradas = sum(m.valor for m in movimentacoes if m.tipo == "entrada")
    saidas = sum(m.valor for m in movimentacoes if m.tipo == "saida")
    return ComparacaoPeriodo(entradas=entradas, saidas=saidas, resultado=entradas - saidas)


def _media_periodos(conn: sqlite3.Connection, periodos: List[tuple]) -> ComparacaoPeriodo:
    if not periodos:
        return ComparacaoPeriodo(0, 0, 0)
    totais = [_totais_periodo(conn, mes, ano) for mes, ano in periodos]
    entradas = round(sum(t.entradas for t in totais) / len(totais))
    saidas = round(sum(t.saidas for t in totais) / len(totais))
    return ComparacaoPeriodo(entradas=entradas, saidas=saidas, resultado=entradas - saidas)


def _agrupar_por(
    movimentacoes: List[Movimentacao], chave_para_nome: Callable[[Movimentacao], str]
) -> List[ItemGasto]:
    totais: dict = {}
    for mov in movimentacoes:
        nome = chave_para_nome(mov)
        totais[nome] = totais.get(nome, 0) + mov.valor
    total_geral = sum(totais.values())
    itens = [
        ItemGasto(nome=nome, valor=valor, percentual=(valor / total_geral * 100) if total_geral else 0.0)
        for nome, valor in totais.items()
    ]
    itens.sort(key=lambda item: item.valor, reverse=True)
    return itens


def gerar_relatorio_mensal(conn: sqlite3.Connection, mes: int, ano: int) -> RelatorioMensal:
    movimentacoes_saida = _movimentacoes_do_mes(conn, mes, ano, tipo="saida")
    movimentacoes_entrada = _movimentacoes_do_mes(conn, mes, ano, tipo="entrada")

    total_entradas = sum(m.valor for m in movimentacoes_entrada)
    total_saidas = sum(m.valor for m in movimentacoes_saida)
    resultado = total_entradas - total_saidas
    taxa_economia = (resultado / total_entradas * 100) if total_entradas > 0 else 0.0

    categorias = {c.id: c.nome for c in CategoriaRepository(conn).list(apenas_ativas=False)}
    formas_pagamento = {f.id: f.nome for f in FormaPagamentoRepository(conn).list(apenas_ativas=False)}

    gastos_por_categoria = _agrupar_por(movimentacoes_saida, lambda m: categorias.get(m.categoria_id, "?"))
    gastos_por_forma_pagamento = _agrupar_por(
        movimentacoes_saida, lambda m: formas_pagamento.get(m.forma_pagamento_id, "?")
    )

    if gastos_por_categoria:
        maior_categoria_gasto = MaiorCategoriaGasto(
            nome=gastos_por_categoria[0].nome, valor=gastos_por_categoria[0].valor
        )
    else:
        maior_categoria_gasto = MaiorCategoriaGasto(nome=None, valor=0)

    if movimentacoes_saida:
        maior_mov = max(movimentacoes_saida, key=lambda m: m.valor)
        maior_despesa_individual = MaiorDespesaIndividual(
            descricao=maior_mov.descricao, valor=maior_mov.valor, data=maior_mov.data
        )
    else:
        maior_despesa_individual = MaiorDespesaIndividual(descricao=None, valor=0, data=None)

    resumo = ResumoMensal(
        total_entradas=total_entradas,
        total_saidas=total_saidas,
        resultado=resultado,
        taxa_economia=taxa_economia,
        maior_categoria_gasto=maior_categoria_gasto,
        maior_despesa_individual=maior_despesa_individual,
    )

    mes_ant, ano_ant = mes_anterior(mes, ano)
    comparacao_historica = ComparacaoHistorica(
        mes_anterior=_totais_periodo(conn, mes_ant, ano_ant),
        media_3_meses=_media_periodos(conn, meses_anteriores(mes, ano, 3)),
        media_6_meses=_media_periodos(conn, meses_anteriores(mes, ano, 6)),
    )

    return RelatorioMensal(
        mes=mes,
        ano=ano,
        resumo=resumo,
        gastos_por_categoria=gastos_por_categoria,
        gastos_por_forma_pagamento=gastos_por_forma_pagamento,
        orcamento=calcular_consumo_orcamento(conn, mes, ano),
        comparacao_historica=comparacao_historica,
        insights=gerar_insights(conn, mes, ano),
    )
