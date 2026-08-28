from app.services.sugestao_categoria import sugerir_categoria


def test_sugere_supermercado_por_palavra_chave():
    assert sugerir_categoria("Compra no Carrefour") == "Supermercado"


def test_sugere_assinaturas_para_netflix():
    assert sugerir_categoria("Netflix mensal") == "Assinaturas"


def test_retorna_none_quando_nao_reconhece():
    assert sugerir_categoria("xyz aleatorio 123") is None


def test_ignora_acentos_e_maiusculas():
    assert sugerir_categoria("FARMÁCIA São João") == "Saúde"
