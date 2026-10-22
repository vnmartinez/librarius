"""Verificações automáticas não invasivas: só leitura, nada é instalado nem alterado."""
import json, shutil, subprocess
from pathlib import Path
import pytest

RAIZ = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.hosts


def _rodar(*cmd, tempo=60):
    cmd = [shutil.which(cmd[0]) or cmd[0], *cmd[1:]]
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                          timeout=tempo, cwd=RAIZ)


def _exige(cli):
    if not shutil.which(cli):
        pytest.skip(f"{cli} ausente")


def test_claude_valida_o_plugin():
    _exige("claude")
    r = _rodar("claude", "plugin", "validate", str(RAIZ), "--strict")
    assert r.returncode == 0 and "Validation passed" in (r.stdout or ""), (r.stdout or "") + (r.stderr or "")


def test_codex_lista_marketplaces_somente_leitura():
    _exige("codex")
    assert _rodar("codex", "plugin", "marketplace", "--help").returncode == 0
    r = _rodar("codex", "plugin", "marketplace", "list")
    assert r.returncode == 0 and "MARKETPLACE" in (r.stdout or "")


def test_antigravity_lista_plugins_em_json():
    _exige("agy")
    r = _rodar("agy", "plugin", "list", "--json")
    assert r.returncode == 0 and isinstance(json.loads(r.stdout), list)


def test_antigravity_valida_o_plugin():
    _exige("agy")
    r = _rodar("agy", "plugin", "validate", str(RAIZ), "--json")
    assert r.returncode == 0
    assert not [f for f in json.loads(r.stdout)["findings"] if f["severity"] == "error"]


def test_opencode_responde_a_versao():
    _exige("opencode")
    r = _rodar("opencode", "--version")
    assert r.returncode == 0 and (r.stdout or "").strip()
