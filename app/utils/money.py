from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Union


def reais_para_centavos(valor: Union[str, float, Decimal]) -> int:
    try:
        valor_decimal = Decimal(str(valor).replace(",", "."))
    except InvalidOperation as exc:
        raise ValueError(f"Valor monetário inválido: {valor!r}") from exc

    centavos = (valor_decimal * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(centavos)


def centavos_para_reais(centavos: int) -> Decimal:
    return (Decimal(centavos) / 100).quantize(Decimal("0.01"))


def formatar_moeda(centavos: int) -> str:
    valor = centavos_para_reais(centavos)
    sinal = "-" if valor < 0 else ""
    inteiro, frac = f"{abs(valor):.2f}".split(".")
    inteiro_formatado = f"{int(inteiro):,}".replace(",", ".")
    return f"{sinal}R$ {inteiro_formatado},{frac}"
