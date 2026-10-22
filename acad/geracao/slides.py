from __future__ import annotations

from pathlib import Path
from typing import Callable, Protocol


class GeradorSlides(Protocol):
    def gerar(self, conteudo: dict, template: Path | None) -> bytes: ...


class GeradorSlidesFalso:
    def gerar(self, conteudo: dict, template: Path | None) -> bytes:
        return b"PPTX-FALSO:" + str(conteudo.get("tema", "")).encode("utf-8")


def obter_gerador(ler_bytes: Callable[[Path], bytes] | None = None, identidade=None) -> GeradorSlides:
    """Gerador real com identidade visual do perfil."""
    from acad.geracao.identidade import IDENTIDADE_NEUTRA
    from acad.geracao.slides_pptx import GeradorSlidesPptx

    return GeradorSlidesPptx(ler_bytes, identidade or IDENTIDADE_NEUTRA)
