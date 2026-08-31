import sqlite3
from datetime import date
from typing import List

from app.analytics.fatura_cartao import mes_fatura_da_compra
from app.models.compra_cartao import CompraCartao, ParcelaCartao
from app.repositories.cartao_repository import CartaoRepository
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.compra_cartao_repository import CompraCartaoRepository
from app.repositories.fatura_paga_repository import FaturaPagaRepository
from app.services.exceptions import ErroValidacao
from app.utils.datas import mes_seguinte
from app.utils.money import formatar_moeda


class CompraCartaoService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.repo = CompraCartaoRepository(conn)
        self.cartoes = CartaoRepository(conn)
        self.categorias = CategoriaRepository(conn)
        self.faturas_pagas = FaturaPagaRepository(conn)

    def registrar_compra(
        self,
        cartao_id: int,
        categoria_id: int,
        descricao: str,
        data_compra: str,
        valor_total: int,
        numero_parcelas: int = 1,
    ) -> int:
        if not descricao or not descricao.strip():
            raise ErroValidacao("Descrição não pode ser vazia.")
        if valor_total <= 0:
            raise ErroValidacao("Valor deve ser maior que zero.")
        if numero_parcelas < 1:
            raise ErroValidacao("Número de parcelas deve ser ao menos 1.")

        cartao = self.cartoes.get_by_id(cartao_id)
        if cartao is None or not cartao.ativo:
            raise ErroValidacao("Cartão inválido ou inativo.")

        categoria = self.categorias.get_by_id(categoria_id)
        if categoria is None or not categoria.ativo:
            raise ErroValidacao("Categoria inválida ou inativa.")
        if categoria.tipo != "saida":
            raise ErroValidacao("Compras no cartão devem usar uma categoria de saída.")

        try:
            data_compra_convertida = date.fromisoformat(data_compra)
        except ValueError as exc:
            raise ErroValidacao(f"Data da compra inválida: {data_compra!r}.") from exc

        periodos_pagos = self.faturas_pagas.periodos_pagos(cartao_id)
        total_em_aberto = self.repo.total_em_aberto(cartao_id, periodos_pagos)
        if total_em_aberto + valor_total > cartao.limite:
            disponivel = cartao.limite - total_em_aberto
            raise ErroValidacao(f"Limite do cartão insuficiente. Disponível: {formatar_moeda(disponivel)}.")

        parcelas_valores = self._dividir_em_parcelas(valor_total, numero_parcelas)
        mes_atual, ano_atual = mes_fatura_da_compra(data_compra_convertida, cartao.dia_fechamento)

        compra = CompraCartao(
            cartao_id=cartao_id,
            categoria_id=categoria_id,
            descricao=descricao.strip(),
            data_compra=data_compra,
            valor_total=valor_total,
            numero_parcelas=numero_parcelas,
        )
        for numero, valor_parcela in enumerate(parcelas_valores, start=1):
            compra.parcelas.append(
                ParcelaCartao(
                    compra_id=0,
                    numero=numero,
                    valor=valor_parcela,
                    fatura_mes=mes_atual,
                    fatura_ano=ano_atual,
                )
            )
            mes_atual, ano_atual = mes_seguinte(mes_atual, ano_atual)

        return self.repo.create(compra)

    def listar_compras(self, cartao_id: int) -> List[CompraCartao]:
        return self.repo.list_por_cartao(cartao_id)

    def excluir_compra(self, compra_id: int) -> None:
        compra = self.repo.get_by_id(compra_id)
        if compra is None:
            raise ErroValidacao("Compra não encontrada.")

        periodos_pagos = self.faturas_pagas.periodos_pagos(compra.cartao_id)
        if any((p.fatura_mes, p.fatura_ano) in periodos_pagos for p in compra.parcelas):
            raise ErroValidacao("Não é possível excluir: alguma parcela já está em fatura paga.")

        self.repo.delete(compra_id)

    @staticmethod
    def _dividir_em_parcelas(valor_total: int, numero_parcelas: int) -> List[int]:
        valor_base = valor_total // numero_parcelas
        resto = valor_total - valor_base * numero_parcelas
        parcelas = [valor_base] * numero_parcelas
        for indice in range(resto):
            parcelas[indice] += 1
        return parcelas
