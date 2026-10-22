from datetime import datetime

from acad.arquivos.privacidade import Workspace
from acad.manifestos.hashes import hash_bytes, hash_entrada, hash_item, hash_pasta
from acad.manifestos.manifesto import divergencias, montar_manifesto


def test_hash_bytes_formato():
    assert hash_bytes(b"abc") == "sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_hash_item_ignora_ordem_e_manifesto():
    a = {"id": "Aula 03", "tema": "Rotações AVL", "manifesto": {"x": 1}}
    b = {"tema": "Rotações AVL", "id": "Aula 03"}
    assert hash_item(a) == hash_item(b)


def test_hash_item_muda_com_tema():
    assert hash_item({"id": "Aula 03", "tema": "A"}) != hash_item({"id": "Aula 03", "tema": "B"})


def test_hash_pasta_ignora_lock(tmp_path):
    (tmp_path / "m").mkdir()
    (tmp_path / "m" / "a.js").write_text("1")
    ws = Workspace(tmp_path, [])
    h1 = hash_pasta(ws, tmp_path / "m")
    (tmp_path / "m" / "~$a.pptx").write_text("lixo")
    (tmp_path / "m" / "node_modules").mkdir()
    (tmp_path / "m" / "node_modules" / "x.js").write_text("lixo")
    assert hash_pasta(ws, tmp_path / "m") == h1


def test_hash_entrada_item_arquivo_e_ausente(tmp_path):
    (tmp_path / "aulas.yaml").write_text("versao_esquema: 1\naulas:\n- id: Aula 01\n  tema: Árvores\n", encoding="utf-8")
    ws = Workspace(tmp_path, [])
    assert hash_entrada(ws, tmp_path, "aulas.yaml#Aula 01") == hash_item({"id": "Aula 01", "tema": "Árvores"})
    assert hash_entrada(ws, tmp_path, "aulas.yaml") == hash_bytes((tmp_path / "aulas.yaml").read_bytes())
    assert hash_entrada(ws, tmp_path, "ausente.yaml") is None


def test_divergencias():
    m = montar_manifesto(["x.pptx"], {"a": "sha256:1", "b": "sha256:2"}, "0.1.0", datetime(2026, 10, 20, 14, 2))
    assert divergencias(m, {"a": "sha256:1", "b": "sha256:3"}.get) == ["b"]
    assert divergencias(m, {"a": "sha256:1"}.get) == ["b"]
    assert m["aprovado"] is False and m["aprovado_em"] is None
