from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.analytics.relatorio_mensal import RelatorioMensal
from app.utils.money import formatar_moeda

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

ROTULOS_SITUACAO_ORCAMENTO = {
    "dentro": "Dentro do limite",
    "proximo": "Próximo do limite",
    "ultrapassado": "Limite ultrapassado",
}


def gerar_pdf_relatorio_mensal(relatorio: RelatorioMensal, caminho_saida: Path) -> Path:
    caminho_saida = Path(caminho_saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    documento = SimpleDocTemplate(
        str(caminho_saida),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle("TituloRelatorio", parent=estilos["Title"], fontSize=18)
    estilo_secao = ParagraphStyle("Secao", parent=estilos["Heading2"], spaceBefore=14, spaceAfter=6)
    estilo_normal = estilos["Normal"]
    estilo_subsecao = estilos["Heading3"]

    elementos = [
        Paragraph("RELATÓRIO FINANCEIRO", estilo_titulo),
        Paragraph(f"{NOMES_MESES[relatorio.mes]}/{relatorio.ano}", estilo_normal),
        Spacer(1, 0.4 * cm),
    ]

    elementos.append(Paragraph("Resumo", estilo_secao))
    elementos.append(_tabela_resumo(relatorio, estilo_normal))

    elementos.append(Paragraph("Despesas", estilo_secao))
    elementos.append(Paragraph("Por categoria", estilo_subsecao))
    elementos.append(_tabela_itens(relatorio.gastos_por_categoria, "Categoria", estilo_normal))
    elementos.append(Paragraph("Por forma de pagamento", estilo_subsecao))
    elementos.append(_tabela_itens(relatorio.gastos_por_forma_pagamento, "Forma de pagamento", estilo_normal))
    elementos.append(Paragraph("Evolução", estilo_subsecao))
    elementos.append(_tabela_evolucao(relatorio))

    elementos.append(Paragraph("Orçamento", estilo_secao))
    elementos.append(_tabela_orcamento(relatorio, estilo_normal))

    elementos.append(Paragraph("Insights", estilo_secao))
    elementos.extend(_paragrafos_insights(relatorio, estilo_normal))

    documento.build(elementos)
    return caminho_saida


def _tabela_resumo(relatorio: RelatorioMensal, estilo_normal) -> Table:
    resumo = relatorio.resumo
    maior_categoria = (
        f"{resumo.maior_categoria_gasto.nome} ({formatar_moeda(resumo.maior_categoria_gasto.valor)})"
        if resumo.maior_categoria_gasto.nome
        else "—"
    )
    maior_despesa = (
        f"{resumo.maior_despesa_individual.descricao} "
        f"({formatar_moeda(resumo.maior_despesa_individual.valor)})"
        if resumo.maior_despesa_individual.descricao
        else "—"
    )
    dados = [
        ["Entradas", formatar_moeda(resumo.total_entradas)],
        ["Saídas", formatar_moeda(resumo.total_saidas)],
        ["Resultado", formatar_moeda(resumo.resultado)],
        ["Taxa de economia", f"{resumo.taxa_economia:.1f}%"],
        ["Maior categoria de gasto", maior_categoria],
        ["Maior despesa individual", maior_despesa],
    ]
    return _tabela(dados, larguras=[7 * cm, 9 * cm])


def _tabela_itens(itens, rotulo_coluna: str, estilo_normal) -> Table:
    if not itens:
        return Paragraph("Nenhuma despesa registrada no período.", estilo_normal)
    dados = [[rotulo_coluna, "Valor", "%"]]
    dados += [[item.nome, formatar_moeda(item.valor), f"{item.percentual:.1f}%"] for item in itens]
    return _tabela(dados, larguras=[8 * cm, 5 * cm, 3 * cm], cabecalho=True)


def _tabela_evolucao(relatorio: RelatorioMensal) -> Table:
    resumo = relatorio.resumo
    comparacao = relatorio.comparacao_historica
    dados = [
        ["Período", "Entradas", "Saídas", "Resultado"],
        ["Mês atual", formatar_moeda(resumo.total_entradas), formatar_moeda(resumo.total_saidas), formatar_moeda(resumo.resultado)],
        [
            "Mês anterior",
            formatar_moeda(comparacao.mes_anterior.entradas),
            formatar_moeda(comparacao.mes_anterior.saidas),
            formatar_moeda(comparacao.mes_anterior.resultado),
        ],
        [
            "Média últimos 3 meses",
            formatar_moeda(comparacao.media_3_meses.entradas),
            formatar_moeda(comparacao.media_3_meses.saidas),
            formatar_moeda(comparacao.media_3_meses.resultado),
        ],
        [
            "Média últimos 6 meses",
            formatar_moeda(comparacao.media_6_meses.entradas),
            formatar_moeda(comparacao.media_6_meses.saidas),
            formatar_moeda(comparacao.media_6_meses.resultado),
        ],
    ]
    return _tabela(dados, larguras=[5 * cm, 3.7 * cm, 3.7 * cm, 3.7 * cm], cabecalho=True)


def _tabela_orcamento(relatorio: RelatorioMensal, estilo_normal) -> Table:
    if not relatorio.orcamento:
        return Paragraph("Nenhum orçamento definido para o período.", estilo_normal)
    dados = [["Categoria", "Planejado", "Realizado", "Desvio"]]
    for item in relatorio.orcamento:
        desvio = item.gasto - item.limite
        sinal = "+" if desvio > 0 else ""
        dados.append(
            [
                item.categoria_nome,
                formatar_moeda(item.limite),
                formatar_moeda(item.gasto),
                f"{sinal}{formatar_moeda(desvio)} ({ROTULOS_SITUACAO_ORCAMENTO[item.situacao]})",
            ]
        )
    return _tabela(dados, larguras=[4.5 * cm, 3.2 * cm, 3.2 * cm, 5.1 * cm], cabecalho=True)


def _paragrafos_insights(relatorio: RelatorioMensal, estilo_normal) -> list:
    if not relatorio.insights:
        return [Paragraph("Nenhuma observação relevante neste período.", estilo_normal)]
    return [Paragraph(f"• {texto}", estilo_normal) for texto in relatorio.insights]


def _tabela(dados, larguras, cabecalho: bool = False) -> Table:
    tabela = Table(dados, colWidths=larguras)
    estilo = [
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]
    if cabecalho:
        estilo.append(("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke))
        estilo.append(("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"))
    tabela.setStyle(TableStyle(estilo))
    return tabela
