"""Pacotes .zip de skills para o ChatGPT (uma pasta de topo e um SKILL.md por pacote)."""
from __future__ import annotations

import zipfile
from pathlib import Path

from acad.plataformas import skills

TRECHO_CHATGPT = "chamar-nucleo-chatgpt.md"
LIMITE = 50 * 1024 * 1024


def _skill_para_chatgpt(pasta: Path, raiz: Path) -> str:
    texto = (pasta / "SKILL.md").read_text(encoding="utf-8")
    novo = (raiz / "scripts" / "trechos" / TRECHO_CHATGPT).read_text(encoding="utf-8").strip()
    antes, resto = texto.split(skills.INICIO, 1)
    depois = resto.split(skills.FIM, 1)[1]
    return antes + novo + depois


def empacotar(raiz: Path, destino: Path) -> list[Path]:
    destino.mkdir(parents=True, exist_ok=True)
    gerados = []
    for nome in skills.SKILLS:
        pasta = raiz / "skills" / nome
        zip_path = destino / f"{nome}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr(f"{nome}/SKILL.md", _skill_para_chatgpt(pasta, raiz))
            for extra in sorted(pasta.rglob("*")):
                if extra.is_file() and extra.name != "SKILL.md":
                    z.write(extra, f"{nome}/{extra.relative_to(pasta).as_posix()}")
        if zip_path.stat().st_size > LIMITE:
            raise ValueError(f"{zip_path.name} passa de 50 MB")
        gerados.append(zip_path)
    return gerados
