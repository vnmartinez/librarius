from datetime import date
from pathlib import Path

from acad.cronograma.consulta import consultar, encontrar_raiz, palavras_chave, resumo_texto
from acad.perfil.perfil import carregar_perfil

AMOSTRA = Path(__file__).resolve().parents[1] / "amostras" / "fasoft"


def test_encontra_raiz_subindo():
    assert encontrar_raiz(AMOSTRA / "2026" / "Segundo Semestre") == AMOSTRA


def test_palavras_chave_sem_acento_e_stopwords():
    assert palavras_chave("Árvores Binárias de Busca (BST) - Aula") == ["arvores", "binarias", "busca"]


def test_tipo_avaliacao():
    resultado = consultar(AMOSTRA, date(2026, 9, 1), carregar_perfil().exclusao)
    assert resultado["aulas"][0]["tipo"] == "avaliacao"


def test_resumo_texto_simples():
    from acad.mensagens import contem_termo_tecnico
    texto = resumo_texto(consultar(AMOSTRA, date(2026, 7, 28), carregar_perfil().exclusao))
    assert "28/07/2026" in texto and "Estrutura de Dados 2" in texto
    assert not contem_termo_tecnico(texto)
