import json

import pptx
import pytest

from testes.ferramentas.referencia_slides import ARQUIVO_REFERENCIA, gerar_referencia, resumos


def test_slides_fasoft_identicos_a_referencia():
    referencia = json.loads(ARQUIVO_REFERENCIA.read_text(encoding="utf-8"))
    if referencia["python_pptx"] != pptx.__version__:
        pytest.fail(f"python-pptx mudou ({referencia['python_pptx']} -> {pptx.__version__}): "
                    "regrave a referencia a partir de d944cbe, nunca do codigo novo.")
    assert resumos(gerar_referencia()) == referencia["partes"]
