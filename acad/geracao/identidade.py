"""Identidade visual dos slides definida pelo perfil da instituicao."""
from __future__ import annotations

from dataclasses import dataclass, field

PALETA_NEUTRA = {
    "principal": "2F3E4E", "secundaria": "4A6076", "claro": "E8ECF0", "claro2": "F4F6F8",
    "tinta": "1E2328", "corpo": "2E3338", "apagado": "6B737B", "linha": "CDD3D9", "fundo": "FFFFFF",
    "subtitulo_capa": "DCE2E8", "codigo_fundo": "1E252C", "codigo_comentario": "9AA8B5", "codigo_texto": "E1E6EB",
}
LIMITES_PADRAO = {"topicos": 6, "linhas_codigo": 16, "linhas_tabela": 8}


@dataclass(frozen=True)
class IdentidadeSlides:
    largura_emu: int = 9144000
    altura_emu: int = 5143500
    fonte: str = "Calibri"
    fonte_codigo: str = "Courier New"
    paleta: dict = field(default_factory=lambda: dict(PALETA_NEUTRA))
    capa_linhas: tuple[str, ...] = ()
    capa_local: str = "{ano}"
    logo_cabecalho: str | None = None
    logos_capa: tuple[str, ...] = ()
    limites: dict = field(default_factory=lambda: dict(LIMITES_PADRAO))


IDENTIDADE_NEUTRA = IdentidadeSlides()


def identidade_de(bloco: dict | None) -> IdentidadeSlides:
    if not bloco:
        return IDENTIDADE_NEUTRA
    base = IDENTIDADE_NEUTRA
    tamanho, fontes = bloco.get("tamanho", {}), bloco.get("fontes", {})
    capa, logos = bloco.get("capa", {}), bloco.get("logos", {})
    return IdentidadeSlides(
        largura_emu=tamanho.get("largura_emu", base.largura_emu),
        altura_emu=tamanho.get("altura_emu", base.altura_emu),
        fonte=fontes.get("texto", base.fonte),
        fonte_codigo=fontes.get("codigo", base.fonte_codigo),
        paleta={**base.paleta, **{chave: valor.upper() for chave, valor in bloco.get("paleta", {}).items()}},
        capa_linhas=tuple(capa.get("linhas", base.capa_linhas)),
        capa_local=capa.get("local", base.capa_local),
        logo_cabecalho=logos.get("cabecalho", base.logo_cabecalho),
        logos_capa=tuple(logos.get("capa", base.logos_capa)),
        limites={**base.limites, **bloco.get("limites", {})},
    )


def mistura(a: str, b: str, t: float) -> str:
    canais = []
    for i in (0, 2, 4):
        x, y = int(a[i:i + 2], 16), int(b[i:i + 2], 16)
        canais.append(f"{round(x + (y - x) * t):02X}")
    return "".join(canais)


def paleta_de_cor(cor: str) -> dict[str, str]:
    cor = cor.upper()
    return {**PALETA_NEUTRA, "principal": cor,
            "secundaria": mistura(cor, "FFFFFF", 0.25), "claro": mistura(cor, "FFFFFF", 0.88),
            "claro2": mistura(cor, "FFFFFF", 0.94), "linha": mistura(cor, "FFFFFF", 0.75),
            "subtitulo_capa": mistura(cor, "FFFFFF", 0.82)}
