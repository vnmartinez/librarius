from pathlib import Path

import pytest

from acad.geracao.avaliacao import renderizar
from acad.geracao.latex import compilar, compilador


@pytest.mark.latex
def test_compilar_prova_generica_em_pdf(tmp_path):
    if compilador() is None:
        pytest.skip("Compilador LaTeX ausente")
    modelo = (Path(__file__).resolve().parents[2] / "modelos" / "prova.tex").read_text(encoding="utf-8")
    tex = tmp_path / "prova.tex"
    tex.write_text(renderizar(modelo, {
        "titulo": "AVALIAÇÃO 1", "disciplina": "Estrutura de Dados 2",
        "professor": "Docente", "data": "2026-10-22",
    }, [{"id": "Q1", "tipo": "discursiva", "enunciado": "Explique AVL.",
         "resposta": "Árvore balanceada", "pontos": 2}], False), encoding="utf-8")
    pdf = compilar(tex)
    assert pdf is not None and pdf.read_bytes().startswith(b"%PDF")
