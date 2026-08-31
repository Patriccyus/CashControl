from app.utils.senha import gerar_hash, verificar_senha


def test_verificar_senha_correta():
    hash_senha, salt = gerar_hash("1234")
    assert verificar_senha("1234", hash_senha, salt)


def test_verificar_senha_incorreta():
    hash_senha, salt = gerar_hash("1234")
    assert not verificar_senha("0000", hash_senha, salt)


def test_hashes_diferentes_para_mesma_senha_com_salts_diferentes():
    hash1, salt1 = gerar_hash("1234")
    hash2, salt2 = gerar_hash("1234")
    assert salt1 != salt2
    assert hash1 != hash2
