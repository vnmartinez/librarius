from datetime import datetime

import pytest

from acad.erros import ErroAcad
from acad.planejamento.status import TRANSICOES, mudar_status


AGORA = datetime.fromisoformat("2026-10-22T12:00:00-03:00")


@pytest.mark.parametrize("atual,novo", [(atual, novo) for atual, destinos in {
    "planejada": {"rascunho"}, "rascunho": {"revisada", "planejada"},
    "revisada": {"aprovada", "rascunho"}, "aprovada": {"ministrada"},
}.items() for novo in destinos])
def test_transicao_valida(atual, novo):
    aula = {"id": "Aula 01", "status": atual,
            "manifesto": {"aprovado": False, "aprovado_em": None}}
    alterada = mudar_status(aula, novo, AGORA, encontro="E05")
    assert alterada["status"] == novo and aula["status"] == atual
    assert novo in TRANSICOES[atual]


@pytest.mark.parametrize("atual,novo", [
    ("planejada", "aprovada"), ("rascunho", "aprovada"),
    ("revisada", "ministrada"), ("aprovada", "rascunho"),
    ("ministrada", "rascunho"),
])
def test_transicao_invalida(atual, novo):
    with pytest.raises(ErroAcad) as erro:
        mudar_status({"id": "Aula 01", "status": atual}, novo, AGORA)
    assert erro.value.codigo == "transicao-invalida"


def test_aprovar_carimba_manifesto():
    aula = {"id": "Aula 01", "status": "revisada", "manifesto": {"aprovado": False, "aprovado_em": None}}
    resultado = mudar_status(aula, "aprovada", AGORA)
    assert resultado["manifesto"]["aprovado"] is True
    assert resultado["manifesto"]["aprovado_em"] == AGORA.isoformat()


def test_ministrada_exige_encontro():
    with pytest.raises(ErroAcad):
        mudar_status({"id": "Aula 01", "status": "aprovada"}, "ministrada", AGORA)


def test_ministrada_registra_encontro():
    resultado = mudar_status({"id": "Aula 01", "status": "aprovada"}, "ministrada", AGORA, "E05")
    assert resultado["ministrada_em"] == ["E05"]


def test_cli_ministrada_propõe_aula_e_encontro(capsys, semestre_sintetico):
    import json
    from acad import esquemas
    from acad.cli import main

    pasta = semestre_sintetico / "01 - Disc A - 3º Período" / "01 - Planejamento"
    arquivo_aulas = pasta / "aulas.yaml"
    arquivo_aulas.write_text(esquemas.para_yaml({
        "versao_esquema": 1, "disciplina": "DA",
        "aulas": [{"id": "Aula 01", "tema": "Árvores", "status": "aprovada"}],
    }), encoding="utf-8")
    arquivo_encontros = pasta / "encontros-TA.yaml"
    arquivo_encontros.write_text(esquemas.para_yaml({
        "versao_esquema": 1, "gerado_por": "acad 0.1.0", "gerado_em": AGORA.isoformat(), "entradas": {},
        "encontros": [{"id": "E05", "data": "2026-08-10", "inicio": "19:00", "fim": "20:40",
                       "status": "previsto", "aulas": ["Aula 01"], "funcao": "conteudo", "origem": "horario"}],
    }), encoding="utf-8")
    codigo = main(["aula", "status", "01", "--aula", "01", "ministrada", "--encontro", "E05",
                   "--raiz", str(semestre_sintetico), "--json"])
    resultado = json.loads(capsys.readouterr().out)
    assert codigo == 0
    assert {item["destino"].split("/")[-1] for item in resultado["proposta"]["itens"]} == {
        "aulas.yaml", "encontros-TA.yaml"}
    assert "ministrada" not in arquivo_aulas.read_text(encoding="utf-8")
    assert "realizado" not in arquivo_encontros.read_text(encoding="utf-8")
