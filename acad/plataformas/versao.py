"""Versão única do plugin, sincronizada em todos os manifestos."""
from __future__ import annotations

import re
from pathlib import Path

ARQUIVOS = [
    ("pyproject.toml", "project.version"),
    ("acad/__init__.py", "__version__"),
    (".claude-plugin/plugin.json", "version"),
    (".claude-plugin/marketplace.json", "plugins.0.version"),
    (".codex-plugin/plugin.json", "version"),
]

_PADROES = {
    "project.version": re.compile(r'(?m)^(version\s*=\s*")([^"]+)(")'),
    "__version__": re.compile(r'(?m)^(__version__\s*=\s*")([^"]+)(")'),
    "version": re.compile(r'("version"\s*:\s*")([^"]+)(")'),
    "plugins.0.version": re.compile(r'("version"\s*:\s*")([^"]+)(")'),
}


def ler_todas(raiz: Path) -> dict[str, str]:
    saida = {}
    for arquivo, chave in ARQUIVOS:
        texto = (raiz / arquivo).read_bytes().decode("utf-8")
        m = _PADROES[chave].search(texto)
        if not m:
            raise ValueError(f"versão não encontrada em {arquivo}")
        saida[arquivo] = m.group(2)
    return saida


def aplicar(raiz: Path, nova: str) -> None:
    if not re.fullmatch(r"\d+\.\d+\.\d+", nova):
        raise ValueError("versão deve ter o formato 1.2.3")
    for arquivo, chave in ARQUIVOS:
        caminho = raiz / arquivo
        texto = caminho.read_bytes().decode("utf-8")
        novo, n = _PADROES[chave].subn(lambda m: m.group(1) + nova + m.group(3), texto, count=1)
        if n != 1:
            raise ValueError(f"versão não encontrada em {arquivo}")
        caminho.write_bytes(novo.encode("utf-8"))
