import csv
import shutil
import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import List

from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.conta_repository import ContaRepository
from app.repositories.forma_pagamento_repository import FormaPagamentoRepository
from app.repositories.movimentacao_repository import MovimentacaoRepository
from app.services.exceptions import ErroValidacao
from app.utils.money import centavos_para_reais


class BackupService:
    def __init__(self, caminho_banco: Path, pasta_backups: Path):
        self.caminho_banco = Path(caminho_banco)
        self.pasta_backups = Path(pasta_backups)

    def criar_backup(self) -> Path:
        if not self.caminho_banco.exists():
            raise ErroValidacao("Banco de dados não encontrado.")

        self.pasta_backups.mkdir(parents=True, exist_ok=True)
        agora = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho_backup = self.pasta_backups / f"backup_{agora}.db"
        shutil.copy2(self.caminho_banco, caminho_backup)
        return caminho_backup

    def ja_existe_backup_hoje(self) -> bool:
        prefixo = f"backup_{date.today().strftime('%Y%m%d')}"
        return any(caminho.stem.startswith(prefixo) for caminho in self.listar_backups())

    def listar_backups(self) -> List[Path]:
        if not self.pasta_backups.exists():
            return []
        return sorted(self.pasta_backups.glob("backup_*.db"), reverse=True)

    def restaurar_backup(self, caminho_backup: Path, conn: sqlite3.Connection) -> None:
        caminho_backup = Path(caminho_backup)
        if not caminho_backup.exists():
            raise ErroValidacao("Arquivo de backup não encontrado.")
        conn.close()
        shutil.copy2(caminho_backup, self.caminho_banco)

    def exportar_csv(self, conn: sqlite3.Connection, caminho_destino: Path) -> Path:
        caminho_destino = Path(caminho_destino)
        caminho_destino.parent.mkdir(parents=True, exist_ok=True)

        categorias = {c.id: c.nome for c in CategoriaRepository(conn).list(apenas_ativas=False)}
        contas = {c.id: c.nome for c in ContaRepository(conn).list(apenas_ativas=False)}
        formas_pagamento = {f.id: f.nome for f in FormaPagamentoRepository(conn).list(apenas_ativas=False)}
        movimentacoes = MovimentacaoRepository(conn).list()

        with open(caminho_destino, "w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(
                ["Data", "Tipo", "Descrição", "Valor", "Categoria", "Conta", "Forma de pagamento", "Status"]
            )
            for mov in movimentacoes:
                escritor.writerow(
                    [
                        mov.data,
                        "Entrada" if mov.tipo == "entrada" else "Saída",
                        mov.descricao,
                        f"{centavos_para_reais(mov.valor)}".replace(".", ","),
                        categorias.get(mov.categoria_id, "?"),
                        contas.get(mov.conta_id, "?"),
                        formas_pagamento.get(mov.forma_pagamento_id, "?"),
                        "Pago/Recebido" if mov.status == "pago" else "Pendente",
                    ]
                )

        return caminho_destino
