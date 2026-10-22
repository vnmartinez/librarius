from __future__ import annotations

from pathlib import Path
from typing import Protocol

from acad.erros import ErroAcad
from acad.mensagens import msg


class GeradorSlides(Protocol):
    def gerar(self, conteudo: dict, template: Path | None) -> bytes: ...


class GeradorSlidesFalso:
    def gerar(self, conteudo: dict, template: Path | None) -> bytes:
        return b"PPTX-FALSO:" + str(conteudo.get("tema", "")).encode("utf-8")


class GeradorSlidesBloqueado:
    def gerar(self, conteudo: dict, template: Path | None) -> bytes:
        raise ErroAcad("decisao-pendente-d4", msg("decisao-pendente", assunto="qual modelo de slides usar"), saida=4)


def obter_gerador() -> GeradorSlides:
    return GeradorSlidesBloqueado()
