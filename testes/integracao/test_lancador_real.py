import json, os, subprocess, sys
from pathlib import Path
import pytest

RAIZ = Path(__file__).resolve().parents[2]

@pytest.mark.rede
def test_lancador_cria_ambiente_e_roda(tmp_path):
    env = {**os.environ, "ACAD_DADOS": str(tmp_path)}
    r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "acad.py"), "ambiente", "verificar", "--json"],
                       capture_output=True, text=True, encoding="utf-8", env=env, timeout=900)
    assert r.returncode == 0, r.stdout + r.stderr
    assert json.loads(r.stdout)["ok"] is True
