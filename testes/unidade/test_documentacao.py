from pathlib import Path
RAIZ = Path(__file__).resolve().parents[2]

def test_instalar_sem_terminal_antes_do_avancado():
    t = (RAIZ / "INSTALAR.md").read_text(encoding="utf-8")
    antes, _, depois = t.partition("## Para usuários avançados")
    assert depois, "falta a seção para usuários avançados"
    assert "```" not in antes                      # nenhum comando antes da seção avançada
    for host in ("Claude Code", "Cowork", "Codex", "Antigravity", "OpenCode", "ChatGPT"):
        assert host in antes
    assert "claude plugin marketplace add" in depois and "agy plugin install" in depois

def test_readme_publico_certo():
    t = (RAIZ / "README.md").read_text(encoding="utf-8")
    assert "sem conhecimento de programação" in t or "sem formação técnica" in t
    assert "alunos" in t and "MIT" in t
