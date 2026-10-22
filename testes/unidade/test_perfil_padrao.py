import json

from acad import contexto
from acad.cli import main
from acad.config import dir_dados
from acad.perfil.perfil import carregar_perfil


def test_sem_configuracao_usa_neutro():
    assert contexto.perfil().id == "neutro"


def test_neutro_sem_marca_e_com_pastas_minusculas():
    neutro = carregar_perfil("neutro")
    assert neutro.slides.capa_linhas == () and neutro.slides.logos_capa == ()
    assert neutro.pasta("planejamento") == "planejamento" and neutro.pasta("arquivo") == "arquivo"
    assert neutro.semestre_de(dir_dados() / "2027-1") == (2027, 1)
    assert neutro.unidade_carga is None
    assert "*/projetos" in neutro.exclusao and "*Notas*" in neutro.exclusao


def test_iniciar_sem_perfil_nao_grava_fasoft(tmp_path, capsys):
    semestre = tmp_path / "2027-1"
    semestre.mkdir()
    assert main(["iniciar", "2027-1", "--raiz", str(semestre), "--confirmar", "--json"]) == 0
    saida = json.loads(capsys.readouterr().out)
    assert saida["dados"]["perfil"] == "neutro"
    assert any("perfil neutro" in aviso for aviso in saida["avisos"])
    assert contexto.carregar_configuracao()["perfil"] == "neutro"


def test_iniciar_sem_perfil_mantem_o_da_configuracao(tmp_path, capsys):
    semestre = tmp_path / "2027-1"
    semestre.mkdir()
    main(["iniciar", "2027-1", "--raiz", str(semestre), "--perfil", "fasoft", "--confirmar", "--json"])
    main(["iniciar", "2027-1", "--raiz", str(semestre), "--confirmar", "--json"])
    capsys.readouterr()
    assert contexto.carregar_configuracao()["perfil"] == "fasoft"


def test_iniciar_com_perfil_inexistente_para(tmp_path, capsys):
    semestre = tmp_path / "2027-1"
    semestre.mkdir()
    assert main(["iniciar", "2027-1", "--raiz", str(semestre), "--perfil", "nao-existe", "--json"]) == 4
