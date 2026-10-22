import pytest
from pathlib import Path


def pytest_configure(config):
    for nome, descricao in [
        ("drive", "lê G:\\Meu Drive\\Fasoft em modo leitura"),
        ("hosts", "exige a CLI de um host instalada"),
        ("latex", "exige tectonic ou pdflatex"),
        ("rede", "baixa dependências da internet"),
    ]:
        config.addinivalue_line("markers", f"{nome}: {descricao}")


@pytest.fixture(autouse=True)
def dados_isolados(tmp_path, monkeypatch):
    monkeypatch.setenv("ACAD_DADOS", str(tmp_path / "_dados"))


def _mk(caminho: Path, conteudo: str = ""):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(conteudo, encoding="utf-8")


@pytest.fixture
def perfil_fasoft(monkeypatch):
    from acad import contexto
    monkeypatch.setattr(contexto, "PERFIL_PADRAO", "fasoft")


@pytest.fixture
def semestre_sintetico(tmp_path, perfil_fasoft) -> Path:
    raiz = tmp_path / "fasoft"
    _mk(raiz / "AGENTS.md", "# Fasoft - Diretrizes do Projeto\n")
    semestre = raiz / "2026" / "Segundo Semestre"
    _mk(semestre / "README.md", "```text\nSegundo Semestre/\n├── 00 - Administração Acadêmica/\n├── 01 - Disc A - 3º Período/\n├── 08 - Avaliações/\n└── 09 - Modelos/\n```\n")
    _mk(semestre / "2026 - Notas N1.gsheet", "{}")
    (semestre / "00 - Administração Acadêmica").mkdir(parents=True)
    disciplina = semestre / "01 - Disc A - 3º Período"
    for subpasta in [
        "01 - Planejamento", "02 - Aulas", "03 - Atividades e Listas",
        "05 - Materiais de Referência", "06 - Código e Exemplos", "99 - Arquivo",
    ]:
        (disciplina / subpasta).mkdir(parents=True)
    _mk(disciplina / "04 - Projetos e Entregáveis" / "entrega-aluno.txt", "nome do aluno")
    _mk(semestre / "07 - TFC 1" / "02 - Alunos" / "Fulano" / "tcc.docx", "x")
    for etapa in ["N1", "N2", "N3"]:
        (semestre / "08 - Avaliações" / etapa).mkdir(parents=True)
    (semestre / "09 - Modelos").mkdir()
    _mk(semestre / "11-Relatórios" / "rel.docx", "x")
    return semestre


@pytest.fixture
def semestre_neutro(tmp_path) -> Path:
    semestre = tmp_path / "Materiais" / "2027-1"
    (semestre / "administracao").mkdir(parents=True)
    (semestre / "avaliacoes" / "AV1").mkdir(parents=True)
    (semestre / "modelos").mkdir()
    for disciplina in ("Algoritmos", "Banco de Dados"):
        for subpasta in ("planejamento", "aulas", "atividades", "referencias", "codigo", "arquivo"):
            (semestre / disciplina / subpasta).mkdir(parents=True)
    _mk(semestre / "Algoritmos" / "projetos" / "entrega-aluno.txt", "nome do aluno")
    _mk(semestre / "Notas 2027-1.xlsx", "x")
    return semestre


@pytest.fixture(autouse=True)
def bloquear_drive(monkeypatch):
    monkeypatch.setenv("ACAD_BLOQUEAR_ESCRITA", r"G:\;G:/;/g/")
