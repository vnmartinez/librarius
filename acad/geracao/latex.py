from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from acad.config import registrar_detalhe


_ESCAPES = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
    "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
    "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
}


def escapar_latex(texto: str) -> str:
    return "".join(_ESCAPES.get(caractere, caractere) for caractere in texto)


def compilador() -> list[str] | None:
    if shutil.which("tectonic"):
        return ["tectonic", "-X", "compile"]
    if shutil.which("pdflatex"):
        return ["pdflatex", "-disable-installer", "-interaction=nonstopmode", "-halt-on-error"]
    return None


def compilar(tex: Path) -> Path | None:
    comando = compilador()
    if comando is None:
        return None
    tex = Path(tex)
    with tempfile.TemporaryDirectory(prefix="acad-latex-") as diretorio:
        trabalho = Path(diretorio)
        fonte = trabalho / tex.name
        shutil.copy2(tex, fonte)
        for apoio in tex.parent.iterdir():
            if apoio != tex and apoio.is_file() and apoio.suffix.lower() in {".sty", ".jpg", ".jpeg", ".png", ".cls"}:
                shutil.copy2(apoio, trabalho / apoio.name)
        passes = 1 if comando[0] == "tectonic" else 2
        try:
            for _ in range(passes):
                resultado = subprocess.run([*comando, fonte.name], cwd=trabalho, capture_output=True,
                                           text=True, timeout=90, check=False)
                if resultado.returncode:
                    registrar_detalhe(f"Compilação LaTeX falhou: {resultado.stdout[-2000:]} {resultado.stderr[-500:]}")
                    return None
            pdf = trabalho / tex.with_suffix(".pdf").name
            if not pdf.is_file():
                registrar_detalhe("Compilação LaTeX terminou sem gerar PDF.")
                return None
            destino = tex.with_suffix(".pdf")
            shutil.copy2(pdf, destino)
            return destino
        except (OSError, subprocess.TimeoutExpired) as erro:
            registrar_detalhe(f"Compilação LaTeX falhou: {erro}")
            return None
