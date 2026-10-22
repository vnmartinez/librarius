import subprocess
import sys

import acad


def test_versao_definida():
    assert acad.__version__ == "0.1.0"


def test_modulo_executavel():
    resultado = subprocess.run(
        [sys.executable, "-m", "acad", "--versao"], capture_output=True, text=True
    )
    assert resultado.returncode == 0
    assert "0.1.0" in resultado.stdout
