from dataclasses import dataclass
from typing import Optional


@dataclass
class Recorrencia:
    descricao: str
    valor: int
    categoria_id: int
    conta_id: int
    forma_pagamento_id: int
    frequencia: str
    proxima_data: str
    id: Optional[int] = None
    data_fim: Optional[str] = None
    ativo: bool = True
