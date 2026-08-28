from dataclasses import dataclass
from typing import Optional


@dataclass
class FormaPagamento:
    nome: str
    tipo: str
    id: Optional[int] = None
    ativo: bool = True
