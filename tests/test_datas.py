from app.utils.datas import avancar_data


def test_avancar_data_diaria():
    assert avancar_data("2026-08-30", "diaria") == "2026-08-31"


def test_avancar_data_semanal():
    assert avancar_data("2026-08-01", "semanal") == "2026-08-08"


def test_avancar_data_mensal():
    assert avancar_data("2026-08-15", "mensal") == "2026-09-15"


def test_avancar_data_mensal_clampa_dia_inexistente():
    assert avancar_data("2026-01-31", "mensal") == "2026-02-28"


def test_avancar_data_mensal_vira_ano():
    assert avancar_data("2026-12-10", "mensal") == "2027-01-10"


def test_avancar_data_anual():
    assert avancar_data("2026-08-15", "anual") == "2027-08-15"


def test_avancar_data_anual_ano_bissexto_clampa():
    assert avancar_data("2024-02-29", "anual") == "2025-02-28"
