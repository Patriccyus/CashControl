import sqlite3
from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Tuple

from app.models.compra_cartao import ItemParcelaFatura
from app.repositories.cartao_repository import CartaoRepository
from app.repositories.compra_cartao_repository import CompraCartaoRepository
from app.repositories.fatura_paga_repository import FaturaPagaRepository
from app.utils.datas import mes_seguinte, ultimo_dia_do_mes


@dataclass
class FaturaCartao:
    cartao_id: int
    mes: int
    ano: int
    itens: List[ItemParcelaFatura]
    valor_total: int
    data_fechamento: str
    data_vencimento: str
    status: str


def data_fechamento_fatura(dia_fechamento: int, mes: int, ano: int) -> date:
    dia = min(dia_fechamento, ultimo_dia_do_mes(mes, ano))
    return date(ano, mes, dia)


def data_vencimento_fatura(dia_vencimento: int, mes: int, ano: int) -> date:
    mes_venc, ano_venc = mes_seguinte(mes, ano)
    dia = min(dia_vencimento, ultimo_dia_do_mes(mes_venc, ano_venc))
    return date(ano_venc, mes_venc, dia)


def mes_fatura_da_compra(data_compra: date, dia_fechamento: int) -> Tuple[int, int]:
    if data_compra.day < dia_fechamento:
        return data_compra.month, data_compra.year
    return mes_seguinte(data_compra.month, data_compra.year)


def calcular_fatura(
    conn: sqlite3.Connection, cartao_id: int, mes: int, ano: int, referencia: Optional[date] = None
) -> FaturaCartao:
    referencia = referencia or date.today()
    cartao = CartaoRepository(conn).get_by_id(cartao_id)
    itens = CompraCartaoRepository(conn).parcelas_por_fatura(cartao_id, mes, ano)
    valor_total = sum(item.valor for item in itens)

    fechamento = data_fechamento_fatura(cartao.dia_fechamento, mes, ano)
    vencimento = data_vencimento_fatura(cartao.dia_vencimento, mes, ano)

    if FaturaPagaRepository(conn).get(cartao_id, mes, ano) is not None:
        status = "paga"
    elif referencia < fechamento:
        status = "aberta"
    else:
        status = "fechada"

    return FaturaCartao(
        cartao_id=cartao_id,
        mes=mes,
        ano=ano,
        itens=itens,
        valor_total=valor_total,
        data_fechamento=fechamento.isoformat(),
        data_vencimento=vencimento.isoformat(),
        status=status,
    )


def total_despesas_futuras_cartoes(conn: sqlite3.Connection) -> int:
    total = 0
    for cartao in CartaoRepository(conn).list(apenas_ativos=True):
        periodos_pagos = FaturaPagaRepository(conn).periodos_pagos(cartao.id)
        total += CompraCartaoRepository(conn).total_em_aberto(cartao.id, periodos_pagos)
    return total


def projecao_futura(
    conn: sqlite3.Connection, cartao_id: int, meses: int = 6, referencia: Optional[date] = None
) -> List[FaturaCartao]:
    referencia = referencia or date.today()
    periodos = CompraCartaoRepository(conn).parcelas_futuras_por_periodo(cartao_id)
    periodos_pagos = FaturaPagaRepository(conn).periodos_pagos(cartao_id)

    periodos_em_aberto = sorted(
        {(mes, ano) for mes, ano, _ in periodos if (mes, ano) not in periodos_pagos},
        key=lambda periodo: (periodo[1], periodo[0]),
    )

    return [calcular_fatura(conn, cartao_id, mes, ano, referencia) for mes, ano in periodos_em_aberto[:meses]]
