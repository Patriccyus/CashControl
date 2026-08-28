from dataclasses import dataclass
from typing import Optional


@dataclass
class Conta:
    nome: str
    tipo: str
    id: Optional[int] = None
    saldo_inicial: int = 0
    ativo: bool = True
