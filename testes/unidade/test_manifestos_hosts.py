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


def _editar(d, rel, fn):
    m = d / rel
    j = json.loads(m.read_text(encoding="utf-8")); fn(j)
    m.write_text(json.dumps(j), encoding="utf-8")


def test_codex_ok():
    assert manifestos.validar_codex(RAIZ) == []

def test_codex_recusa_version_na_raiz(tmp_path):
    d = _copia(tmp_path)
    _editar(d, "plugin.json", lambda j: j.update(version="0.1.0"))
    assert manifestos.validar_codex(d)

def test_codex_recusa_policy_invalida(tmp_path):
    d = _copia(tmp_path)
    _editar(d, ".agents/plugins/marketplace.json", lambda j: j["plugins"][0]["policy"].update(installation="SEMPRE"))
    assert any("installation" in p for p in manifestos.validar_codex(d))

def test_codex_recusa_sem_category(tmp_path):
    d = _copia(tmp_path)
    _editar(d, ".agents/plugins/marketplace.json", lambda j: j["plugins"][0].pop("category"))
    assert any("category" in p for p in manifestos.validar_codex(d))


def test_antigravity_ok():
    assert manifestos.validar_antigravity(RAIZ) == []

def test_antigravity_recusa_chave_extra(tmp_path):
    d = _copia(tmp_path)
    _editar(d, "plugin.json", lambda j: j.update(displayName="Librarius"))
    assert any("displayName" in p for p in manifestos.validar_antigravity(d))

def test_antigravity_recusa_nome_invalido(tmp_path):
    d = _copia(tmp_path)
    _editar(d, "plugin.json", lambda j: j.update(name="libra rius"))
    assert manifestos.validar_antigravity(d)


@pytest.mark.hosts
def test_antigravity_validate_oficial():
    import subprocess
    if not shutil.which("agy"):
        pytest.skip("agy ausente")
    r = subprocess.run(["agy", "plugin", "validate", str(RAIZ), "--json"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0, (r.stdout or "") + (r.stderr or "")
    dados = json.loads(r.stdout)
    assert dados["components"]["skills"] == 7
    assert not [f for f in dados["findings"] if f["severity"] == "error"]


def test_opencode_ok():
    assert manifestos.validar_opencode(RAIZ) == []

def test_opencode_recusa_json_invalido(tmp_path):
    d = _copia(tmp_path)
    (d / "opencode.json").write_text('{"skills": ["./skills"],}', encoding="utf-8")
    assert manifestos.validar_opencode(d)

def test_opencode_recusa_skills_como_texto(tmp_path):
    d = _copia(tmp_path)
    _editar(d, "opencode.json", lambda j: j.update(skills="./skills"))
    assert any("skills" in p for p in manifestos.validar_opencode(d))

def test_opencode_recusa_caminho_inexistente(tmp_path):
    d = _copia(tmp_path)
    _editar(d, "opencode.json", lambda j: j.update(skills=["./nao-existe"]))
    assert manifestos.validar_opencode(d)

def test_opencode_instalar_cita_as_duas_formas(tmp_path):
    d = _copia(tmp_path)
    (d / ".opencode" / "INSTALAR.md").write_text("só a opção skills", encoding="utf-8")
    assert any("INSTALAR" in p for p in manifestos.validar_opencode(d))
