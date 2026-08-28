import sqlite3
import sys
from datetime import date
from pathlib import Path
from typing import List, Optional, TypeVar

from app.analytics.orcamento_analytics import calcular_consumo_orcamento
from app.analytics.relatorio_mensal import gerar_relatorio_mensal
from app.database.connection import get_connection, init_db
from app.database.seed import seed_dados_iniciais
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.conta_repository import ContaRepository
from app.repositories.forma_pagamento_repository import FormaPagamentoRepository
from app.repositories.movimentacao_repository import FiltroMovimentacao, MovimentacaoRepository
from app.reports.relatorio_pdf import gerar_pdf_relatorio_mensal
from app.services.exceptions import ErroValidacao
from app.services.movimentacao_service import MovimentacaoService
from app.services.orcamento_service import OrcamentoService
from app.services.sugestao_categoria import sugerir_categoria
from app.utils.money import formatar_moeda, reais_para_centavos

T = TypeVar("T")

PASTA_RELATORIOS = Path(__file__).resolve().parents[2] / "reports"

ROTULOS_SITUACAO = {
    "dentro": "dentro do limite",
    "proximo": "próximo do limite",
    "ultrapassado": "limite ultrapassado",
}

NOMES_MESES = [
    "",
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]


def _escolher(opcoes: List[T], rotulo_attr: str = "nome") -> T:
    for indice, opcao in enumerate(opcoes, start=1):
        print(f"  {indice}. {getattr(opcao, rotulo_attr)}")
    while True:
        escolha = input("Escolha o número: ").strip()
        if escolha.isdigit() and 1 <= int(escolha) <= len(opcoes):
            return opcoes[int(escolha) - 1]
        print("Opção inválida, tente novamente.")


def _perguntar_opcional(rotulo: str) -> Optional[str]:
    valor = input(f"{rotulo} (Enter para pular): ").strip()
    return valor or None


def _imprimir_movimentacoes(conn: sqlite3.Connection, movimentacoes: list) -> None:
    categorias = {c.id: c.nome for c in CategoriaRepository(conn).list(apenas_ativas=False)}
    for mov in movimentacoes:
        sinal = "+" if mov.tipo == "entrada" else "-"
        categoria_nome = categorias.get(mov.categoria_id, "?")
        print(f"{mov.data} | {sinal}{formatar_moeda(mov.valor)} | {categoria_nome} | {mov.status} | {mov.descricao}")


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
    _imprimir_movimentacoes(conn, movimentacoes)


def historico_com_filtros(conn: sqlite3.Connection) -> None:
    data_inicio = _perguntar_opcional("Data início (AAAA-MM-DD)")
    data_fim = _perguntar_opcional("Data fim (AAAA-MM-DD)")

    tipo = _perguntar_opcional("Tipo (entrada/saida)")
    while tipo not in (None, "entrada", "saida"):
        print("Tipo inválido.")
        tipo = _perguntar_opcional("Tipo (entrada/saida)")

    categoria_id = None
    categorias = CategoriaRepository(conn).list(tipo=tipo, apenas_ativas=False)
    if categorias and input("Filtrar por categoria? [s/N]: ").strip().lower() == "s":
        categoria_id = _escolher(categorias).id

    conta_id = None
    contas = ContaRepository(conn).list()
    if contas and input("Filtrar por conta? [s/N]: ").strip().lower() == "s":
        conta_id = _escolher(contas).id

    forma_pagamento_id = None
    formas_pagamento = FormaPagamentoRepository(conn).list()
    if formas_pagamento and input("Filtrar por forma de pagamento? [s/N]: ").strip().lower() == "s":
        forma_pagamento_id = _escolher(formas_pagamento).id

    status = _perguntar_opcional("Status (pago/pendente)")
    while status not in (None, "pago", "pendente"):
        print("Status inválido.")
        status = _perguntar_opcional("Status (pago/pendente)")

    busca_texto = _perguntar_opcional("Buscar por texto na descrição")

    filtro = FiltroMovimentacao(
        data_inicio=data_inicio,
        data_fim=data_fim,
        categoria_id=categoria_id,
        tipo=tipo,
        forma_pagamento_id=forma_pagamento_id,
        conta_id=conta_id,
        status=status,
        busca_texto=busca_texto,
    )

    movimentacoes = MovimentacaoRepository(conn).list(filtro)
    if not movimentacoes:
        print("Nenhuma movimentação encontrada com esses filtros.")
        return
    _imprimir_movimentacoes(conn, movimentacoes)


def definir_orcamento(conn: sqlite3.Connection) -> None:
    categorias = CategoriaRepository(conn).list(tipo="saida")
    if not categorias:
        print("Nenhuma categoria de saída cadastrada.")
        return
    print("Categoria:")
    categoria = _escolher(categorias)

    hoje = date.today()
    mes_texto = input(f"Mês [1-12] (Enter para {hoje.month}): ").strip()
    mes = int(mes_texto) if mes_texto else hoje.month
    ano_texto = input(f"Ano (Enter para {hoje.year}): ").strip()
    ano = int(ano_texto) if ano_texto else hoje.year

    limite_texto = input("Limite mensal (ex: 500,00): ").strip()
    try:
        limite = reais_para_centavos(limite_texto)
    except ValueError as exc:
        print(f"Valor inválido: {exc}")
        return

    try:
        OrcamentoService(conn).definir_limite(categoria.id, mes, ano, limite)
    except ErroValidacao as exc:
        print(f"Erro: {exc}")
        return

    print(f"Orçamento de {categoria.nome} para {mes:02d}/{ano} definido em {formatar_moeda(limite)}.")


def ver_orcamento_do_mes(conn: sqlite3.Connection) -> None:
    hoje = date.today()
    consumo = calcular_consumo_orcamento(conn, hoje.month, hoje.year)
    if not consumo:
        print("Nenhum orçamento definido para este mês.")
        return

    for item in consumo:
        print(
            f"{item.categoria_nome}: {formatar_moeda(item.gasto)} de {formatar_moeda(item.limite)} "
            f"({item.percentual:.0f}%) — {ROTULOS_SITUACAO[item.situacao]}"
        )


def resumo_do_mes(conn: sqlite3.Connection) -> None:
    prefixo_mes = date.today().strftime("%Y-%m")
    movimentacoes = [m for m in MovimentacaoRepository(conn).list() if m.data.startswith(prefixo_mes)]
    entradas = sum(m.valor for m in movimentacoes if m.tipo == "entrada")
    saidas = sum(m.valor for m in movimentacoes if m.tipo == "saida")
    print(f"Entradas do mês: {formatar_moeda(entradas)}")
    print(f"Saídas do mês:   {formatar_moeda(saidas)}")
    print(f"Resultado:       {formatar_moeda(entradas - saidas)}")


def gerar_relatorio_do_mes(conn: sqlite3.Connection) -> None:
    hoje = date.today()
    mes_texto = input(f"Mês [1-12] (Enter para {hoje.month}): ").strip()
    mes = int(mes_texto) if mes_texto else hoje.month
    ano_texto = input(f"Ano (Enter para {hoje.year}): ").strip()
    ano = int(ano_texto) if ano_texto else hoje.year

    relatorio = gerar_relatorio_mensal(conn, mes, ano)
    resumo = relatorio.resumo

    print(f"\n=== Relatório de {NOMES_MESES[mes]}/{ano} ===")
    print(f"Entradas: {formatar_moeda(resumo.total_entradas)}")
    print(f"Saídas:   {formatar_moeda(resumo.total_saidas)}")
    print(f"Resultado: {formatar_moeda(resumo.resultado)}")
    print(f"Taxa de economia: {resumo.taxa_economia:.1f}%")
    if resumo.maior_categoria_gasto.nome:
        print(
            f"Maior categoria de gasto: {resumo.maior_categoria_gasto.nome} "
            f"({formatar_moeda(resumo.maior_categoria_gasto.valor)})"
        )
    if resumo.maior_despesa_individual.descricao:
        print(
            f"Maior despesa individual: {resumo.maior_despesa_individual.descricao} "
            f"({formatar_moeda(resumo.maior_despesa_individual.valor)})"
        )

    if relatorio.insights:
        print("\nInsights:")
        for texto in relatorio.insights:
            print(f"  • {texto}")

    caminho = PASTA_RELATORIOS / f"relatorio_{ano:04d}_{mes:02d}.pdf"
    gerar_pdf_relatorio_mensal(relatorio, caminho)
    print(f"\nPDF salvo em {caminho}")


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
        "3": ("Histórico com filtros", historico_com_filtros),
        "4": ("Resumo do mês", resumo_do_mes),
        "5": ("Definir orçamento", definir_orcamento),
        "6": ("Ver orçamento do mês", ver_orcamento_do_mes),
        "7": ("Gerar relatório do mês (PDF)", gerar_relatorio_do_mes),
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
