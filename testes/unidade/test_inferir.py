import pytest

from acad.erros import ErroAcad
from acad.perfil.inferir import inferir_perfil
from acad.perfil.perfil import perfil_de_documento
from acad.perfil.validar import problemas_do_perfil


def test_infere_a_outra_instituicao(semestre_neutro):
    documento, resumo = inferir_perfil(semestre_neutro, "faculdade-x", "Faculdade X")
    assert problemas_do_perfil(documento) == []
    perfil = perfil_de_documento(documento)
    assert perfil.id == "faculdade-x" and perfil.instituicao == "Faculdade X"
    assert perfil.semestre_de(semestre_neutro) == (2027, 1)
    assert perfil.pasta("aulas") == "aulas" and perfil.pasta("referencias") == "referencias"
    assert perfil.pasta("projetos") == "projetos"
    assert "*/projetos" in perfil.exclusao
    assert resumo == {"ano": 2027, "periodo": 1, "disciplinas": ["Algoritmos", "Banco de Dados"],
                      "papeis_criados": []}
    assert perfil.slides.capa_linhas == ()


def test_papel_ausente_ganha_nome_neutro(tmp_path):
    semestre = tmp_path / "2026" / "2º Semestre"
    for disciplina in ("01 - Redes", "02 - Sistemas"):
        for subpasta in ("01 - Planejamento das Aulas", "02 - Aulas", "03 - Exercícios"):
            (semestre / disciplina / subpasta).mkdir(parents=True)
    documento, resumo = inferir_perfil(semestre, "x", "X")
    perfil = perfil_de_documento(documento)
    assert perfil.semestre_de(semestre) == (2026, 2)
    assert perfil.pasta("planejamento") == "01 - Planejamento das Aulas"
    assert perfil.pasta("atividades") == "03 - Exercícios"
    assert perfil.partes_disciplina("01 - Redes")["nome"] == "Redes"
    assert perfil.re_pasta.pattern == r"^\d{2} - "
    assert set(resumo["papeis_criados"]) == {"projetos", "referencias", "codigo", "arquivo"}
    assert perfil.subpastas_disciplina[-4:] == ("projetos", "referencias", "codigo", "arquivo")


def test_cor_e_rodape(semestre_neutro):
    documento, _ = inferir_perfil(semestre_neutro, "x", "X", cor="1f3a5f",
                                  rodape=["FACULDADE X", "Curso Y"], local="Cidade — {ano}")
    slides = perfil_de_documento(documento).slides
    assert slides.paleta["principal"] == "1F3A5F"
    assert slides.capa_linhas == ("FACULDADE X", "Curso Y") and slides.capa_local == "Cidade — {ano}"


def test_modelos_achados(semestre_neutro):
    (semestre_neutro / "modelos" / "slides da casa").mkdir()
    (semestre_neutro / "modelos" / "latex").mkdir()
    (semestre_neutro / "modelos" / "latex" / "prova-base.tex").write_text("x", encoding="utf-8")
    perfil = perfil_de_documento(inferir_perfil(semestre_neutro, "x", "X")[0])
    assert perfil.modelo_slides == "slides da casa"
    assert perfil.modelo_prova == "latex/prova-base.tex"


def test_semestre_sem_ano_pede_decisao(tmp_path):
    (tmp_path / "semestre atual" / "Disc" / "aulas").mkdir(parents=True)
    with pytest.raises(ErroAcad) as erro:
        inferir_perfil(tmp_path / "semestre atual", "x", "X")
    assert erro.value.saida == 4 and "2027-1" in erro.value.mensagem


def test_nao_entra_em_pasta_protegida(semestre_neutro, monkeypatch):
    lidos = []
    from acad.arquivos import privacidade
    original = privacidade.Workspace.listar
    monkeypatch.setattr(privacidade.Workspace, "listar",
                        lambda self, pasta: lidos.append(pasta.name) or original(self, pasta))
    inferir_perfil(semestre_neutro, "x", "X")
    assert "projetos" not in lidos
