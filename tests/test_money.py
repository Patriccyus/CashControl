from app.utils.money import centavos_para_reais, formatar_moeda, reais_para_centavos


def test_reais_para_centavos():
    assert reais_para_centavos("25,90") == 2590
    assert reais_para_centavos(25.9) == 2590
    assert reais_para_centavos("1000") == 100000


def test_centavos_para_reais():
    from decimal import Decimal

    assert centavos_para_reais(2590) == Decimal("25.90")


def test_formatar_moeda():
    assert formatar_moeda(2590) == "R$ 25,90"
    assert formatar_moeda(100000) == "R$ 1.000,00"
    assert formatar_moeda(-500) == "-R$ 5,00"
