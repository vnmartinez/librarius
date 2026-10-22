import zipfile
from pathlib import Path
import pytest
from acad.plataformas import chatgpt, skills

RAIZ = Path(__file__).resolve().parents[2]

@pytest.fixture(scope="module")
def pacotes(tmp_path_factory):
    destino = tmp_path_factory.mktemp("dist")
    return chatgpt.empacotar(RAIZ, destino)

def test_um_zip_por_skill(pacotes):
    assert sorted(p.stem for p in pacotes) == sorted(skills.SKILLS)

def test_zip_com_pasta_de_topo_e_um_skill_md(pacotes):
    for z in pacotes:
        nomes = zipfile.ZipFile(z).namelist()
        assert {n.split("/")[0] for n in nomes} == {z.stem}
        assert sum(n.endswith("SKILL.md") for n in nomes) == 1
        assert z.stat().st_size <= 50 * 1024 * 1024

def test_sem_referencias_ao_computador(pacotes):
    for z in pacotes:
        t = zipfile.ZipFile(z).read(f"{z.stem}/SKILL.md").decode("utf-8")
        assert "scripts/acad.py" not in t and "${CLAUDE_PLUGIN_ROOT}" not in t
        assert "não acesso os arquivos do seu computador" in t

def test_frontmatter_preservado(pacotes, tmp_path):
    for z in pacotes:
        zipfile.ZipFile(z).extractall(tmp_path)
        probs = [p for p in skills.problemas(tmp_path / z.stem) if "trecho comum" not in p]
        assert probs == []
