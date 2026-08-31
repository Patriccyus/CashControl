from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ParcelaCartao:
    compra_id: int
    numero: int
    valor: int
    fatura_mes: int
    fatura_ano: int
    id: Optional[int] = None


@dataclass
class CompraCartao:
    cartao_id: int
    categoria_id: int
    descricao: str
    data_compra: str
    valor_total: int
    numero_parcelas: int
    id: Optional[int] = None
    criado_em: Optional[str] = None
    parcelas: List[ParcelaCartao] = field(default_factory=list)


@dataclass
class ItemParcelaFatura:
    parcela_id: int
    compra_id: int
    descricao: str
    categoria_id: int
    numero: int
    numero_parcelas: int
    valor: int
