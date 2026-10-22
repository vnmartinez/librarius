import json
from argparse import Namespace

from acad import contexto
from acad.cli import main
from acad.config import dir_dados
from acad.perfil.detectar import detectar


def test_detectar_semestre_e_pasta_protegida_existente(semestre_sintetico):
    dados = detectar(semestre_sintetico, contexto.perfil())
    assert len(dados["semestres"]) == 1
    assert len(dados["disciplinas"]) == 1
    assert dados["disciplinas"][0]["subpastas_faltando"] == []


def test_iniciar_so_grava_com_confirmar(capsys, semestre_sintetico):
    arquivo = dir_dados() / "configuracao.yaml"
    argumentos = ["iniciar", "2026-2", "--raiz", str(semestre_sintetico), "--json"]
    assert main(argumentos) == 0
    assert not arquivo.exists()
    capsys.readouterr()
    assert main(argumentos + ["--confirmar"]) == 0
    assert arquivo.exists()
    assert contexto.raiz_semestre(Namespace(raiz=None)) == semestre_sintetico


def test_turma_rejeita_dia_invalido(capsys, semestre_sintetico):
    codigo = main(["turma", "criar", "01", "--turma", "TA", "--horario", "8 19:00 20:40",
                   "--raiz", str(semestre_sintetico), "--json"])
    dados = json.loads(capsys.readouterr().out)
    assert codigo != 0 and "dia da semana vai de 1" in dados["mensagem"]


def test_disciplina_exige_minutos_na_hora_aula(capsys, semestre_sintetico):
    codigo = main(["disciplina", "criar", "DA", "--pasta", "01 - Disc A - 3º Período",
                   "--nome", "Disc A", "--carga", "80", "--unidade", "hora_aula",
                   "--raiz", str(semestre_sintetico), "--json"])
    dados = json.loads(capsys.readouterr().out)
    assert codigo != 0 and "minutos" in dados["mensagem"]


def test_disciplina_estrutura_propõe_so_pasta_faltante(capsys, semestre_sintetico):
    pasta = semestre_sintetico / "01 - Disc A - 3º Período" / "05 - Materiais de Referência"
    pasta.rmdir()
    codigo = main(["disciplina", "estrutura", "01", "--raiz", str(semestre_sintetico), "--json"])
    dados = json.loads(capsys.readouterr().out)
    assert codigo == 0
    assert [(item["tipo"], item["destino"].split("/")[-1]) for item in dados["proposta"]["itens"]] == [
        ("criar-pasta", "05 - Materiais de Referência")]
    assert not pasta.exists()


def test_criar_disciplina_e_turma_so_propõe(capsys, semestre_sintetico):
    argumentos = ["disciplina", "criar", "DA", "--pasta", "01 - Disc A - 3º Período",
                  "--nome", "Disc A", "--carga", "80", "--unidade", "hora_aula",
                  "--minutos-hora-aula", "50", "--raiz", str(semestre_sintetico), "--json"]
    assert main(argumentos) == 0
    disciplina = json.loads(capsys.readouterr().out)
    assert disciplina["dados"]["disciplina"]["planejamento"]["status"] == "rascunho"
    assert disciplina["proposta"]["itens"][0]["destino"].endswith("disciplina.yaml")
    assert main(["turma", "criar", "01", "--turma", "TA", "--horario", "2 19:00 20:40 A1",
                 "--raiz", str(semestre_sintetico), "--json"]) == 0
    turma = json.loads(capsys.readouterr().out)
    assert turma["dados"]["turma"]["horarios"][0]["sala"] == "A1"
    assert turma["proposta"]["itens"][0]["destino"].endswith("turma-TA.yaml")
    pasta = semestre_sintetico / "01 - Disc A - 3º Período" / "01 - Planejamento"
    assert not (pasta / "disciplina.yaml").exists() and not (pasta / "turma-TA.yaml").exists()


def test_disciplina_sem_unidade_usa_hora_aula_de_50_do_perfil(capsys, semestre_sintetico):
    codigo = main(["disciplina", "criar", "DA", "--pasta", "01 - Disc A - 3º Período",
                   "--nome", "Disc A", "--carga", "72", "--raiz", str(semestre_sintetico), "--json"])
    carga = json.loads(capsys.readouterr().out)["dados"]["disciplina"]["carga_horaria"]
    assert codigo == 0 and carga["unidade"] == "hora_aula" and carga["minutos_hora_aula"] == 50
