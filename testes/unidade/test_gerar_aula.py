from datetime import datetime

import pytest
import yaml

from acad.arquivos.privacidade import Workspace
from acad.erros import ErroAcad
from acad.geracao.aula import planejar_aula
from acad.geracao.nomes import arquivos_da_aula, slug
from acad.geracao.slides import GeradorSlidesBloqueado, GeradorSlidesFalso


DISC = "01 - Disc A - 3º Período"
CONTEUDO = {
    "tema": "Rotações AVL",
    "roteiro": {"objetivo": "Aplicar rotações", "blocos": [
        {"titulo": "Revisão", "minutos": 20, "texto": "…"},
        {"titulo": "Rotações", "minutos": 80, "texto": "…"}]},
    "codigo": {"arquivos": {"main.go": "package main\n"}},
    "lista": {"questoes": [{"enunciado": "Insira 3, 2, 1 numa AVL."}]},
    "slides": {"slides": [{"tipo": "capa", "titulo": "Rotações AVL"}]},
}


@pytest.fixture
def disc(semestre_sintetico):
    pasta = semestre_sintetico / DISC
    (pasta / "01 - Planejamento" / "aulas.yaml").write_text(yaml.safe_dump({
        "versao_esquema": 1, "disciplina": "DA", "aulas": [{
            "id": "Aula 03", "tema": "Rotações AVL", "status": "planejada", "objetivos": [],
            "prerequisitos": [], "encontros_necessarios": 1,
        }],
    }, allow_unicode=True), encoding="utf-8")
    return pasta


def test_nomes_canonicos():
    nomes = arquivos_da_aula("03", "Rotações AVL: casos?")
    assert nomes["roteiro"] == "02 - Aulas/Aula 03 - Roteiro de Aula - Rotações AVL casos.md"
    assert nomes["codigo"] == "06 - Código e Exemplos/aula-03-rotacoes-avl-casos"
    assert slug("Árvore B+") == "arvore-b"


def test_planeja_arquivos_e_manifesto(semestre_sintetico, disc):
    operacoes, avisos = planejar_aula(Workspace(semestre_sintetico, []), semestre_sintetico,
                                      disc, "03", CONTEUDO, GeradorSlidesFalso(), datetime(2026, 10, 20, 14, 2))
    destinos = {operacao.destino for operacao in operacoes}
    assert f"{DISC}/02 - Aulas/Aula 03 - Rotações AVL.pptx" in destinos
    assert f"{DISC}/06 - Código e Exemplos/aula-03-rotacoes-avl/main.go" in destinos
    aulas = yaml.safe_load(next(op for op in operacoes if op.destino.endswith("aulas.yaml")).conteudo)
    aula = aulas["aulas"][0]
    assert aula["status"] == "rascunho" and aula["manifesto"]["aprovado"] is False
    assert f"{DISC}/01 - Planejamento/aulas.yaml#Aula 03" in aula["manifesto"]["entradas"]


def test_slides_bloqueados_nao_impedem_resto(semestre_sintetico, disc):
    operacoes, avisos = planejar_aula(Workspace(semestre_sintetico, []), semestre_sintetico,
                                      disc, "03", CONTEUDO, GeradorSlidesBloqueado(), datetime(2026, 10, 20))
    assert not any(op.destino.endswith(".pptx") for op in operacoes)
    assert any("slides ficam para depois" in aviso.lower() for aviso in avisos)


def test_aula_aprovada_recusa(semestre_sintetico, disc):
    arquivo = disc / "01 - Planejamento" / "aulas.yaml"
    documento = yaml.safe_load(arquivo.read_text(encoding="utf-8"))
    documento["aulas"][0]["status"] = "aprovada"
    arquivo.write_text(yaml.safe_dump(documento, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ErroAcad) as erro:
        planejar_aula(Workspace(semestre_sintetico, []), semestre_sintetico,
                      disc, "03", CONTEUDO, GeradorSlidesFalso(), datetime(2026, 10, 20))
    assert erro.value.codigo == "aula-aprovada"


def test_estimativa_de_tempo(semestre_sintetico, disc):
    longo = {**CONTEUDO, "roteiro": {"objetivo": "x", "blocos": [
        {"titulo": "a", "minutos": 140, "texto": "…"}]}}
    (disc / "01 - Planejamento" / "encontros-TA.yaml").write_text(yaml.safe_dump({
        "versao_esquema": 1, "gerado_por": "acad 0.1.0", "gerado_em": "2026-10-01T10:00:00-03:00",
        "entradas": {}, "encontros": [{"id": "E03", "data": "2026-08-10", "inicio": "19:00", "fim": "20:40",
                                    "status": "previsto", "aulas": ["Aula 03"], "funcao": "conteudo", "origem": "horario"}],
    }), encoding="utf-8")
    _, avisos = planejar_aula(Workspace(semestre_sintetico, []), semestre_sintetico,
                              disc, "03", longo, GeradorSlidesFalso(), datetime(2026, 10, 20))
    assert any("140 min" in aviso and "100 min" in aviso for aviso in avisos)


def test_conteudo_invalido(semestre_sintetico, disc):
    with pytest.raises(ErroAcad) as erro:
        planejar_aula(Workspace(semestre_sintetico, []), semestre_sintetico,
                      disc, "03", {"tema": 1}, GeradorSlidesFalso(), datetime(2026, 10, 20))
    assert erro.value.codigo == "esquema-invalido"


def test_cli_gera_proposta_sem_gravar(capsys, semestre_sintetico, disc, tmp_path):
    import json
    from acad.cli import main

    arquivo = tmp_path / "conteudo.json"
    arquivo.write_text(json.dumps(CONTEUDO, ensure_ascii=False), encoding="utf-8")
    codigo = main(["gerar", "aula", "01", "--aula", "03", "--conteudo", str(arquivo),
                   "--raiz", str(semestre_sintetico), "--json"])
    resultado = json.loads(capsys.readouterr().out)
    assert codigo == 0
    assert resultado["proposta"] and any("aulas.yaml" in item["destino"]
                                         for item in resultado["proposta"]["itens"])
    assert any("slides ficam para depois" in aviso.lower() for aviso in resultado["avisos"])
    assert not list((disc / "02 - Aulas").glob("*.md"))
