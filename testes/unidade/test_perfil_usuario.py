import pytest

from acad import esquemas
from acad.erros import ErroAcad
from acad.mensagens import contem_termo_tecnico
from acad.perfil.perfil import carregar_perfil, pasta_perfis_usuario, perfis_disponiveis
from acad.perfil.validar import problemas_do_perfil
from testes.unidade.test_perfil import _v1


def _gravar(id, documento):
    pasta = pasta_perfis_usuario()
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / f"{id}.yaml").write_text(esquemas.para_yaml(documento), encoding="utf-8")


def test_perfil_do_usuario_vence_o_empacotado():
    documento = _v1()
    documento["perfil"]["instituicao"] = "Minha cópia"
    _gravar("fasoft", documento)
    assert carregar_perfil("fasoft").instituicao == "Minha cópia"
    assert perfis_disponiveis()["fasoft"] == "usuario"


def test_perfil_novo_do_usuario():
    documento = _v1()
    documento["perfil"]["id"] = "faculdade-x"
    _gravar("faculdade-x", documento)
    assert carregar_perfil("faculdade-x").id == "faculdade-x"


@pytest.mark.parametrize("id", ["../fora", "Fasoft", "a/b", "", "x" * 41])
def test_id_invalido(id):
    with pytest.raises(ErroAcad) as erro:
        carregar_perfil(id)
    assert erro.value.codigo == "perfil-invalido"


def test_perfil_inexistente_pede_decisao():
    with pytest.raises(ErroAcad) as erro:
        carregar_perfil("nao-existe")
    assert erro.value.codigo == "perfil-nao-encontrado" and erro.value.saida == 4
    assert "criar" in erro.value.mensagem


def test_mensagens_simples():
    documento = _v1()
    del documento["perfil"]["instituicao"]
    documento["perfil"]["disciplina_pasta"] = "(sem fechar"
    documento["perfil"]["extra"] = 1
    problemas = problemas_do_perfil(documento)
    assert "Falta o nome da instituição." in problemas
    assert "O perfil tem uma informação que não conheço: “extra”." in problemas
    assert all(not contem_termo_tecnico(texto) for texto in problemas)


def test_regra_que_nao_compila():
    documento = _v1()
    documento["perfil"]["disciplina_pasta"] = "(sem fechar"
    assert problemas_do_perfil(documento) == ["A regra que reconhece as pastas das disciplinas não funciona."]


def test_perfil_quebrado_no_usuario_da_erro_simples():
    documento = _v1()
    del documento["perfil"]["instituicao"]
    _gravar("quebrado", documento)
    with pytest.raises(ErroAcad) as erro:
        carregar_perfil("quebrado")
    assert erro.value.codigo == "perfil-invalido"
    assert erro.value.mensagem == "O perfil da instituição tem problemas: Falta o nome da instituição."
