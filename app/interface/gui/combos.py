import sqlite3

from PySide6.QtWidgets import QComboBox

from app.repositories.conta_repository import ContaRepository


def preencher_combo_contas(
    combo: QComboBox,
    conn: sqlite3.Connection,
    incluir_todas: bool = False,
    apenas_ativas: bool = True,
) -> None:
    conta_id_atual = combo.currentData()
    combo.blockSignals(True)
    combo.clear()
    if incluir_todas:
        combo.addItem("Todas as contas", None)
    for conta in ContaRepository(conn).list(apenas_ativas=apenas_ativas):
        combo.addItem(conta.nome, conta.id)
    indice = combo.findData(conta_id_atual)
    combo.setCurrentIndex(indice if indice >= 0 else 0)
    combo.blockSignals(False)
