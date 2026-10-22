import json, shutil, subprocess, sys
from pathlib import Path
from acad.plataformas import versao

RAIZ = Path(__file__).resolve().parents[2]
ARQS = [a for a, _ in versao.ARQUIVOS]

def _copia(tmp_path):
    d = tmp_path / "p"
    for a in ARQS + ["scripts/sincronizar-versao.py"]:
        (d / a).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(RAIZ / a, d / a)
    return d

def test_uma_versao_so():
    assert len(set(versao.ler_todas(RAIZ).values())) == 1

def test_aplicar_muda_so_a_versao(tmp_path):
    d = _copia(tmp_path)
    antes = {a: (d / a).read_bytes() for a in ARQS}
    versao.aplicar(d, "0.2.0")
    assert set(versao.ler_todas(d).values()) == {"0.2.0"}
    for a in ARQS:
        velho = antes[a].decode("utf-8").replace("0.1.0", "0.2.0")
        assert (d / a).read_bytes().decode("utf-8") == velho, a

def test_verificar_sai_1_se_divergir(tmp_path):
    d = _copia(tmp_path)
    p = d / ".codex-plugin" / "plugin.json"
    p.write_text(p.read_text(encoding="utf-8").replace("0.1.0", "0.9.9"), encoding="utf-8")
    r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "sincronizar-versao.py"), "--verificar", "--raiz", str(d)])
    assert r.returncode == 1
    r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "sincronizar-versao.py"), "--verificar"])
    assert r.returncode == 0
