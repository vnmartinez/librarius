"""Referencia dos slides fasoft, gravada a partir de d944cbe."""
from __future__ import annotations

import hashlib
import io
import json
import sys
import tempfile
import zipfile
from pathlib import Path

import pptx

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from testes.unidade.test_slides_pptx import CONTEUDO, _png  # noqa: E402

ARQUIVO_REFERENCIA = RAIZ / "testes" / "esperados" / "slides-fasoft.json"
LOGOS = (("logo-header-unirv.png", 6), ("logo-unirv.png", 5), ("logo-fasoft.png", 4))


def resumos(dados: bytes) -> dict[str, str]:
    with zipfile.ZipFile(io.BytesIO(dados)) as pacote:
        return {nome: hashlib.sha256(pacote.read(nome)).hexdigest()
                for nome in sorted(pacote.namelist()) if nome != "docProps/core.xml"}


def gerador_fasoft():
    from acad.geracao.slides_pptx import GeradorSlidesPptx
    from acad.perfil.perfil import carregar_perfil
    return GeradorSlidesPptx(identidade=carregar_perfil("fasoft").slides)


def gerar_referencia() -> bytes:
    with tempfile.TemporaryDirectory() as pasta:
        assets = Path(pasta) / "assets"
        assets.mkdir()
        for nome, largura in LOGOS:
            _png(assets / nome, w=largura)
        return gerador_fasoft().gerar({**CONTEUDO, "ano": 2026}, Path(pasta))


if __name__ == "__main__":
    ARQUIVO_REFERENCIA.write_text(json.dumps(
        {"python_pptx": pptx.__version__, "partes": resumos(gerar_referencia())},
        indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(ARQUIVO_REFERENCIA)
