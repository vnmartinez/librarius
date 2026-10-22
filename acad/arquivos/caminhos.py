import unicodedata
from pathlib import Path


def nfc(texto: str) -> str:
    return unicodedata.normalize("NFC", texto)


def sem_acento(texto: str) -> str:
    decomposto = unicodedata.normalize("NFD", texto)
    return "".join(
        caractere for caractere in decomposto
        if unicodedata.category(caractere) != "Mn"
    ).lower()


def relativo_posix(caminho: Path, base: Path) -> str:
    return nfc(Path(caminho).relative_to(base).as_posix())
