import sqlite3
from typing import Dict, List

from app.analytics.orcamento_analytics import calcular_consumo_orcamento
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.movimentacao_repository import FiltroMovimentacao, MovimentacaoRepository
from app.utils.datas import mes_anterior, meses_anteriores, ultimo_dia_do_mes

LIMIAR_CRESCIMENTO_CATEGORIA = 20.0
LIMIAR_PARTICIPACAO_CATEGORIA = 30.0


def gerar_insights(conn: sqlite3.Connection, mes: int, ano: int) -> List[str]:
    insights: List[str] = []
    insights.extend(_insight_orcamento_estourado(conn, mes, ano))
    insights.extend(_insight_crescimento_categoria(conn, mes, ano))
    insights.extend(_insight_categoria_representativa(conn, mes, ano))
    insights.extend(_insight_despesas_vs_receitas(conn, mes, ano))
    return insights


def _insight_orcamento_estourado(conn: sqlite3.Connection, mes: int, ano: int) -> List[str]:
    ultrapassadas = [c for c in calcular_consumo_orcamento(conn, mes, ano) if c.situacao == "ultrapassado"]
    if not ultrapassadas:
        return []
    if len(ultrapassadas) == 1:
        return [f"Você ultrapassou o limite planejado em {ultrapassadas[0].categoria_nome}."]
    nomes = ", ".join(c.categoria_nome for c in ultrapassadas)
    return [f"Você ultrapassou o limite planejado em {len(ultrapassadas)} categorias: {nomes}."]


def _gasto_por_categoria(conn: sqlite3.Connection, mes: int, ano: int) -> Dict[str, int]:
    data_inicio = f"{ano:04d}-{mes:02d}-01"
    data_fim = f"{ano:04d}-{mes:02d}-{ultimo_dia_do_mes(mes, ano):02d}"
    movimentacoes = MovimentacaoRepository(conn).list(
        FiltroMovimentacao(data_inicio=data_inicio, data_fim=data_fim, tipo="saida", status="pago")
    )
    categorias = {c.id: c.nome for c in CategoriaRepository(conn).list(apenas_ativas=False)}
    totais: Dict[str, int] = {}
    for mov in movimentacoes:
        nome = categorias.get(mov.categoria_id, "?")
        totais[nome] = totais.get(nome, 0) + mov.valor
    return totais


def _insight_crescimento_categoria(conn: sqlite3.Connection, mes: int, ano: int) -> List[str]:
    gasto_atual = _gasto_por_categoria(conn, mes, ano)
    if not gasto_atual:
        return []

    totais_anteriores = [_gasto_por_categoria(conn, m, a) for m, a in meses_anteriores(mes, ano, 3)]

    insights = []
    for categoria, valor_atual in gasto_atual.items():
        valores_historicos = [totais.get(categoria, 0) for totais in totais_anteriores]
        media_historica = sum(valores_historicos) / len(valores_historicos)
        if media_historica <= 0:
            continue
        crescimento = (valor_atual - media_historica) / media_historica * 100
        if crescimento >= LIMIAR_CRESCIMENTO_CATEGORIA:
            insights.append(
                f"Seus gastos com {categoria} aumentaram {crescimento:.0f}% "
                "em relação à média dos últimos 3 meses."
            )
    return insights


def _insight_categoria_representativa(conn: sqlite3.Connection, mes: int, ano: int) -> List[str]:
    gasto_atual = _gasto_por_categoria(conn, mes, ano)
    total_gastos = sum(gasto_atual.values())
    if total_gastos <= 0:
        return []

    categoria_maior, valor_maior = max(gasto_atual.items(), key=lambda item: item[1])
    percentual = valor_maior / total_gastos * 100
    if percentual >= LIMIAR_PARTICIPACAO_CATEGORIA:
        return [f"{categoria_maior} representa {percentual:.0f}% das suas despesas no período."]
    return []


def _totais_pagos_do_mes(conn: sqlite3.Connection, mes: int, ano: int):
    data_inicio = f"{ano:04d}-{mes:02d}-01"
    data_fim = f"{ano:04d}-{mes:02d}-{ultimo_dia_do_mes(mes, ano):02d}"
    movimentacoes = MovimentacaoRepository(conn).list(
        FiltroMovimentacao(data_inicio=data_inicio, data_fim=data_fim, status="pago")
    )
    entradas = sum(m.valor for m in movimentacoes if m.tipo == "entrada")
    saidas = sum(m.valor for m in movimentacoes if m.tipo == "saida")
    return entradas, saidas


def _insight_despesas_vs_receitas(conn: sqlite3.Connection, mes: int, ano: int) -> List[str]:
    mes_ant, ano_ant = mes_anterior(mes, ano)
    entradas_atual, saidas_atual = _totais_pagos_do_mes(conn, mes, ano)
    entradas_ant, saidas_ant = _totais_pagos_do_mes(conn, mes_ant, ano_ant)

    if entradas_ant <= 0 or saidas_ant <= 0:
        return []

    crescimento_entradas = (entradas_atual - entradas_ant) / entradas_ant * 100
    crescimento_saidas = (saidas_atual - saidas_ant) / saidas_ant * 100

    if crescimento_saidas > crescimento_entradas and crescimento_saidas > 0:
        if crescimento_entradas > 0:
            return ["Sua renda aumentou, mas suas despesas cresceram em proporção maior."]
        return ["Suas despesas cresceram em relação ao mês anterior, acima do crescimento da sua renda."]
    return []
