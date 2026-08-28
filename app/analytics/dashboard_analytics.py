import sqlite3
from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Tuple

from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.conta_repository import ContaRepository
from app.repositories.movimentacao_repository import FiltroMovimentacao, MovimentacaoRepository


@dataclass
class ResumoDashboard:
    saldo_atual: int
    entradas_mes: int
    saidas_mes: int
    resultado_mes: int
    quantidade_pendentes: int
    valor_pendente: int
    percentual_renda_comprometida: float


def calcular_resumo_dashboard(conn: sqlite3.Connection, referencia: Optional[date] = None) -> ResumoDashboard:
    referencia = referencia or date.today()
    prefixo_mes = referencia.strftime("%Y-%m")

    saldo_inicial_total = sum(c.saldo_inicial for c in ContaRepository(conn).list(apenas_ativas=False))

    movimentacoes_pagas = MovimentacaoRepository(conn).list(FiltroMovimentacao(status="pago"))
    total_entradas = sum(m.valor for m in movimentacoes_pagas if m.tipo == "entrada")
    total_saidas = sum(m.valor for m in movimentacoes_pagas if m.tipo == "saida")
    saldo_atual = saldo_inicial_total + total_entradas - total_saidas

    movimentacoes_mes = [m for m in movimentacoes_pagas if m.data.startswith(prefixo_mes)]
    entradas_mes = sum(m.valor for m in movimentacoes_mes if m.tipo == "entrada")
    saidas_mes = sum(m.valor for m in movimentacoes_mes if m.tipo == "saida")

    pendentes = MovimentacaoRepository(conn).list(FiltroMovimentacao(status="pendente"))
    valor_pendente = sum(m.valor for m in pendentes)

    percentual_renda_comprometida = (saidas_mes / entradas_mes * 100) if entradas_mes > 0 else 0.0

    return ResumoDashboard(
        saldo_atual=saldo_atual,
        entradas_mes=entradas_mes,
        saidas_mes=saidas_mes,
        resultado_mes=entradas_mes - saidas_mes,
        quantidade_pendentes=len(pendentes),
        valor_pendente=valor_pendente,
        percentual_renda_comprometida=percentual_renda_comprometida,
    )


def entradas_saidas_por_mes(
    conn: sqlite3.Connection, meses: int = 6, referencia: Optional[date] = None
) -> List[Tuple[str, int, int]]:
    referencia = referencia or date.today()
    ano, mes = referencia.year, referencia.month
    periodos = []
    for _ in range(meses):
        periodos.append((ano, mes))
        mes -= 1
        if mes == 0:
            mes, ano = 12, ano - 1
    periodos.reverse()

    movimentacoes = MovimentacaoRepository(conn).list(FiltroMovimentacao(status="pago"))

    resultado = []
    for ano_periodo, mes_periodo in periodos:
        prefixo = f"{ano_periodo:04d}-{mes_periodo:02d}"
        do_periodo = [m for m in movimentacoes if m.data.startswith(prefixo)]
        entradas = sum(m.valor for m in do_periodo if m.tipo == "entrada")
        saidas = sum(m.valor for m in do_periodo if m.tipo == "saida")
        resultado.append((prefixo, entradas, saidas))
    return resultado


def gastos_por_categoria_do_mes(
    conn: sqlite3.Connection, referencia: Optional[date] = None, top_n: int = 8
) -> List[Tuple[str, int]]:
    referencia = referencia or date.today()
    prefixo_mes = referencia.strftime("%Y-%m")

    movimentacoes = MovimentacaoRepository(conn).list(
        FiltroMovimentacao(
            data_inicio=f"{prefixo_mes}-01",
            data_fim=f"{prefixo_mes}-31",
            tipo="saida",
            status="pago",
        )
    )
    categorias = {c.id: c.nome for c in CategoriaRepository(conn).list(apenas_ativas=False)}

    totais: dict = {}
    for mov in movimentacoes:
        nome = categorias.get(mov.categoria_id, "?")
        totais[nome] = totais.get(nome, 0) + mov.valor

    return sorted(totais.items(), key=lambda item: item[1], reverse=True)[:top_n]
