import os
from datetime import datetime
from pathlib import Path


def dir_dados() -> Path:
    for variavel in ("ACAD_DADOS", "CLAUDE_PLUGIN_DATA"):
        if os.environ.get(variavel):
            return Path(os.environ[variavel])
    if os.environ.get("LOCALAPPDATA"):
        return Path(os.environ["LOCALAPPDATA"]) / "librarius"
    return Path.home() / ".local" / "share" / "librarius"


def registrar_detalhe(texto: str) -> None:
    diretorio = dir_dados()
    diretorio.mkdir(parents=True, exist_ok=True)
    with open(diretorio / "registro.log", "a", encoding="utf-8") as registro:
        registro.write(f"{datetime.now().isoformat(timespec='seconds')} {texto}\n")
