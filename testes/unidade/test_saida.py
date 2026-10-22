import json

from acad.saida import Resultado
from acad.erros import ErroAcad
from acad import mensagens


def test_envelope_json_tem_campos_da_spec():
    dados = json.loads(Resultado(ok=True, mensagem="Tudo certo.").para_json())
    assert set(dados) == {"ok", "mensagem", "dados", "avisos", "erros", "proposta"}
    assert dados["ok"] is True and dados["proposta"] is None


def test_json_preserva_acentos():
    assert "Período" in Resultado(ok=True, mensagem="Período").para_json()


def test_texto_mostra_mensagem_e_avisos():
    texto = Resultado(ok=True, mensagem="Pronto.", avisos=["Falta o slide."]).para_texto()
    assert "Pronto." in texto and "Falta o slide." in texto


def test_erro_acad_guarda_codigo_e_saida():
    erro = ErroAcad("raiz-nao-encontrada", "Não achei a pasta.", "x", saida=3)
    assert (erro.codigo, erro.saida, str(erro)) == (
        "raiz-nao-encontrada", 3, "Não achei a pasta."
    )


def test_mensagens_do_catalogo_sem_termo_tecnico():
    for codigo, texto in mensagens.MENSAGENS.items():
        assert not mensagens.contem_termo_tecnico(texto), codigo


def test_msg_formata_parametros():
    assert "3" in mensagens.msg("propostas-arquivos", n=3)
