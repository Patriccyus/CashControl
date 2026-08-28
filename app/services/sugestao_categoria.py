import unicodedata
from typing import Dict, List, Optional

PALAVRAS_CHAVE_POR_CATEGORIA: Dict[str, List[str]] = {
    "Supermercado": ["carrefour", "supermercado", "mercado", "atacadao", "assai", "extra", "pao de acucar"],
    "Alimentação": ["restaurante", "lanchonete", "ifood", "padaria", "cafe", "bar"],
    "Moradia": ["aluguel", "condominio", "iptu"],
    "Transporte": ["uber", "99", "combustivel", "gasolina", "estacionamento", "onibus", "metro"],
    "Saúde": ["farmacia", "hospital", "medico", "consulta", "plano de saude"],
    "Educação": ["escola", "faculdade", "curso", "mensalidade"],
    "Lazer": ["cinema", "show", "viagem", "parque", "ingresso"],
    "Assinaturas": ["netflix", "spotify", "amazon prime", "youtube premium", "assinatura"],
    "Serviços": ["cabeleireiro", "manicure", "conserto", "manutencao"],
    "Salário": ["salario", "folha de pagamento"],
    "Freelance": ["freela", "freelance"],
}


def _normalizar(texto: str) -> str:
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return texto


def sugerir_categoria(descricao: str) -> Optional[str]:
    descricao_normalizada = _normalizar(descricao)
    for categoria, palavras_chave in PALAVRAS_CHAVE_POR_CATEGORIA.items():
        for palavra in palavras_chave:
            if palavra in descricao_normalizada:
                return categoria
    return None
