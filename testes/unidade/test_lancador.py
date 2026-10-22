import importlib.util, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("lancador", RAIZ / "scripts" / "acad.py")
L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)

def test_versao_e_dependencias():
    assert L.versao() == "0.1.0"
    assert any(d.startswith("pyyaml") for d in L.dependencias())

def test_dir_dados_prioridade(monkeypatch, tmp_path):
    monkeypatch.setenv("ACAD_DADOS", str(tmp_path))
    assert L.dir_dados() == tmp_path

def test_preparar_nao_reinstala(tmp_path, monkeypatch):
    chamadas = []
    monkeypatch.setattr(L.shutil, "which", lambda n: None)
    fake = lambda cmd, **k: chamadas.append(cmd) or type("R", (), {"returncode": 0})()
    L.preparar(tmp_path / "amb", executar=fake)
    n = len(chamadas)
    L.preparar(tmp_path / "amb", executar=fake)
    assert n >= 2 and len(chamadas) == n

def test_python_antigo(monkeypatch, capsys):
    monkeypatch.setattr(L.sys, "version_info", (3, 9, 0))
    assert L.main(["ambiente", "verificar"]) == 3
    assert "Python" in capsys.readouterr().out

def test_falha_de_instalacao_explica(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("ACAD_DADOS", str(tmp_path))
    monkeypatch.setattr(L, "preparar", lambda amb, **k: (_ for _ in ()).throw(L.FalhaInstalacao("x")))
    assert L.main(["ambiente", "verificar"]) == 3
    assert "internet" in capsys.readouterr().out
