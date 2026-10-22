from datetime import date, timedelta

import pytest

from acad.encontros.gerar import Encontro
from acad.erros import ErroAcad
from acad.planejamento.distribuir import distribuir
from acad.planejamento.replanejar import cancelar, diff, resumo_diff


def _es(n):
    return [Encontro(f"E{i:02d}", date(2026, 10, 5) + timedelta(days=2 * (i - 1)),
                     "19:00", "20:40", "previsto", [], "conteudo", "horario") for i in range(1, n + 1)]


AULAS = [{"id": f"Aula {i:02d}", "tema": "x", "status": "planejada",
          "encontros_necessarios": 1, "prerequisitos": []} for i in range(1, 5)]


def test_cancelar_desloca_e_afeta_avaliacao():
    antes, _ = distribuir(AULAS, _es(5))
    depois, sobra = distribuir(AULAS, cancelar(antes, date(2026, 10, 7), "chuva"))
    # Aula 03 muda de 09/10 para 11/10; prova em 10/10 passa a precedê-la.
    aval = [{"etapa": "N2", "data": "2026-10-10", "aulas_cobertas": ["Aula 03"]}]
    d = diff(antes, depois, aval)
    assert {"aula": "Aula 02", "de": ["2026-10-07"], "para": ["2026-10-09"]} in d["deslocadas"]
    assert d["avaliacoes_afetadas"] == [{"etapa": "N2", "data": "2026-10-10", "aulas": ["Aula 03"]}]
    assert sobra == []


def test_resumo_em_portugues():
    antes, _ = distribuir(AULAS, _es(5))
    depois, _ = distribuir(AULAS, cancelar(antes, date(2026, 10, 7), "chuva"))
    texto = resumo_diff(diff(antes, depois, []))
    assert "Aula 02" in texto and "07/10" in texto and "09/10" in texto


def test_cancelar_data_sem_encontro():
    with pytest.raises(ErroAcad) as erro:
        cancelar(_es(2), date(2026, 10, 8), "chuva")
    assert erro.value.codigo == "sem-encontro-na-data"


def test_cancelar_nao_muda_original():
    antes, _ = distribuir(AULAS, _es(5))
    depois = cancelar(antes, date(2026, 10, 7), "chuva")
    assert antes[1].status == "previsto" and antes[1].aulas == ["Aula 02"]
    assert depois[1].status == "cancelado" and depois[1].aulas == []


def test_cli_replanejar_propõe_diff_sem_gravar(capsys, semestre_sintetico):
    import json
    from datetime import datetime
    from acad import esquemas
    from acad.cli import main
    from acad.planejamento.arquivos import documento_encontros

    pasta = semestre_sintetico / "01 - Disc A - 3º Período" / "01 - Planejamento"
    (pasta / "aulas.yaml").write_text(esquemas.para_yaml({
        "versao_esquema": 1, "disciplina": "DA",
        "aulas": [{**aula, "objetivos": []} for aula in AULAS],
    }), encoding="utf-8")
    anteriores, _ = distribuir(AULAS, _es(5))
    original = documento_encontros(anteriores, {}, "0.1.0", datetime.now().astimezone())
    arquivo = pasta / "encontros-TA.yaml"
    arquivo.write_text(esquemas.para_yaml(original), encoding="utf-8")
    codigo = main(["plano", "replanejar", "01", "--turma", "TA", "--cancelar", "2026-10-07",
                   "--motivo", "chuva", "--raiz", str(semestre_sintetico), "--json"])
    resultado = json.loads(capsys.readouterr().out)
    assert codigo == 0
    assert resultado["dados"]["diff"]["deslocadas"]
    assert resultado["proposta"]["itens"][0]["destino"].endswith("encontros-TA.yaml")
    assert "chuva" not in arquivo.read_text(encoding="utf-8")
