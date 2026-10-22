import pytest

from acad import esquemas

TURMA_OK = {
    "versao_esquema": 1,
    "turma": {
        "id": "TA", "disciplina": "ED2", "fuso": "America/Sao_Paulo",
        "horarios": [{"dia_semana": 2, "inicio": "19:00", "fim": "20:40", "sala": "B-204"}],
        "excecoes": [
            {"tipo": "cancelamento", "data": "2026-10-12", "motivo": "feriado"},
            {"tipo": "reposicao", "data": "2026-10-17", "inicio": "08:00", "fim": "09:40", "repoe": "2026-10-12"},
        ],
    },
}

DISC_OK = {
    "versao_esquema": 1,
    "disciplina": {
        "codigo": "ED2", "nome": "Estrutura de Dados II",
        "pasta": "04 - Estrutura de Dados 2 - 5º Período", "semestre": "2026-2",
        "carga_horaria": {"valor": 60, "unidade": "hora_relogio", "minutos_hora_aula": None},
        "objetivos": [{"id": "OBJ-01", "descricao": "Implementar árvores balanceadas", "bloom": "aplicar"}],
        "configuracao": {"template_slides": "institucional", "template_provas": "latex-padrao", "idioma": "pt-BR"},
        "planejamento": {"status": "rascunho", "aprovado_em": None},
    },
}


def test_turma_valida():
    assert esquemas.validar("turma", TURMA_OK) == []


def test_reposicao_sem_repoe_invalida():
    turma = {**TURMA_OK["turma"], "excecoes": [{"tipo": "reposicao", "data": "2026-10-17", "inicio": "08:00", "fim": "09:40"}]}
    assert esquemas.validar("turma", {**TURMA_OK, "turma": turma})


def test_hora_mal_formatada():
    turma = {**TURMA_OK["turma"], "horarios": [{"dia_semana": 2, "inicio": "7h", "fim": "20:40"}]}
    assert any("inicio" in erro for erro in esquemas.validar("turma", {**TURMA_OK, "turma": turma}))


def test_hora_aula_exige_minutos():
    disciplina = {**DISC_OK["disciplina"], "carga_horaria": {"valor": 72, "unidade": "hora_aula", "minutos_hora_aula": None}}
    assert esquemas.validar("disciplina", {**DISC_OK, "disciplina": disciplina})


def test_unidade_nula_aceita_ate_d3():
    disciplina = {**DISC_OK["disciplina"], "carga_horaria": {"valor": 60, "unidade": None, "minutos_hora_aula": None}}
    assert esquemas.validar("disciplina", {**DISC_OK, "disciplina": disciplina}) == []


def test_campo_extra_rejeitado():
    assert esquemas.validar("disciplina", {**DISC_OK, "disciplina": {**DISC_OK["disciplina"], "inventado": 1}})


def test_aula_id_formato():
    documento = {"versao_esquema": 1, "disciplina": "ED2", "aulas": [{"id": "Aula 3", "tema": "x", "status": "planejada"}]}
    assert esquemas.validar("aula", documento)


def test_calendario_sabado_letivo_exige_equivalencia():
    documento = {"versao_esquema": 1, "calendario": {
        "semestre": "2026-2", "inicio": "2026-07-27", "fim": "2026-12-12",
        "fonte": {"tipo": "manual"}, "status": "rascunho", "confirmado_em": None,
        "dias": [{"data": "2026-10-17", "tipo": "sabado-letivo"}], "eventos": [],
    }}
    assert esquemas.validar("calendario", documento)


def test_carregar_yaml_converte_datas():
    assert esquemas.carregar_yaml("d: 2026-10-12\n") == {"d": "2026-10-12"}


@pytest.mark.parametrize("nome", ["calendario", "disciplina", "turma", "encontro", "aula", "questao", "avaliacao", "manifesto", "perfil", "semestre"])
def test_todo_esquema_existe_e_e_estrito(nome):
    esquema = esquemas.carregar_esquema(nome)
    assert esquema["$id"].endswith(f"/esquemas/{nome}.schema.json")
