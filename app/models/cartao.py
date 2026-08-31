from dataclasses import dataclass
from typing import Optional


@dataclass
class Cartao:
    nome: str
    limite: int
    dia_fechamento: int
    dia_vencimento: int
    conta_id: int
    id: Optional[int] = None
    ativo: bool = True
