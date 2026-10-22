import json
from pathlib import Path

from acad.geracao.avaliacao import nome_arquivo, renderizar, versoes
from acad.geracao.latex import escapar_latex
from acad.cli import main


MODELO = Path(__file__).resolve().parents[2] / "modelos" / "prova.tex"


def test_escapar_latex():
    assert escapar_latex("50% de R$ 10_000") == r"50\% de R\$ 10\_000"


def test_versoes_reprodutiveis_e_resposta_acompanha_alternativa():
    questoes = [{"id": str(i), "tipo": "multipla-escolha", "enunciado": str(i),
                "alternativas": ["A", "B", "C"], "resposta": "B", "pontos": 1} for i in range(8)]
    primeiras = versoes(questoes, 1234, 2)
    assert primeiras == versoes(questoes, 1234, 2)
    assert primeiras[1] != versoes(questoes, 9999, 2)[1]
    assert primeiras[0] == questoes
    assert all("B" in questao["alternativas"] and questao["resposta"] == "B" for questao in primeiras[1])


def test_nomes_da_prova():
    assert nome_arquivo("Estrutura de Dados 2", "N1", "Avaliação", "TA", None, False, "tex") == (
        "Estrutura de Dados 2 - N1 - Avaliação - TA.tex")
    assert nome_arquivo("Estrutura de Dados 2", "N1", "Avaliação", "TA", "B", False, "tex") == (
        "Estrutura de Dados 2 - N1 - Avaliação - TA - Versão B.tex")
    assert nome_arquivo("Estrutura de Dados 2", "N1", "Avaliação", "TA", None, True, "tex") == (
        "Estrutura de Dados 2 - N1 - Avaliação - TA - Gabarito.tex")


def test_renderizar_prova_e_gabarito():
    modelo = MODELO.read_text(encoding="utf-8")
    dados = {"titulo": "AVALIAÇÃO 1", "disciplina": "Estrutura de Dados 2",
             "professor": "Docente", "data": "2026-10-22"}
    questoes = [{"id": "Q1", "tipo": "discursiva", "enunciado": "Explique AVL.",
                "resposta": "Árvore balanceada", "pontos": 2}]
    prova = renderizar(modelo, dados, questoes, False)
    gabarito = renderizar(modelo, dados, questoes, True)
    assert r"\avaliacaoDisciplina{Estrutura de Dados 2}" in prova
    assert "Explique AVL" in prova and "Árvore balanceada" not in prova
    assert r"\textbf{Árvore balanceada}" in gabarito


def _preparar(semestre_sintetico, data_encontro: str, tmp_path):
    from acad import esquemas

    pasta = semestre_sintetico / "01 - Disc A - 3º Período" / "01 - Planejamento"
    (pasta / "aulas.yaml").write_text(esquemas.para_yaml({
        "versao_esquema": 1, "disciplina": "DA",
        "aulas": [{"id": "Aula 09", "tema": "AVL", "status": "planejada"}],
    }), encoding="utf-8")
    (pasta / "encontros-TA.yaml").write_text(esquemas.para_yaml({
        "versao_esquema": 1, "gerado_por": "acad 0.1.0", "gerado_em": "2026-10-01T10:00:00-03:00",
        "entradas": {}, "encontros": [{"id": "E09", "data": data_encontro,
            "inicio": "19:00", "fim": "20:40", "status": "previsto", "aulas": ["Aula 09"],
            "funcao": "conteudo", "origem": "horario"}],
    }), encoding="utf-8")
    conteudo = tmp_path / "questoes.json"
    conteudo.write_text(json.dumps({"aulas_cobertas": ["Aula 09"], "objetivos": [],
        "questoes": [{"id": "Q1", "enunciado": "Explique AVL.", "tipo": "discursiva",
                      "resposta": "Árvore balanceada", "pontos": 2}]}, ensure_ascii=False), encoding="utf-8")
    return conteudo


def test_cli_recusa_prova_sobre_aula_futura(capsys, semestre_sintetico, tmp_path):
    conteudo = _preparar(semestre_sintetico, "2026-09-08", tmp_path)
    codigo = main(["gerar", "avaliacao", "01", "--etapa", "N1", "--turma", "TA",
                   "--data", "2026-09-01", "--conteudo", str(conteudo),
                   "--raiz", str(semestre_sintetico), "--json"])
    resultado = json.loads(capsys.readouterr().out)
    assert codigo == 1 and resultado["erros"][0]["codigo"] == "avaliacao-sobre-nao-ministrada"


def test_cli_propõe_arquivos_na_pasta_de_avaliacoes(capsys, semestre_sintetico, tmp_path):
    conteudo = _preparar(semestre_sintetico, "2026-08-20", tmp_path)
    codigo = main(["gerar", "avaliacao", "01", "--etapa", "N1", "--turma", "TA",
                   "--data", "2026-09-01", "--conteudo", str(conteudo),
                   "--raiz", str(semestre_sintetico), "--json"])
    resultado = json.loads(capsys.readouterr().out)
    assert codigo == 0
    destinos = [item["destino"] for item in resultado["proposta"]["itens"]]
    assert any("08 - Avaliações/N1/" in destino and destino.endswith(".tex") for destino in destinos)
    assert any(destino.endswith("01 - Planejamento/avaliacoes/N1-TA.yaml") for destino in destinos)
