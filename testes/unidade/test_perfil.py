from acad.perfil.perfil import carregar_perfil


def test_perfil_fasoft_carrega():
    perfil = carregar_perfil("fasoft")
    assert perfil.subpastas_disciplina[0] == "01 - Planejamento"
    assert perfil.pasta_arquivo == "99 - Arquivo"
    assert perfil.etapas_avaliacao == ("N1", "N2", "N3")


def test_regex_disciplina_extrai_partes():
    correspondencia = carregar_perfil().disciplina_pasta.match("04 - Estrutura de Dados 2 - 5º Período")
    assert correspondencia["num"] == "04"
    assert correspondencia["nome"] == "Estrutura de Dados 2"
    assert correspondencia["periodo"] == "5º Período"


def test_unidade_carga_pendente_d3():
    perfil = carregar_perfil()
    assert perfil.unidade_carga is None and perfil.minutos_hora_aula is None


def test_sufixos_proibidos_pegam_casos_reais():
    perfil = carregar_perfil()
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
    exclusao = carregar_perfil().exclusao
    assert "*Notas*" in exclusao and "* - TFC*/02 - Alunos" in exclusao
