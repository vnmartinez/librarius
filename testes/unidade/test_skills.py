from pathlib import Path
import subprocess, sys
import pytest
from acad.plataformas import skills
from acad import cli
import acad.comandos  # noqa: F401  (registra os comandos)

RAIZ = Path(__file__).resolve().parents[2]

def test_existem_as_sete_skills():
    assert sorted(p.name for p in (RAIZ / "skills").iterdir() if p.is_dir()) == sorted(skills.SKILLS)

@pytest.mark.parametrize("nome", skills.SKILLS)
def test_conformidade(nome):
    assert skills.problemas(RAIZ / "skills" / nome) == []

@pytest.mark.parametrize("nome", skills.SKILLS)
def test_comandos_citados_existem(nome):
    _, corpo = skills.ler_skill(RAIZ / "skills" / nome)
    assert skills.comandos_citados(corpo) <= set(cli._COMANDOS) | {"aplicar", "desfazer"}

def test_trecho_sincronizado():
    r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "sincronizar-skills.py"), "--verificar"])
    assert r.returncode == 0

def test_regra_de_nome_pega_erros(tmp_path):
    d = tmp_path / "Errada"; d.mkdir()
    (d / "SKILL.md").write_text("---\nname: errada\ndescription: x\n---\ncorpo\n", encoding="utf-8")
    probs = skills.problemas(d)
    assert any("pasta" in p for p in probs) and any("Quando usar" in p for p in probs)
