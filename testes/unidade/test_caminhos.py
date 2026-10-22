import unicodedata

from acad.arquivos.caminhos import nfc, sem_acento, relativo_posix


def test_sem_acento_iguala_arvores():
    assert sem_acento("Árvores B") == sem_acento("Arvores b") == "arvores b"


def test_nfc_iguala_formas():
    nfd = unicodedata.normalize("NFD", "Período")
    assert nfc(nfd) == "Período"


def test_relativo_posix(tmp_path):
    caminho = tmp_path / "04 - ED2" / "02 - Aulas" / "Aula 01 - X.pptx"
    assert relativo_posix(caminho, tmp_path) == "04 - ED2/02 - Aulas/Aula 01 - X.pptx"
