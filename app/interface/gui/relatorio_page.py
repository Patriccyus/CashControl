import sqlite3
from datetime import date
from pathlib import Path

from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSpinBox, QTextEdit, QVBoxLayout, QWidget

from app.analytics.relatorio_mensal import gerar_relatorio_mensal
from app.reports.relatorio_pdf import gerar_pdf_relatorio_mensal
from app.utils.money import formatar_moeda

PASTA_RELATORIOS = Path(__file__).resolve().parents[3] / "reports"

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


class RelatorioPage(QWidget):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__()
        self.conn = conn

        layout = QVBoxLayout(self)

        titulo = QLabel("Relatório mensal")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(titulo)

        controles = QHBoxLayout()
        hoje = date.today()

        self.spin_mes = QSpinBox()
        self.spin_mes.setRange(1, 12)
        self.spin_mes.setValue(hoje.month)
        self.spin_mes.valueChanged.connect(self._atualizar_previa)
        controles.addWidget(self.spin_mes)

        self.spin_ano = QSpinBox()
        self.spin_ano.setRange(2000, 2100)
        self.spin_ano.setValue(hoje.year)
        self.spin_ano.valueChanged.connect(self._atualizar_previa)
        controles.addWidget(self.spin_ano)

        self.botao_gerar = QPushButton("Gerar relatório em PDF")
        self.botao_gerar.clicked.connect(self._gerar_pdf)
        controles.addWidget(self.botao_gerar)

        layout.addLayout(controles)

        self.rotulo_status = QLabel("")
        layout.addWidget(self.rotulo_status)

        self.texto_previa = QTextEdit()
        self.texto_previa.setReadOnly(True)
        layout.addWidget(self.texto_previa)

        self._atualizar_previa()

    def atualizar(self) -> None:
        self._atualizar_previa()

    def _atualizar_previa(self) -> None:
        self.rotulo_status.setText("")
        relatorio = gerar_relatorio_mensal(self.conn, self.spin_mes.value(), self.spin_ano.value())
        resumo = relatorio.resumo

        linhas = [
            f"{NOMES_MESES[relatorio.mes]}/{relatorio.ano}",
            "",
            f"Entradas: {formatar_moeda(resumo.total_entradas)}",
            f"Saídas: {formatar_moeda(resumo.total_saidas)}",
            f"Resultado: {formatar_moeda(resumo.resultado)}",
            f"Taxa de economia: {resumo.taxa_economia:.1f}%",
            "",
        ]
        if relatorio.insights:
            linhas.append("Insights:")
            linhas.extend(f"• {texto}" for texto in relatorio.insights)
        else:
            linhas.append("Nenhuma observação relevante neste período.")

        self.texto_previa.setPlainText("\n".join(linhas))

    def _gerar_pdf(self) -> None:
        relatorio = gerar_relatorio_mensal(self.conn, self.spin_mes.value(), self.spin_ano.value())
        caminho = PASTA_RELATORIOS / f"relatorio_{relatorio.ano:04d}_{relatorio.mes:02d}.pdf"
        gerar_pdf_relatorio_mensal(relatorio, caminho)

        self.rotulo_status.setStyleSheet("color: #1a7a3c;")
        self.rotulo_status.setText(f"Relatório salvo em {caminho}")
