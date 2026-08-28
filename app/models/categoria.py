from dataclasses import dataclass
from typing import Optional


@dataclass
class Categoria:
    nome: str
    tipo: str
    id: Optional[int] = None
    ativo: bool = True
    categoria_pai_id: Optional[int] = None
