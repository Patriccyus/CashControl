from dataclasses import dataclass
from typing import Optional


@dataclass
class Recorrencia:
    descricao: str
    valor: int
    categoria_id: int
    frequencia: str
    proxima_data: str
    id: Optional[int] = None
    ativo: bool = True
