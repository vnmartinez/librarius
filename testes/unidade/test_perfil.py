from pathlib import Path

from acad import esquemas
from acad.perfil.perfil import carregar_perfil, perfil_de_documento

V1 = Path(__file__).resolve().parents[1] / "esperados" / "perfil-fasoft-v1.yaml"


def _v1():
    return esquemas.carregar_yaml(V1.read_text(encoding="utf-8"))


def test_perfil_v1_continua_valido():
    assert esquemas.validar("perfil", _v1()) == []


def test_v1_recebe_a_estrutura_que_o_mvp_usava():
    perfil = perfil_de_documento(_v1())
    assert perfil.pasta("planejamento") == "01 - Planejamento"
    assert perfil.pasta("aulas") == "02 - Aulas"
    assert perfil.pasta("arquivo") == "99 - Arquivo"
    assert perfil.re_administracao.match("00 - Administração Acadêmica")
    assert perfil.modelo_slides is None and perfil.modelo_prova is None


def test_fasoft_v2_tem_a_mesma_estrutura_do_v1():
    v1, v2 = perfil_de_documento(_v1()), carregar_perfil("fasoft")
    for campo in ("disciplina_pasta", "subpastas_disciplina", "pasta_arquivo", "pasta_avaliacoes",
                  "pasta_modelos", "etapas_avaliacao", "re_aula", "re_lista", "re_pasta",
                  "sufixos_proibidos", "unidade_carga", "minutos_hora_aula", "exclusao",
                  "re_semestre", "periodos", "re_administracao", "papeis"):
        assert getattr(v1, campo) == getattr(v2, campo), campo
    assert v2.modelo_slides == "Modelo de Slides UniRV"
    assert v2.modelo_prova == "Modelo LaTeX/modelo-prova.tex"


def test_semestre_de_e_base(tmp_path):
    perfil = carregar_perfil("fasoft")
    semestre = tmp_path / "Fasoft" / "2026" / "Segundo Semestre"
    assert perfil.semestre_de(semestre) == (2026, 2)
    assert perfil.base_semestre(semestre) == tmp_path / "Fasoft"
    assert perfil.semestre_de(tmp_path / "2026" / "Terceiro Semestre") is None


def test_partes_disciplina_sem_grupo_vira_none():
    perfil = carregar_perfil("fasoft")
    assert perfil.partes_disciplina("01 - Disc A") == {"num": "01", "nome": "Disc A", "periodo": None}
    assert perfil.partes_disciplina("sem numero") is None


def test_v2_aceita_blocos_novos_e_recusa_chave_desconhecida():
    documento = _v1()
    documento["versao_esquema"] = 2
    documento["perfil"]["estrutura"] = {"semestre": r"^(?P<ano>\d{4})-(?P<periodo>[12])$"}
    assert esquemas.validar("perfil", documento) == []
    documento["perfil"]["estrutura"]["outra"] = 1
    assert esquemas.validar("perfil", documento)


def test_perfil_fasoft_carrega():
    perfil = carregar_perfil("fasoft")
    assert perfil.subpastas_disciplina[0] == "01 - Planejamento"
    assert perfil.pasta_arquivo == "99 - Arquivo"
    assert perfil.etapas_avaliacao == ("N1", "N2", "N3")


def test_regex_disciplina_extrai_partes():
    correspondencia = carregar_perfil("fasoft").disciplina_pasta.match("04 - Estrutura de Dados 2 - 5º Período")
    assert correspondencia["num"] == "04"
    assert correspondencia["nome"] == "Estrutura de Dados 2"
    assert correspondencia["periodo"] == "5º Período"


def test_unidade_carga_d3_hora_aula_de_50_minutos():
    perfil = carregar_perfil("fasoft")
    assert perfil.unidade_carga == "hora_aula" and perfil.minutos_hora_aula == 50


def test_sufixos_proibidos_pegam_casos_reais():
    perfil = carregar_perfil("fasoft")
    for nome in [
        "Aula 18 - Arvores (v2).pptx", "Recepção dos Calouros (1).xlsx",
        "Cronograma - ED2.xlsx.bak", "Aula 05 - BST - copia.pptx",
        "Lista_v2.docx", "X (Revisado).docx",
    ]:
        assert any(regra.search(nome) for regra in perfil.sufixos_proibidos), nome
    assert not any(
        regra.search("Aula 05 - Árvores Binárias de Busca (BST).pptx")
        for regra in perfil.sufixos_proibidos
    )


def test_exclusao_cobre_dados_de_aluno():
    exclusao = carregar_perfil("fasoft").exclusao
    assert "*Notas*" in exclusao and "* - TFC*/02 - Alunos" in exclusao
