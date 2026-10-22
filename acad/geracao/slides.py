from __future__ import annotations

from pathlib import Path
from typing import Callable, Protocol


class GeradorSlides(Protocol):
    def gerar(self, conteudo: dict, template: Path | None) -> bytes: ...


class GeradorSlidesFalso:
    def gerar(self, conteudo: dict, template: Path | None) -> bytes:
        return b"PPTX-FALSO:" + str(conteudo.get("tema", "")).encode("utf-8")


def obter_gerador(ler_bytes: Callable[[Path], bytes] | None = None) -> GeradorSlides:
    """Gerador real (D4 fechada em 22/10/2026): python-pptx no padrão visual UniRV."""
    from acad.geracao.slides_pptx import GeradorSlidesPptx

    return GeradorSlidesPptx(ler_bytes)
