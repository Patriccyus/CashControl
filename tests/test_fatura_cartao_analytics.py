from datetime import date

from app.analytics.fatura_cartao import (
    data_fechamento_fatura,
    data_vencimento_fatura,
    mes_fatura_da_compra,
)


def test_mes_fatura_da_compra_antes_do_fechamento():
    assert mes_fatura_da_compra(date(2026, 8, 10), dia_fechamento=25) == (8, 2026)


def test_mes_fatura_da_compra_no_dia_do_fechamento_ou_depois():
    assert mes_fatura_da_compra(date(2026, 8, 25), dia_fechamento=25) == (9, 2026)
    assert mes_fatura_da_compra(date(2026, 8, 28), dia_fechamento=25) == (9, 2026)


def test_mes_fatura_da_compra_vira_ano():
    assert mes_fatura_da_compra(date(2026, 12, 30), dia_fechamento=25) == (1, 2027)


def test_data_fechamento_fatura():
    assert data_fechamento_fatura(25, 8, 2026) == date(2026, 8, 25)


def test_data_vencimento_fatura_mes_seguinte():
    assert data_vencimento_fatura(5, 8, 2026) == date(2026, 9, 5)


def test_data_vencimento_fatura_vira_ano():
    assert data_vencimento_fatura(5, 12, 2026) == date(2027, 1, 5)
