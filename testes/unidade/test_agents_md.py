from pathlib import Path
from acad.plataformas.skills import SKILLS

RAIZ = Path(__file__).resolve().parents[2]

def test_agents_md_compacto_e_completo():
    t = (RAIZ / "AGENTS.md").read_text(encoding="utf-8")
    assert len(t.splitlines()) <= 80
    assert all(s in t for s in SKILLS)
    assert "acad aplicar" in t and "desfazer" in t and "alunos" in t
