from datetime import date

from icalendar import Calendar

from acad.encontros.gerar import Encontro
from acad.exportadores.ics import exportar_ics


def test_exporta_apenas_encontros_nao_cancelados_com_uid_estavel():
    encontros = [
        Encontro("E01", date(2026, 8, 4), "19:00", "20:40", "previsto", ["Aula 03"], "conteudo", "horario"),
        Encontro("E02", date(2026, 8, 7), "19:00", "20:40", "cancelado", [], "conteudo", "horario"),
        Encontro("E03", date(2026, 8, 11), "19:00", "20:40", "previsto", [], "avaliacao", "horario"),
    ]
    kwargs = (encontros, "Estrutura de Dados 2", "TA", "America/Sao_Paulo", {"Aula 03": "Rotações AVL"})
    primeiro = Calendar.from_ical(exportar_ics(*kwargs))
    segundo = Calendar.from_ical(exportar_ics(*kwargs))
    eventos = list(primeiro.walk("VEVENT"))
    assert len(eventos) == 2
    assert [str(evento["UID"]) for evento in eventos] == [str(evento["UID"]) for evento in segundo.walk("VEVENT")]
    assert "Aula 03: Rotações AVL" in str(eventos[0]["SUMMARY"])
    assert "Avaliação" in str(eventos[1]["SUMMARY"])
    assert eventos[0].decoded("DTSTART").hour == 19
    assert str(eventos[0].decoded("DTSTART").tzinfo) == "America/Sao_Paulo"


def test_cli_propõe_arquivo_ics_sem_gravar(capsys, semestre_sintetico):
    import json
    from acad import esquemas
    from acad.cli import main

    pasta = semestre_sintetico / "01 - Disc A - 3º Período" / "01 - Planejamento"
    (pasta / "turma-TA.yaml").write_text(esquemas.para_yaml({
        "versao_esquema": 1, "turma": {"id": "TA", "disciplina": "DA", "fuso": "America/Sao_Paulo",
                                         "horarios": [{"dia_semana": 2, "inicio": "19:00", "fim": "20:40"}]},
    }), encoding="utf-8")
    (pasta / "aulas.yaml").write_text(esquemas.para_yaml({
        "versao_esquema": 1, "disciplina": "DA",
        "aulas": [{"id": "Aula 03", "tema": "Rotações AVL", "status": "planejada"}],
    }), encoding="utf-8")
    (pasta / "encontros-TA.yaml").write_text(esquemas.para_yaml({
        "versao_esquema": 1, "gerado_por": "acad 0.1.0", "gerado_em": "2026-10-01T10:00:00-03:00",
        "entradas": {}, "encontros": [{"id": "E01", "data": "2026-08-04", "inicio": "19:00", "fim": "20:40",
            "status": "previsto", "aulas": ["Aula 03"], "funcao": "conteudo", "origem": "horario"}],
    }), encoding="utf-8")
    codigo = main(["exportar", "ics", "01", "--turma", "TA", "--raiz", str(semestre_sintetico), "--json"])
    resultado = json.loads(capsys.readouterr().out)
    assert codigo == 0
    assert resultado["proposta"]["itens"][0]["destino"].endswith(".ics")
    assert not list(pasta.glob("*.ics"))
