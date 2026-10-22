import json, shutil
from pathlib import Path
import pytest
from acad.plataformas import manifestos

RAIZ = Path(__file__).resolve().parents[2]

def _copia(tmp_path):
    destino = tmp_path / "plugin"
    shutil.copytree(RAIZ, destino, ignore=shutil.ignore_patterns(".git", ".venv", "testes", "__pycache__", "node_modules", "*.egg-info"))
    return destino

def test_claude_ok():
    assert manifestos.validar_claude(RAIZ) == []

def test_claude_recusa_bin(tmp_path):
    d = _copia(tmp_path); (d / "bin").mkdir()
    assert any("bin" in p for p in manifestos.validar_claude(d))

def test_claude_recusa_caminho_sem_ponto_barra(tmp_path):
    d = _copia(tmp_path); m = d / ".claude-plugin" / "plugin.json"
    j = json.loads(m.read_text(encoding="utf-8")); j["skills"] = "skills/"
    m.write_text(json.dumps(j), encoding="utf-8")
    assert manifestos.validar_claude(d)

def test_claude_recusa_chave_desconhecida(tmp_path):
    d = _copia(tmp_path); m = d / ".claude-plugin" / "plugin.json"
    j = json.loads(m.read_text(encoding="utf-8")); j["inventado"] = 1
    m.write_text(json.dumps(j), encoding="utf-8")
    assert any("inventado" in p for p in manifestos.validar_claude(d))

def test_claude_recusa_marketplace_com_fonte_errada(tmp_path):
    d = _copia(tmp_path); m = d / ".claude-plugin" / "marketplace.json"
    j = json.loads(m.read_text(encoding="utf-8")); j["plugins"][0]["source"] = "../fora"
    m.write_text(json.dumps(j), encoding="utf-8")
    assert manifestos.validar_claude(d)

@pytest.mark.hosts
def test_claude_validate_oficial():
    import subprocess
    if not shutil.which("claude"):
        pytest.skip("claude ausente")
    r = subprocess.run(["claude", "plugin", "validate", str(RAIZ), "--strict"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0 and "Validation passed" in r.stdout, r.stdout + r.stderr
