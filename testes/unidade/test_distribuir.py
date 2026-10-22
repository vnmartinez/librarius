from datetime import date, timedelta

import pytest

from acad.encontros.gerar import Encontro
from acad.erros import ErroAcad
from acad.planejamento.distribuir import distribuir, ordenar_por_prerequisitos


def _es(n, **kw):
    return [Encontro(f"E{i:02d}", date(2026, 8, 3) + timedelta(days=2 * i), "19:00", "20:40",
                     kw.get("status", "previsto"), [], kw.get("funcao", "conteudo"), "horario")
            for i in range(1, n + 1)]


def _a(id, nec=1, pre=(), status="planejada"):
    return {"id": id, "tema": id, "status": status, "encontros_necessarios": nec, "prerequisitos": list(pre)}


def test_sequencial_com_dois_encontros():
    es, sobra = distribuir([_a("Aula 01"), _a("Aula 02", 2), _a("Aula 03")], _es(4))
    assert [e.aulas for e in es] == [["Aula 01"], ["Aula 02"], ["Aula 02"], ["Aula 03"]] and sobra == []


def test_pula_avaliacao_e_cancelado():
    es = _es(4)
    es[1].funcao = "avaliacao"
    es[2].status = "cancelado"
    es, _ = distribuir([_a("Aula 01"), _a("Aula 02")], es)
    assert es[1].aulas == [] and es[2].aulas == [] and es[3].aulas == ["Aula 02"]


def test_realizado_preservado():
    es = _es(3)
    es[0].status, es[0].aulas = "realizado", ["Aula 01"]
    es, _ = distribuir([_a("Aula 01", status="ministrada"), _a("Aula 02")], es)
    assert es[0].aulas == ["Aula 01"] and es[1].aulas == ["Aula 02"]


def test_sobra_aula():
    _, sobra = distribuir([_a("Aula 01"), _a("Aula 02")], _es(1))
    assert sobra == ["Aula 02"]


def test_prerequisito_reordena():
    ordem = ordenar_por_prerequisitos([_a("Aula 02", pre=["Aula 01"]), _a("Aula 01"), _a("Aula 03")])
    assert [a["id"] for a in ordem] == ["Aula 01", "Aula 02", "Aula 03"]


def test_ciclo():
    with pytest.raises(ErroAcad) as erro:
        ordenar_por_prerequisitos([_a("Aula 01", pre=["Aula 02"]), _a("Aula 02", pre=["Aula 01"])])
    assert erro.value.codigo == "prerequisitos-em-ciclo"


def test_cli_propõe_encontros_sem_gravar(capsys, semestre_sintetico):
    import json
    from acad import esquemas
    from acad.cli import main
    from acad.planejamento.arquivos import documento_encontros

    pasta = semestre_sintetico / "01 - Disc A - 3º Período" / "01 - Planejamento"
    (pasta / "aulas.yaml").write_text(esquemas.para_yaml({
        "versao_esquema": 1, "disciplina": "DA", "aulas": [{
            **_a("Aula 01"), "objetivos": []
        }],
    }), encoding="utf-8")
    original = documento_encontros(_es(2), {}, "0.1.0", __import__("datetime").datetime.now().astimezone())
    (pasta / "encontros-TA.yaml").write_text(esquemas.para_yaml(original), encoding="utf-8")
    codigo = main(["plano", "distribuir", "01", "--turma", "TA", "--raiz", str(semestre_sintetico), "--json"])
    resultado = json.loads(capsys.readouterr().out)
    assert codigo == 0
    assert "Aula 01" in resultado["mensagem"]
    assert resultado["proposta"]["itens"][0]["destino"].endswith("encontros-TA.yaml")
    assert "Aula 01" not in (pasta / "encontros-TA.yaml").read_text(encoding="utf-8")

