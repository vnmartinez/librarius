from datetime import date
from pathlib import Path

from acad.arquivos.privacidade import Workspace
from acad.calendario.modelo import de_documento
from acad.encontros.gerar import Encontro
from acad.manifestos.hashes import hash_item
from acad.validacao import regras


def E(id, d, aulas=(), status="previsto", origem="horario"):
    return Encontro(id, d, "19:00", "20:40", status, list(aulas), "conteudo", origem)


CAL = de_documento({"versao_esquema": 1, "calendario": {
    "semestre": "2026-2", "inicio": "2026-08-01", "fim": "2026-12-12",
    "fonte": {"tipo": "manual"}, "status": "confirmado", "confirmado_em": "2026-07-01T10:00:00-03:00",
    "dias": [{"data": "2026-10-12", "tipo": "feriado"}], "eventos": []}})


def test_encontro_em_feriado():
    [a] = regras.regra_dia_nao_letivo([E("E01", date(2026, 10, 12))], CAL)
    assert a.codigo == "encontro-em-dia-nao-letivo"
    assert regras.regra_dia_nao_letivo([E("E01", date(2026, 10, 12), status="cancelado")], CAL) == []
    assert regras.regra_dia_nao_letivo([E("E01", date(2026, 10, 12), origem="reposicao")], CAL) == []


def test_prerequisito():
    aulas = [{"id": "Aula 01", "prerequisitos": []}, {"id": "Aula 02", "prerequisitos": ["Aula 01"]}]
    es = [E("E01", date(2026, 8, 3), ["Aula 02"]), E("E02", date(2026, 8, 5), ["Aula 01"])]
    [a] = regras.regra_prerequisitos(aulas, es)
    assert a.codigo == "aula-antes-de-prerequisito" and "Aula 02" in a.mensagem


def test_cobertura():
    disc = {"objetivos": [{"id": "OBJ-01"}, {"id": "OBJ-02"}]}
    aulas = [{"id": "Aula 01", "objetivos": ["OBJ-01"]}]
    avs = [{"etapa": "N1", "objetivos": ["OBJ-01"]}]
    cods = {a.codigo for a in regras.regra_cobertura(disc, aulas, avs)}
    assert cods == {"objetivo-sem-aula", "objetivo-sem-avaliacao"}
    assert {a.codigo for a in regras.regra_cobertura(disc, aulas, [])} == {"objetivo-sem-aula"}


def test_avaliacao_sobre_aula_futura():
    av = {"etapa": "N1", "data": "2026-09-01", "aulas_cobertas": ["Aula 01", "Aula 09"]}
    aulas = [{"id": "Aula 01", "status": "planejada"}, {"id": "Aula 09", "status": "planejada"}]
    es = [E("E01", date(2026, 8, 3), ["Aula 01"]), E("E09", date(2026, 9, 8), ["Aula 09"])]
    [a] = regras.regra_avaliacao_nao_ministrada(av, aulas, es)
    assert "Aula 09" in a.mensagem


def test_numero_repetido_na_amostra():
    aulas = (Path(__file__).resolve().parents[1] / "amostras/fasoft/2026/Segundo Semestre"
             / "04 - Estrutura de Dados 2 - 5º Período/02 - Aulas")
    nums = {a.mensagem.split("“")[1].split("”")[0]
            for a in regras.regra_numero_repetido(Workspace(aulas.parent, []), aulas)}
    assert {"Aula 05", "Aula 07", "Aula 15", "Aula 18"} <= nums


def test_manifesto_aponta_artefato_ausente_e_entrada_alterada(tmp_path):
    disc = tmp_path / "01 - Disc"
    (disc / "01 - Planejamento").mkdir(parents=True)
    aula = {"id": "Aula 01", "tema": "Novo", "manifesto": {
        "artefatos": ["01 - Disc/02 - Aulas/Aula 01.pptx"],
        "entradas": {"01 - Disc/01 - Planejamento/aulas.yaml#Aula 01": hash_item({"id": "Aula 01", "tema": "Antigo"})},
    }}
    achados = regras.regra_manifestos(Workspace(tmp_path, []), tmp_path, disc, [aula])
    assert {a.codigo for a in achados} == {"artefato-ausente", "manifesto-desatualizado"}
    assert any("plano da aula" in a.mensagem for a in achados)


def test_slide_com_tema_mas_numero_divergente(tmp_path):
    disc = tmp_path / "01 - Disc"
    pasta = disc / "02 - Aulas"
    pasta.mkdir(parents=True)
    (pasta / "Aula 03 - Árvores Rubro Negras.pptx").write_bytes(b"")
    achados = regras.regra_slide_divergente(Workspace(tmp_path, []), disc, [
        {"id": "Aula 04", "tema": "Árvores Rubro Negras"}
    ])
    assert len(achados) == 1 and achados[0].codigo == "slide-numeracao-divergente"
