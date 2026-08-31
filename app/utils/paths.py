import sys
from pathlib import Path

_RAIZ_CODIGO_FONTE = Path(__file__).resolve().parents[2]


def base_dir() -> Path:
    """Diretório onde ficam os dados persistentes do usuário (data/, reports/).

    Quando empacotado com PyInstaller, isso precisa ser a pasta do executável,
    não a pasta temporária de extração (_MEIPASS), que é apagada ao fechar o app.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return _RAIZ_CODIGO_FONTE


def recurso_dir() -> Path:
    """Diretório onde ficam arquivos empacotados junto com o código (ex: schema.sql)."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", base_dir()))
    return _RAIZ_CODIGO_FONTE
