from dataclasses import dataclass
from typing import Optional


@dataclass
class Orcamento:
    categoria_id: int
    mes: int
    ano: int
    limite: int
    id: Optional[int] = None
