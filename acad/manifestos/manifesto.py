from __future__ import annotations

from collections.abc import Callable
from datetime import datetime


def montar_manifesto(artefatos: list[str], entradas: dict[str, str],
                     versao: str, agora: datetime) -> dict:
    return {
        "artefatos": artefatos,
        "gerado_em": agora.astimezone().isoformat(timespec="seconds"),
        "entradas": entradas,
        "aprovado": False,
        "aprovado_em": None,
        "versao_acad": versao,
    }


def divergencias(manifesto: dict, calcular: Callable[[str], str | None]) -> list[str]:
    return [chave for chave, registrado in manifesto.get("entradas", {}).items()
            if calcular(chave) != registrado]
