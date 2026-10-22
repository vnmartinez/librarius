from acad import config


def test_acad_dados_tem_prioridade(tmp_path, monkeypatch):
    monkeypatch.setenv("ACAD_DADOS", str(tmp_path / "a"))
    monkeypatch.setenv("CLAUDE_PLUGIN_DATA", str(tmp_path / "b"))
    assert config.dir_dados() == tmp_path / "a"


def test_claude_plugin_data_quando_sem_acad_dados(tmp_path, monkeypatch):
    monkeypatch.delenv("ACAD_DADOS", raising=False)
    monkeypatch.setenv("CLAUDE_PLUGIN_DATA", str(tmp_path / "b"))
    assert config.dir_dados() == tmp_path / "b"


def test_registro_grava_detalhe(tmp_path):
    config.registrar_detalhe("falha X")
    assert "falha X" in (config.dir_dados() / "registro.log").read_text(encoding="utf-8")
