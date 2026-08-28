import sqlite3
import sys
from datetime import date
from typing import List, TypeVar

from app.database.connection import get_connection, init_db
from app.database.seed import seed_dados_iniciais
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.conta_repository import ContaRepository
from app.repositories.forma_pagamento_repository import FormaPagamentoRepository
from app.repositories.movimentacao_repository import MovimentacaoRepository
from app.services.exceptions import ErroValidacao
from app.services.movimentacao_service import MovimentacaoService
from app.services.sugestao_categoria import sugerir_categoria
from app.utils.money import formatar_moeda, reais_para_centavos

T = TypeVar("T")


def _escolher(opcoes: List[T], rotulo_attr: str = "nome") -> T:
    for indice, opcao in enumerate(opcoes, start=1):
        print(f"  {indice}. {getattr(opcao, rotulo_attr)}")
    while True:
        escolha = input("Escolha o número: ").strip()
        if escolha.isdigit() and 1 <= int(escolha) <= len(opcoes):
            return opcoes[int(escolha) - 1]
        print("Opção inválida, tente novamente.")


def novo_lancamento(conn: sqlite3.Connection) -> None:
    tipo = ""
    while tipo not in ("entrada", "saida"):
        entrada_usuario = input("Entrada ou Saída? [e/s]: ").strip().lower()
        tipo = {"e": "entrada", "s": "saida"}.get(entrada_usuario, entrada_usuario)

    valor_texto = input("Valor (ex: 25,90): ").strip()
    try:
        valor = reais_para_centavos(valor_texto)
    except ValueError as exc:
        print(f"Valor inválido: {exc}")
        return

    descricao = input("Descrição: ").strip()

    categoria_repo = CategoriaRepository(conn)
    categorias = categoria_repo.list(tipo=tipo)
    if not categorias:
        print(f"Nenhuma categoria cadastrada para '{tipo}'.")
        return

    categoria = None
    sugestao_nome = sugerir_categoria(descricao)
    if sugestao_nome:
        sugerida = next((c for c in categorias if c.nome == sugestao_nome), None)
        if sugerida:
            confirmar = input(f"Categoria sugerida: {sugerida.nome}. Usar? [S/n]: ").strip().lower()
            if confirmar in ("", "s", "sim"):
                categoria = sugerida

    if categoria is None:
        print("Categorias disponíveis:")
        categoria = _escolher(categorias)

    contas = ContaRepository(conn).list()
    if not contas:
        print("Nenhuma conta cadastrada.")
        return
    print("Contas disponíveis:")
    conta = _escolher(contas)

    formas_pagamento = FormaPagamentoRepository(conn).list()
    if not formas_pagamento:
        print("Nenhuma forma de pagamento cadastrada.")
        return
    print("Formas de pagamento disponíveis:")
    forma_pagamento = _escolher(formas_pagamento)

    service = MovimentacaoService(conn)
    try:
        mov_id = service.registrar(
            data=date.today().isoformat(),
            tipo=tipo,
            descricao=descricao,
            valor=valor,
            categoria_id=categoria.id,
            conta_id=conta.id,
            forma_pagamento_id=forma_pagamento.id,
        )
    except ErroValidacao as exc:
        print(f"Erro ao registrar: {exc}")
        return

    print(f"Movimentação #{mov_id} registrada: {formatar_moeda(valor)} em {categoria.nome}.")


def listar_movimentacoes(conn: sqlite3.Connection) -> None:
    movimentacoes = MovimentacaoRepository(conn).list()
    if not movimentacoes:
        print("Nenhuma movimentação registrada.")
        return
    categorias = {c.id: c.nome for c in CategoriaRepository(conn).list(apenas_ativas=False)}
    for mov in movimentacoes:
        sinal = "+" if mov.tipo == "entrada" else "-"
        categoria_nome = categorias.get(mov.categoria_id, "?")
        print(f"{mov.data} | {sinal}{formatar_moeda(mov.valor)} | {categoria_nome} | {mov.descricao}")


def resumo_do_mes(conn: sqlite3.Connection) -> None:
    prefixo_mes = date.today().strftime("%Y-%m")
    movimentacoes = [m for m in MovimentacaoRepository(conn).list() if m.data.startswith(prefixo_mes)]
    entradas = sum(m.valor for m in movimentacoes if m.tipo == "entrada")
    saidas = sum(m.valor for m in movimentacoes if m.tipo == "saida")
    print(f"Entradas do mês: {formatar_moeda(entradas)}")
    print(f"Saídas do mês:   {formatar_moeda(saidas)}")
    print(f"Resultado:       {formatar_moeda(entradas - saidas)}")


def main() -> None:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")

    init_db()
    conn = get_connection()
    seed_dados_iniciais(conn)

    menu = {
        "1": ("Novo lançamento", novo_lancamento),
        "2": ("Listar movimentações", listar_movimentacoes),
        "3": ("Resumo do mês", resumo_do_mes),
    }

    try:
        while True:
            print("\n=== Controle Financeiro ===")
            for chave, (rotulo, _) in menu.items():
                print(f"  {chave}. {rotulo}")
            print("  0. Sair")
            escolha = input("Escolha uma opção: ").strip()
            if escolha == "0":
                break
            item = menu.get(escolha)
            if item is None:
                print("Opção inválida.")
                continue
            item[1](conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
