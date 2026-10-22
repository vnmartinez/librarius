import importlib
import json

from acad.cli import main


def test_ambiente_confere_slides_e_demais_dependencias(monkeypatch, capsys):
    real = importlib.import_module

    def falso(nome, *a, **k):
        if nome == "pptx":
            raise ImportError(nome)
        return real(nome, *a, **k)

    monkeypatch.setattr(importlib, "import_module", falso)
    codigo = main(["ambiente", "verificar", "--json"])
    dados = json.loads(capsys.readouterr().out)
    assert codigo != 0 and "pptx" in dados["dados"]["faltando"]


def test_ambiente_pronto_com_todas_as_dependencias(capsys):
    assert main(["ambiente", "verificar", "--json"]) == 0
