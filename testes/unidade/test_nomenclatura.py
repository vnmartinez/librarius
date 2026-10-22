from pathlib import Path

import pytest

from acad.arquivos.privacidade import Workspace
from acad.perfil.perfil import carregar_perfil
from acad.validacao.nomenclatura import disciplinas, validar_nomes

AMOSTRA_SEM = Path(__file__).resolve().parents[1] / "amostras" / "fasoft" / "2026" / "Segundo Semestre"


@pytest.fixture
def achados():
    perfil = carregar_perfil()
    workspace = Workspace(AMOSTRA_SEM, perfil.exclusao)
    return validar_nomes(workspace, AMOSTRA_SEM, perfil)


def _tem(achados, codigo, trecho):
    return any(achado.codigo == codigo and trecho in achado.caminho for achado in achados)


def test_disciplinas_da_amostra():
    perfil = carregar_perfil()
    nomes = [pasta.name for pasta in disciplinas(Workspace(AMOSTRA_SEM, perfil.exclusao), AMOSTRA_SEM, perfil)]
    assert nomes == ["04 - Estrutura de Dados 2 - 5º Período"]


def test_divergencias_reais_de_ed2(achados):
    assert _tem(achados, "pasta-sem-prefixo", "02 - Aulas/_ferramentas")
    assert _tem(achados, "sufixo-proibido", "Cronograma - Estrutura de Dados 2.xlsx.bak")
    assert _tem(achados, "sufixo-proibido", "Aula 18 - Arvores Rubro-Negras - Propriedades (v2).pptx")
    assert _tem(achados, "sufixo-proibido", "Recepção dos Calouros (1).xlsx")
    assert _tem(achados, "nome-lista-sem-prefixo", "Lista - BST.pdf")


def test_arquivo_morto_nao_e_cobrado(achados):
    assert not any("99 - Arquivo" in achado.caminho for achado in achados)


def test_nomes_corretos_nao_geram_achado(achados):
    assert not any("Aula 01 - Apresentação da Disciplina.pptx" in achado.caminho for achado in achados)
    assert not any("Aula 17 - Atividade 02" in achado.caminho for achado in achados)


def test_lock_do_office_ignorado(achados):
    assert not any("~$" in achado.caminho for achado in achados)


def test_mensagens_em_portugues_simples(achados):
    from acad.mensagens import contem_termo_tecnico
    assert achados and all(not contem_termo_tecnico(achado.mensagem) for achado in achados)


def test_pasta_protegida_avaliada_so_pelo_nome(semestre_sintetico):
    perfil = carregar_perfil()
    workspace = Workspace(semestre_sintetico, perfil.exclusao)
    list(workspace.percorrer(semestre_sintetico))
    achados = validar_nomes(workspace, semestre_sintetico, perfil)
    assert any(achado.codigo == "pasta-sem-prefixo" and achado.caminho == "11-Relatórios" for achado in achados)
