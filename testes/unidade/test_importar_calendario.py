import json
from datetime import date
from pathlib import Path

from acad.calendario.importar_ics import importar_ics
from acad.calendario.importar_xlsx import importar_xlsx
from acad.cli import main

SINTETICOS = Path(__file__).resolve().parents[1] / "amostras" / "sinteticos"
ARGS = ("2026-2", date(2026, 7, 27), date(2026, 12, 12))


def _tipos(calendario):
    return {(dia.data, dia.tipo) for dia in calendario.dias}


def test_ics():
    calendario = importar_ics((SINTETICOS / "calendario-2026-2.ics").read_bytes(), *ARGS)
    assert (date(2026, 10, 12), "feriado") in _tipos(calendario)
    assert {(date(2026, 11, dia), "recesso") for dia in (19, 20, 21)} <= _tipos(calendario)
    assert (date(2026, 11, 22), "recesso") not in _tipos(calendario)
    assert any(evento.tipo == "semana-academica" for evento in calendario.eventos)
    assert calendario.status == "rascunho" and calendario.fonte["tipo"] == "ics"


def test_sabado_letivo_fica_pendente():
    calendario = importar_ics((SINTETICOS / "calendario-2026-2.ics").read_bytes(), *ARGS)
    [sabado] = [dia for dia in calendario.dias if dia.tipo == "sabado-letivo"]
    assert sabado.equivale_a is None


def test_xlsx_equivale_ao_ics():
    ics = importar_ics((SINTETICOS / "calendario-2026-2.ics").read_bytes(), *ARGS)
    planilha = importar_xlsx((SINTETICOS / "calendario-2026-2.xlsx").read_bytes(), *ARGS)
    assert _tipos(ics) == _tipos(planilha)


def test_cli_importar_gera_proposta(capsys, semestre_sintetico):
    codigo = main([
        "calendario", "importar", str(SINTETICOS / "calendario-2026-2.ics"),
        "--inicio", "2026-07-27", "--fim", "2026-12-12", "--semestre", "2026-2",
        "--raiz", str(semestre_sintetico), "--json",
    ])
    resultado = json.loads(capsys.readouterr().out)
    assert codigo == 0
    assert resultado["proposta"]["itens"][0]["destino"] == "00 - Administração Acadêmica/calendario.yaml"
    assert not (semestre_sintetico / "00 - Administração Acadêmica" / "calendario.yaml").exists()
    assert "feriado" in resultado["mensagem"].lower()
