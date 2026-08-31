from dataclasses import dataclass
from typing import Optional


@dataclass
class FaturaPaga:
    cartao_id: int
    mes: int
    ano: int
    valor_pago: int
    data_pagamento: str
    id: Optional[int] = None
    movimentacao_id: Optional[int] = None
