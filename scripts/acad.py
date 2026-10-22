"""Lançador do Librarius: prepara o ambiente Python e executa o núcleo `acad`.

Usa só a biblioteca padrão, para rodar em qualquer computador com Python 3.11+.
"""
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path


class FalhaInstalacao(Exception):
    pass


def raiz() -> Path:
    return Path(__file__).resolve().parents[1]


def _projeto() -> dict:
    with open(raiz() / "pyproject.toml", "rb") as f:
        return tomllib.load(f)["project"]


def versao() -> str:
    return _projeto()["version"]


def dependencias() -> list[str]:
    return list(_projeto()["dependencies"])


def dir_dados() -> Path:
    for nome in ("ACAD_DADOS", "CLAUDE_PLUGIN_DATA", "PLUGIN_DATA"):
        valor = os.environ.get(nome)
        if valor:
            return Path(valor)
    local = os.environ.get("LOCALAPPDATA")
    if local:
        return Path(local) / "librarius"
    return Path.home() / ".local" / "share" / "librarius"


def python_do_ambiente(amb: Path) -> Path:
    if os.name == "nt":
        return amb / "Scripts" / "python.exe"
    return amb / "bin" / "python"


def _rodar(executar, cmd):
    try:
        r = executar(cmd, capture_output=True, text=True)
    except OSError as erro:
        raise FalhaInstalacao(str(erro)) from erro
    if r.returncode != 0:
        raise FalhaInstalacao(" ".join(map(str, cmd)))


def preparar(amb: Path, executar=subprocess.run) -> Path:
    deps = dependencias()
    marca = amb / ".pronto"
    esperado = "\n".join(deps)
    if marca.exists() and marca.read_text(encoding="utf-8") == esperado:
        return python_do_ambiente(amb)
    py = python_do_ambiente(amb)
    uv = shutil.which("uv")
    if uv:
        _rodar(executar, [uv, "venv", str(amb)])
        _rodar(executar, [uv, "pip", "install", "--python", str(py), *deps])
    else:
        _rodar(executar, [sys.executable, "-m", "venv", str(amb)])
        _rodar(executar, [str(py), "-m", "pip", "install", "--quiet", *deps])
    amb.mkdir(parents=True, exist_ok=True)
    marca.write_text(esperado, encoding="utf-8")
    return py


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if tuple(sys.version_info[:2]) < (3, 11):
        print("O assistente precisa do Python 3.11 ou mais novo. Peça ajuda ao assistente para instalar.")
        return 3
    amb = dir_dados() / "ambientes" / versao()
    try:
        py = preparar(amb)
    except FalhaInstalacao:
        print("Não consegui baixar os componentes de que preciso. Confira a internet e tente de novo.")
        return 3
    env = {**os.environ, "PYTHONPATH": str(raiz()), "PYTHONUTF8": "1"}
    return subprocess.run([str(py), "-m", "acad", *argv], env=env).returncode


if __name__ == "__main__":
    sys.exit(main())
