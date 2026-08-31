import sqlite3
from datetime import date

from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app.analytics.dashboard_analytics import (
    calcular_resumo_dashboard,
    entradas_saidas_por_mes,
    gastos_por_categoria_do_mes,
)
from app.analytics.fatura_cartao import total_despesas_futuras_cartoes
from app.analytics.orcamento_analytics import calcular_consumo_orcamento
from app.interface.gui.mpl_canvas import MplCanvas
from app.utils.money import centavos_para_reais, formatar_moeda


class _CartaoIndicador(QFrame):
    def __init__(self, titulo: str):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)

        self._titulo = QLabel(titulo)
        self._titulo.setStyleSheet("color: #666; font-size: 11px;")

        self._valor = QLabel("—")
        self._valor.setStyleSheet("font-size: 20px; font-weight: bold;")

        layout.addWidget(self._titulo)
        layout.addWidget(self._valor)

    def definir_valor(self, texto: str, cor: str = "#1a1a1a") -> None:
        self._valor.setText(texto)
        self._valor.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {cor};")


class DashboardPage(QWidget):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__()
        self.conn = conn

        layout_principal = QVBoxLayout(self)

        titulo = QLabel("Como está minha situação financeira?")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout_principal.addWidget(titulo)

        cartoes_layout = QHBoxLayout()
        self.cartao_saldo = _CartaoIndicador("Saldo atual")
        self.cartao_entradas = _CartaoIndicador("Entradas do mês")
        self.cartao_saidas = _CartaoIndicador("Saídas do mês")
        self.cartao_resultado = _CartaoIndicador("Resultado do mês")
        self.cartao_pendentes = _CartaoIndicador("Contas pendentes")
        self.cartao_renda_comprometida = _CartaoIndicador("% da renda comprometida")
        self.cartao_despesas_futuras = _CartaoIndicador("Despesas futuras (cartão)")
        for cartao in (
            self.cartao_saldo,
            self.cartao_entradas,
            self.cartao_saidas,
            self.cartao_resultado,
            self.cartao_pendentes,
            self.cartao_renda_comprometida,
            self.cartao_despesas_futuras,
        ):
            cartoes_layout.addWidget(cartao)
        layout_principal.addLayout(cartoes_layout)

        graficos_layout = QGridLayout()
        self.canvas_entradas_saidas = MplCanvas()
        self.canvas_categorias = MplCanvas()
        self.canvas_orcamento = MplCanvas()
        graficos_layout.addWidget(self.canvas_entradas_saidas, 0, 0)
        graficos_layout.addWidget(self.canvas_categorias, 0, 1)
        graficos_layout.addWidget(self.canvas_orcamento, 1, 0, 1, 2)
        layout_principal.addLayout(graficos_layout)

        self.atualizar()

    def atualizar(self) -> None:
        self._atualizar_cartoes()
        self._atualizar_grafico_entradas_saidas()
        self._atualizar_grafico_categorias()
        self._atualizar_grafico_orcamento()

    def _atualizar_cartoes(self) -> None:
        resumo = calcular_resumo_dashboard(self.conn)
        self.cartao_saldo.definir_valor(formatar_moeda(resumo.saldo_atual))
        self.cartao_entradas.definir_valor(formatar_moeda(resumo.entradas_mes), cor="#1a7a3c")
        self.cartao_saidas.definir_valor(formatar_moeda(resumo.saidas_mes), cor="#b3261e")
        cor_resultado = "#1a7a3c" if resumo.resultado_mes >= 0 else "#b3261e"
        self.cartao_resultado.definir_valor(formatar_moeda(resumo.resultado_mes), cor=cor_resultado)
        self.cartao_pendentes.definir_valor(
            f"{resumo.quantidade_pendentes} ({formatar_moeda(resumo.valor_pendente)})"
        )
        self.cartao_renda_comprometida.definir_valor(f"{resumo.percentual_renda_comprometida:.0f}%")
        self.cartao_despesas_futuras.definir_valor(
            formatar_moeda(total_despesas_futuras_cartoes(self.conn))
        )

    def _atualizar_grafico_entradas_saidas(self) -> None:
        eixo = self.canvas_entradas_saidas.limpar()
        serie = entradas_saidas_por_mes(self.conn, meses=6)
        meses = [periodo[-2:] + "/" + periodo[:4] for periodo, _, _ in serie]
        entradas = [float(centavos_para_reais(valor)) for _, valor, _ in serie]
        saidas = [float(centavos_para_reais(valor)) for _, _, valor in serie]

        posicoes = range(len(meses))
        largura = 0.35
        eixo.bar([p - largura / 2 for p in posicoes], entradas, largura, label="Entradas", color="#1a7a3c")
        eixo.bar([p + largura / 2 for p in posicoes], saidas, largura, label="Saídas", color="#b3261e")
        eixo.set_xticks(list(posicoes))
        eixo.set_xticklabels(meses, rotation=0, fontsize=8)
        eixo.set_title("Entradas x saídas (6 meses)", fontsize=10)
        eixo.legend(fontsize=8)
        self.canvas_entradas_saidas.draw()

    def _atualizar_grafico_categorias(self) -> None:
        eixo = self.canvas_categorias.limpar()
        dados = gastos_por_categoria_do_mes(self.conn, top_n=6)
        if not dados:
            eixo.text(0.5, 0.5, "Sem gastos no mês", ha="center", va="center", fontsize=9)
        else:
            nomes = [nome for nome, _ in dados][::-1]
            valores = [float(centavos_para_reais(valor)) for _, valor in dados][::-1]
            eixo.barh(nomes, valores, color="#3b6fb6")
            eixo.tick_params(axis="y", labelsize=8)
        eixo.set_title("Gastos por categoria (mês atual)", fontsize=10)
        self.canvas_categorias.draw()

    def _atualizar_grafico_orcamento(self) -> None:
        eixo = self.canvas_orcamento.limpar()
        hoje = date.today()
        consumo = calcular_consumo_orcamento(self.conn, hoje.month, hoje.year)
        if not consumo:
            eixo.text(0.5, 0.5, "Nenhum orçamento definido para este mês", ha="center", va="center", fontsize=9)
        else:
            nomes = [item.categoria_nome for item in consumo]
            limites = [float(centavos_para_reais(item.limite)) for item in consumo]
            gastos = [float(centavos_para_reais(item.gasto)) for item in consumo]
            posicoes = range(len(nomes))
            largura = 0.35
            eixo.bar([p - largura / 2 for p in posicoes], limites, largura, label="Limite", color="#8a8a8a")
            cores_gasto = [
                "#b3261e" if item.situacao == "ultrapassado" else "#d4a017" if item.situacao == "proximo" else "#1a7a3c"
                for item in consumo
            ]
            eixo.bar([p + largura / 2 for p in posicoes], gastos, largura, label="Gasto", color=cores_gasto)
            eixo.set_xticks(list(posicoes))
            eixo.set_xticklabels(nomes, rotation=20, ha="right", fontsize=8)
            eixo.legend(fontsize=8)
        eixo.set_title("Orçamento: limite x gasto por categoria (mês atual)", fontsize=10)
        self.canvas_orcamento.draw()
