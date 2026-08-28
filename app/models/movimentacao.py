from dataclasses import dataclass
from typing import Optional


@dataclass
class Movimentacao:
    data: str
    tipo: str
    descricao: str
    valor: int
    categoria_id: int
    conta_id: int
    forma_pagamento_id: int
    id: Optional[int] = None
    subcategoria_id: Optional[int] = None
    status: str = "pago"
    observacao: Optional[str] = None
    criado_em: Optional[str] = None
    atualizado_em: Optional[str] = None
