from datetime import date, timedelta
from typing import List, Tuple


def ultimo_dia_do_mes(mes: int, ano: int) -> int:
    if mes == 12:
        proximo_ano, proximo_mes = ano + 1, 1
    else:
        proximo_ano, proximo_mes = ano, mes + 1
    return (date(proximo_ano, proximo_mes, 1) - timedelta(days=1)).day


def mes_anterior(mes: int, ano: int) -> Tuple[int, int]:
    return (12, ano - 1) if mes == 1 else (mes - 1, ano)


def meses_anteriores(mes: int, ano: int, quantidade: int) -> List[Tuple[int, int]]:
    resultado = []
    mes_atual, ano_atual = mes, ano
    for _ in range(quantidade):
        mes_atual, ano_atual = mes_anterior(mes_atual, ano_atual)
        resultado.append((mes_atual, ano_atual))
    return resultado
