import shutil
import sqlite3
import unicodedata
from pathlib import Path
from typing import List

from app.database.connection import DB_PATH as DB_LEGADO_PADRAO
from app.database.connection import get_connection, init_db
from app.database.perfis_connection import PERFIS_DB_PATH
from app.database.seed import seed_dados_iniciais
from app.models.perfil import Perfil
from app.repositories.perfil_repository import PerfilRepository
from app.services.exceptions import ErroValidacao
from app.utils.senha import gerar_hash, verificar_senha

PERFIS_DIR_PADRAO = PERFIS_DB_PATH.parent / "perfis"


class PerfilService:
    def __init__(
        self,
        conn: sqlite3.Connection,
        perfis_dir: Path = PERFIS_DIR_PADRAO,
        legado_db_path: Path = DB_LEGADO_PADRAO,
    ):
        self.conn = conn
        self.repo = PerfilRepository(conn)
        self.perfis_dir = Path(perfis_dir)
        self.legado_db_path = Path(legado_db_path)

    def listar_perfis(self) -> List[Perfil]:
        return self.repo.list()

    def criar_perfil(self, nome: str, senha: str) -> Perfil:
        nome = nome.strip()
        if not nome:
            raise ErroValidacao("Nome do perfil não pode ser vazio.")
        if not senha:
            raise ErroValidacao("Senha não pode ser vazia.")
        if self.repo.get_by_nome(nome) is not None:
            raise ErroValidacao(f"Já existe um perfil chamado '{nome}'.")

        eh_primeiro_perfil = len(self.repo.list()) == 0

        hash_senha, salt = gerar_hash(senha)
        perfil = self.repo.create(Perfil(nome=nome, senha_hash=hash_senha, salt=salt))

        caminho_banco = self.caminho_banco_do_perfil(nome)
        caminho_banco.parent.mkdir(parents=True, exist_ok=True)

        if eh_primeiro_perfil and self.legado_db_path.exists() and not caminho_banco.exists():
            shutil.copy2(self.legado_db_path, caminho_banco)
        else:
            init_db(caminho_banco)
            conexao_perfil = get_connection(caminho_banco)
            try:
                seed_dados_iniciais(conexao_perfil)
            finally:
                conexao_perfil.close()

        return perfil

    def autenticar(self, nome: str, senha: str) -> Perfil:
        perfil = self.repo.get_by_nome(nome.strip())
        if perfil is None or not verificar_senha(senha, perfil.senha_hash, perfil.salt):
            raise ErroValidacao("Perfil ou senha inválidos.")
        return perfil

    def caminho_banco_do_perfil(self, nome: str) -> Path:
        return self.perfis_dir / f"{_slugify(nome)}.db"


def _slugify(nome: str) -> str:
    texto = nome.strip().lower()
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = "".join(caractere if caractere.isalnum() else "_" for caractere in texto)
    while "__" in texto:
        texto = texto.replace("__", "_")
    return texto.strip("_") or "perfil"
