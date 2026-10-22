from datetime import date, datetime

import pytest

from acad.calendario.modelo import de_documento, para_documento, dia, letivo, dia_semana_efetivo, confirmar
from acad.erros import ErroAcad

DOC = {"versao_esquema": 1, "calendario": {
    "semestre": "2026-2", "inicio": "2026-07-27", "fim": "2026-12-12",
    "fonte": {"tipo": "manual"}, "status": "rascunho", "confirmado_em": None,
    "dias": [{"data": "2026-10-12", "tipo": "feriado", "descricao": "Nossa Senhora Aparecida"},
             {"data": "2026-10-17", "tipo": "sabado-letivo", "equivale_a": 1}],
    "eventos": [{"inicio": "2026-09-21", "fim": "2026-09-25", "tipo": "semana-academica", "descricao": "SETECH"}],
}}


def test_ida_e_volta():
    assert para_documento(de_documento(DOC)) == DOC


def test_feriado_nao_letivo():
    calendario = de_documento(DOC)
    assert not letivo(calendario, date(2026, 10, 12))
    assert letivo(calendario, date(2026, 10, 13))


def test_fora_do_semestre():
    assert not letivo(de_documento(DOC), date(2026, 12, 20))


def test_sabado_letivo_equivale_a_segunda():
    assert dia_semana_efetivo(de_documento(DOC), date(2026, 10, 17)) == 1


def test_confirmar_exige_equivalencia():
    documento = {**DOC, "calendario": {**DOC["calendario"], "dias": [{"data": "2026-10-17", "tipo": "sabado-letivo", "equivale_a": None}]}}
    with pytest.raises(ErroAcad) as erro:
        confirmar(de_documento(documento, validar=False), datetime(2026, 7, 1))
    assert "17/10" in erro.value.mensagem


def test_confirmar_muda_status():
    calendario = confirmar(de_documento(DOC), datetime(2026, 7, 1, 10, 0))
    assert calendario.status == "confirmado" and calendario.confirmado_em.startswith("2026-07-01")
