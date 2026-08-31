import hashlib
import secrets
from typing import Tuple

ITERACOES = 100_000


def gerar_hash(senha: str) -> Tuple[str, str]:
    salt = secrets.token_hex(16)
    return _derivar(senha, salt), salt


def verificar_senha(senha: str, hash_esperado: str, salt: str) -> bool:
    return secrets.compare_digest(_derivar(senha, salt), hash_esperado)


def _derivar(senha: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), bytes.fromhex(salt), ITERACOES).hex()
