import json

from acad import esquemas
from acad.cli import main
from acad.mensagens import contem_termo_tecnico
from acad.perfil.perfil import carregar_perfil, pasta_perfis_usuario


def _rodar(capsys, *argumentos):
    codigo = main([*argumentos, "--json"])
    return codigo, json.loads(capsys.readouterr().out)


def test_criar_so_propoe_e_aplicar_grava(capsys, semestre_neutro):
    codigo, saida = _rodar(capsys, "perfil", "criar", "--raiz", str(semestre_neutro),
                           "--id", "faculdade-x", "--instituicao", "Faculdade X", "--cor", "1F3A5F")
    assert codigo == 0 and saida["proposta"]
    assert "2027-1" in saida["mensagem"] and "2 disciplinas" in saida["mensagem"]
    assert not contem_termo_tecnico(saida["mensagem"])
    assert not (pasta_perfis_usuario() / "faculdade-x.yaml").exists()
    assert _rodar(capsys, "aplicar", saida["proposta"]["id"])[0] == 0
    assert carregar_perfil("faculdade-x").slides.paleta["principal"] == "1F3A5F"


def test_criar_de_novo_substitui_e_desfazer_volta(capsys, semestre_neutro):
    base = ["perfil", "criar", "--raiz", str(semestre_neutro), "--id", "fx"]
    _, primeira = _rodar(capsys, *base, "--instituicao", "Antes")
    _rodar(capsys, "aplicar", primeira["proposta"]["id"])
    _, segunda = _rodar(capsys, *base, "--instituicao", "Depois")
    assert segunda["proposta"]["itens"][0]["tipo"] == "substituir"
    _rodar(capsys, "aplicar", segunda["proposta"]["id"])
    assert carregar_perfil("fx").instituicao == "Depois"
    _rodar(capsys, "desfazer")
    assert carregar_perfil("fx").instituicao == "Antes"


def test_importar_valida(capsys, tmp_path):
    from testes.unidade.test_perfil import _v1
    documento = _v1()
    documento["perfil"]["id"] = "colega"
    arquivo = tmp_path / "colega.yaml"
    arquivo.write_text(esquemas.para_yaml(documento), encoding="utf-8")
    codigo, saida = _rodar(capsys, "perfil", "importar", "--arquivo", str(arquivo))
    assert codigo == 0 and saida["proposta"]["itens"][0]["destino"] == "colega.yaml"
    del documento["perfil"]["instituicao"]
    arquivo.write_text(esquemas.para_yaml(documento), encoding="utf-8")
    codigo, saida = _rodar(capsys, "perfil", "importar", "--arquivo", str(arquivo))
    assert codigo == 1 and "Falta o nome da instituição." in saida["mensagem"]


def test_listar_mostra_o_em_uso(capsys):
    codigo, saida = _rodar(capsys, "perfil", "listar")
    assert codigo == 0
    assert saida["dados"]["em_uso"] == "neutro"
    assert {"fasoft", "neutro"} <= set(saida["dados"]["perfis"])


def test_criar_com_id_invalido(capsys, semestre_neutro):
    codigo, saida = _rodar(capsys, "perfil", "criar", "--raiz", str(semestre_neutro),
                           "--id", "Minha Faculdade", "--instituicao", "X")
    assert codigo == 1 and "letras minúsculas" in saida["mensagem"]


def test_criar_com_cor_invalida_explica(capsys, semestre_neutro):
    codigo, saida = _rodar(capsys, "perfil", "criar", "--raiz", str(semestre_neutro),
                           "--id", "fx", "--instituicao", "X", "--cor", "12GG00")
    assert codigo == 1 and "cor" in saida["mensagem"]
    assert not contem_termo_tecnico(saida["mensagem"])
