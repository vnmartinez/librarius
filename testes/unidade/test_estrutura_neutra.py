from acad.arquivos.privacidade import Workspace
from acad.contexto import localizar_disciplina
from acad.geracao.nomes import arquivos_da_aula
from acad.perfil.perfil import carregar_perfil
from acad.validacao.nomenclatura import disciplinas, validar_nomes
from acad.validacao.validar import validar_semestre

NEUTRO = carregar_perfil("neutro")


def test_nomes_dos_arquivos_seguem_o_perfil():
    nomes = arquivos_da_aula("03", "Grafos", NEUTRO)
    assert nomes["slides"] == "aulas/Aula 03 - Grafos.pptx"
    assert nomes["codigo"] == "codigo/aula-03-grafos"
    assert nomes["lista"] == "atividades/Lista 03 - Grafos.md"
    assert arquivos_da_aula("03", "Grafos", carregar_perfil("fasoft"))["slides"] == "02 - Aulas/Aula 03 - Grafos.pptx"


def test_disciplinas_da_outra_instituicao(semestre_neutro):
    ws = Workspace(semestre_neutro, NEUTRO.exclusao)
    assert sorted(p.name for p in disciplinas(ws, semestre_neutro, NEUTRO)) == ["Algoritmos", "Banco de Dados"]


def test_localizar_sem_numero(semestre_neutro):
    ws = Workspace(semestre_neutro, NEUTRO.exclusao)
    assert localizar_disciplina(ws, semestre_neutro, "algoritmos").name == "Algoritmos"


def test_validar_sem_erro_de_estrutura(semestre_neutro):
    ws = Workspace(semestre_neutro, NEUTRO.exclusao)
    achados = validar_semestre(ws, semestre_neutro, NEUTRO) + validar_nomes(ws, semestre_neutro, NEUTRO)
    assert not [a for a in achados if a.nivel == "erro"], achados
    assert ws.excluido(semestre_neutro / "Algoritmos" / "projetos")
