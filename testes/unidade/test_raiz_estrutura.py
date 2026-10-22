from pathlib import Path

from acad.cronograma.consulta import encontrar_raiz
from acad.perfil.detectar import detectar
from acad.perfil.perfil import carregar_perfil

AMOSTRA = Path(__file__).resolve().parents[1] / "amostras" / "fasoft"
FASOFT, NEUTRO = carregar_perfil("fasoft"), carregar_perfil("neutro")


def test_fasoft_de_qualquer_ponto_acha_a_raiz():
    semestre = AMOSTRA / "2026" / "Segundo Semestre"
    disciplina = semestre / "04 - Estrutura de Dados 2 - 5º Período" / "02 - Aulas"
    for inicio in (AMOSTRA, semestre, disciplina):
        assert encontrar_raiz(inicio, FASOFT) == AMOSTRA


def test_nao_le_agents_md(tmp_path):
    (tmp_path / "AGENTS.md").write_text("# Fasoft\n", encoding="utf-8")
    assert encontrar_raiz(tmp_path, FASOFT) is None


def test_outra_instituicao(semestre_neutro):
    base = semestre_neutro.parent
    for inicio in (base, semestre_neutro, semestre_neutro / "Algoritmos" / "aulas"):
        assert encontrar_raiz(inicio, NEUTRO) == base


def test_detectar_outra_instituicao(semestre_neutro):
    dados = detectar(semestre_neutro, NEUTRO)
    assert dados["semestres"] == [{"pasta": "2027-1", "ano": 2027, "periodo": 1}]
    assert dados["raiz"] == str(semestre_neutro.parent) == dados["raiz_fasoft"]
    assert sorted(d["nome"] for d in dados["disciplinas"]) == ["Algoritmos", "Banco de Dados"]
    assert dados["pasta_avaliacoes"] == "avaliacoes" and dados["pasta_modelos"] == "modelos"
    algoritmos = next(d for d in dados["disciplinas"] if d["nome"] == "Algoritmos")
    assert algoritmos["subpastas_faltando"] == []
    banco = next(d for d in dados["disciplinas"] if d["nome"] == "Banco de Dados")
    assert banco["subpastas_faltando"] == ["projetos"]
