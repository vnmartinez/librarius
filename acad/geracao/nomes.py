from __future__ import annotations

import re

from acad.arquivos.caminhos import sem_acento


def limpar_tema(tema: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r'[<>:"/\\|?*]', "", tema)).strip().rstrip(".").strip()


def slug(tema: str) -> str:
    return re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", sem_acento(limpar_tema(tema))))


def arquivos_da_aula(num: str, tema: str, perfil) -> dict[str, str]:
    numero = str(int(num)).zfill(2)
    limpo = limpar_tema(tema)
    return {
        "slides": f"{perfil.pasta('aulas')}/Aula {numero} - {limpo}.pptx",
        "roteiro": f"{perfil.pasta('aulas')}/Aula {numero} - Roteiro de Aula - {limpo}.md",
        "codigo": f"{perfil.pasta('codigo')}/aula-{numero}-{slug(limpo)}",
        "lista": f"{perfil.pasta('atividades')}/Lista {numero} - {limpo}.md",
    }
