from datetime import date
import json

from acad.calendario.modelo import de_documento, para_documento
from acad.encontros.gerar import Encontro, gerar_encontros

CALENDARIO = de_documento({"versao_esquema": 1, "calendario": {
    "semestre": "2026-2", "inicio": "2026-10-05", "fim": "2026-10-23",
    "fonte": {"tipo": "manual"}, "status": "confirmado", "confirmado_em": "2026-07-01T10:00:00-03:00",
    "dias": [{"data": "2026-10-12", "tipo": "feriado", "descricao": "Nossa Senhora Aparecida"},
             {"data": "2026-10-17", "tipo": "sabado-letivo", "equivale_a": 1}],
    "eventos": [],
}})
TURMA = {"id": "TA", "disciplina": "ED2", "fuso": "America/Sao_Paulo",
         "horarios": [{"dia_semana": 1, "inicio": "19:00", "fim": "20:40"},
                      {"dia_semana": 3, "inicio": "19:00", "fim": "20:40"}],
         "excecoes": [{"tipo": "cancelamento", "data": "2026-10-21", "motivo": "evento do curso"},
                      {"tipo": "reposicao", "data": "2026-10-24", "inicio": "08:00", "fim": "09:40", "repoe": "2026-10-21"}]}


def _por_data(encontros):
    return {(encontro.data, encontro.inicio): encontro for encontro in encontros}


def test_segundas_e_quartas():
    encontros = gerar_encontros(CALENDARIO, TURMA)
    previstos = [encontro.data for encontro in encontros if encontro.status == "previsto"]
    assert date(2026, 10, 5) in previstos and date(2026, 10, 7) in previstos
    assert date(2026, 10, 6) not in [encontro.data for encontro in encontros]


def test_feriado_cancela():
    encontro = _por_data(gerar_encontros(CALENDARIO, TURMA))[(date(2026, 10, 12), "19:00")]
    assert encontro.status == "cancelado" and "Aparecida" in encontro.motivo


def test_sabado_letivo_segue_segunda():
    encontro = _por_data(gerar_encontros(CALENDARIO, TURMA))[(date(2026, 10, 17), "19:00")]
    assert encontro.status == "previsto" and encontro.origem == "sabado-letivo"


def test_excecao_e_reposicao_da_turma():
    encontros = _por_data(gerar_encontros(CALENDARIO, TURMA))
    assert encontros[(date(2026, 10, 21), "19:00")].status == "cancelado"
    reposicao = encontros[(date(2026, 10, 24), "08:00")]
    assert reposicao.status == "previsto" and reposicao.origem == "reposicao"


def test_reposicao_fora_do_periodo_ainda_entra():
    assert (date(2026, 10, 24), "08:00") in _por_data(gerar_encontros(CALENDARIO, TURMA))


def test_ids_cronologicos():
    encontros = gerar_encontros(CALENDARIO, TURMA)
    assert [encontro.id for encontro in encontros] == [f"E{i:02d}" for i in range(1, len(encontros) + 1)]
    assert encontros == sorted(encontros, key=lambda encontro: (encontro.data, encontro.inicio))


def test_regerar_preserva_status_e_aulas():
    encontros = gerar_encontros(CALENDARIO, TURMA)
    encontros[0].status, encontros[0].aulas = "realizado", ["Aula 01"]
    novos = gerar_encontros(CALENDARIO, TURMA, anteriores=encontros)
    assert novos[0].status == "realizado" and novos[0].aulas == ["Aula 01"]


def test_calendario_vence_anterior():
    encontros = gerar_encontros(CALENDARIO, TURMA)
    alvo = next(encontro for encontro in encontros if encontro.data == date(2026, 10, 12))
    alvo.status = "previsto"
    novos = _por_data(gerar_encontros(CALENDARIO, TURMA, anteriores=encontros))
    assert novos[(date(2026, 10, 12), "19:00")].status == "cancelado"


def test_minutos():
    encontro = Encontro("E01", date(2026, 10, 5), "19:00", "20:40", "previsto", [], "conteudo", "horario")
    assert encontro.minutos == 100


def test_cli_gera_proposta_sem_gravar(capsys, semestre_sintetico):
    from acad import esquemas
    from acad.cli import main

    disciplina = semestre_sintetico / "01 - Disc A - 3º Período" / "01 - Planejamento"
    (disciplina / "turma-TA.yaml").write_text(
        esquemas.para_yaml({"versao_esquema": 1, "turma": TURMA}), encoding="utf-8"
    )
    administracao = semestre_sintetico / "00 - Administração Acadêmica"
    (administracao / "calendario.yaml").write_text(
        esquemas.para_yaml(para_documento(CALENDARIO)), encoding="utf-8"
    )
    codigo = main(["encontros", "gerar", "01", "--turma", "TA", "--raiz", str(semestre_sintetico), "--json"])
    resultado = json.loads(capsys.readouterr().out)
    assert codigo == 0
    assert resultado["proposta"]["itens"][0]["destino"].endswith("01 - Planejamento/encontros-TA.yaml")
    assert not (disciplina / "encontros-TA.yaml").exists()


def test_cli_recusa_calendario_rascunho(capsys, semestre_sintetico):
    from acad import esquemas
    from acad.cli import main

    administracao = semestre_sintetico / "00 - Administração Acadêmica"
    documento = para_documento(CALENDARIO)
    documento["calendario"]["status"] = "rascunho"
    (administracao / "calendario.yaml").write_text(
        esquemas.para_yaml(documento), encoding="utf-8"
    )
    codigo = main(["encontros", "gerar", "01", "--turma", "TA", "--raiz", str(semestre_sintetico), "--json"])
    resultado = json.loads(capsys.readouterr().out)
    assert codigo == 1 and resultado["erros"][0]["codigo"] == "calendario-nao-confirmado"
