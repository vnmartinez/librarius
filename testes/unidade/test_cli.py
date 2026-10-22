import json
from pathlib import Path

from acad.cli import main

AMOSTRA = Path(__file__).resolve().parents[1] / "amostras" / "fasoft"


def _json(capsys, argv):
    codigo = main(argv + ["--json"])
    return codigo, json.loads(capsys.readouterr().out)


def test_ambiente_verificar(capsys):
    codigo, resultado = _json(capsys, ["ambiente", "verificar"])
    assert codigo == 0 and resultado["ok"] and resultado["dados"]["faltando"] == []


def test_consultar_json(capsys):
    codigo, resultado = _json(capsys, ["cronograma", "consultar", "--data", "2026-07-28", "--raiz", str(AMOSTRA)])
    assert codigo == 0 and resultado["dados"]["quantidade_aulas"] == 1


def test_consultar_aceita_data_brasileira(capsys):
    _, resultado = _json(capsys, ["cronograma", "consultar", "--data", "28/07/2026", "--raiz", str(AMOSTRA)])
    assert resultado["dados"]["data"] == "2026-07-28"


def test_consultar_texto(capsys):
    assert main(["cronograma", "consultar", "--data", "2026-07-28", "--raiz", str(AMOSTRA)]) == 0
    assert "Estrutura de Dados 2" in capsys.readouterr().out


def test_data_invalida_explica(capsys):
    codigo, resultado = _json(capsys, ["cronograma", "consultar", "--data", "amanhã?", "--raiz", str(AMOSTRA)])
    assert codigo == 2 and resultado["erros"][0]["codigo"] == "data-invalida"
    assert "dia/mês/ano" in resultado["erros"][0]["mensagem"]


def test_desfazer_sem_nada(capsys):
    codigo, resultado = _json(capsys, ["desfazer"])
    assert codigo == 0 and "Não há alteração" in resultado["mensagem"]


def test_erro_inesperado_vai_para_registro(capsys, monkeypatch):
    import acad.cronograma.consulta as consulta

    monkeypatch.setattr(consulta, "consultar", lambda *args, **kwargs: 1 / 0)
    codigo, resultado = _json(capsys, ["cronograma", "consultar", "--raiz", str(AMOSTRA)])
    assert codigo == 2 and resultado["erros"][0]["codigo"] == "erro-inesperado"
    assert "ZeroDivisionError" not in resultado["mensagem"]
