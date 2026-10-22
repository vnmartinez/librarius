import pytest


def pytest_configure(config):
    for nome, descricao in [
        ("drive", "lê G:\\Meu Drive\\Fasoft em modo leitura"),
        ("hosts", "exige a CLI de um host instalada"),
        ("latex", "exige tectonic ou pdflatex"),
    ]:
        config.addinivalue_line("markers", f"{nome}: {descricao}")


@pytest.fixture(autouse=True)
def dados_isolados(tmp_path, monkeypatch):
    monkeypatch.setenv("ACAD_DADOS", str(tmp_path / "_dados"))
