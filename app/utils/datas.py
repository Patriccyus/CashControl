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


def mes_seguinte(mes: int, ano: int) -> Tuple[int, int]:
    return (1, ano + 1) if mes == 12 else (mes + 1, ano)


def meses_anteriores(mes: int, ano: int, quantidade: int) -> List[Tuple[int, int]]:
    resultado = []
    mes_atual, ano_atual = mes, ano
    for _ in range(quantidade):
        mes_atual, ano_atual = mes_anterior(mes_atual, ano_atual)
        resultado.append((mes_atual, ano_atual))
    return resultado


def _ano_bissexto(ano: int) -> bool:
    return ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0)


def avancar_data(data_iso: str, frequencia: str) -> str:
    data = date.fromisoformat(data_iso)

    if frequencia == "diaria":
        nova_data = data + timedelta(days=1)
    elif frequencia == "semanal":
        nova_data = data + timedelta(days=7)
    elif frequencia == "mensal":
        mes, ano = data.month + 1, data.year
        if mes == 13:
            mes, ano = 1, ano + 1
        dia = min(data.day, ultimo_dia_do_mes(mes, ano))
        nova_data = date(ano, mes, dia)
    elif frequencia == "anual":
        ano = data.year + 1
        dia = data.day
        if data.month == 2 and dia == 29 and not _ano_bissexto(ano):
            dia = 28
        nova_data = date(ano, data.month, dia)
    else:
        raise ValueError(f"Frequência inválida: {frequencia!r}.")

    return nova_data.isoformat()
