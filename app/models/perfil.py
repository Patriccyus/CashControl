from dataclasses import dataclass
from typing import Optional


@dataclass
class Perfil:
    nome: str
    senha_hash: str
    salt: str
    id: Optional[int] = None
    criado_em: Optional[str] = None
