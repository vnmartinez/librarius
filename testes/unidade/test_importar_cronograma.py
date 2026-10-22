from pathlib import Path

import yaml

from acad.cronograma.importar import importar_cronograma
from acad.cronograma.planilha import ler_cronograma

TESTES = Path(__file__).resolve().parents[1]
XLSX = TESTES / "amostras/fasoft/2026/Segundo Semestre/04 - Estrutura de Dados 2 - 5º Período/01 - Planejamento/Cronograma - Estrutura de Dados 2.xlsx"
TURMA = {"id": "TA", "disciplina": "ED2", "fuso": "America/Sao_Paulo",
         "horarios": [{"dia_semana": 2, "inicio": "19:00", "fim": "20:40"},
                      {"dia_semana": 5, "inicio": "19:00", "fim": "20:40"}]}


def test_importa_amostra_real():
    encontros, aulas = importar_cronograma(ler_cronograma(XLSX.read_bytes(), 2026), TURMA, "ED2")
    assert encontros[0].aulas == ["Aula 01"] and encontros[0].inicio == "19:00"
    avaliacoes = [encontro for encontro in encontros if encontro.funcao == "avaliacao"]
    assert avaliacoes and all(encontro.aulas == [] for encontro in avaliacoes)
    ids = [aula["id"] for aula in aulas["aulas"]]
    assert "Aula 01" in ids and "Aula 11" not in ids


def test_saida_bate_com_esperado():
    from datetime import datetime
    from acad.planejamento.arquivos import documento_encontros

    encontros, aulas = importar_cronograma(ler_cronograma(XLSX.read_bytes(), 2026), TURMA, "ED2")
    esperado = yaml.safe_load((TESTES / "esperados" / "ed2-aulas.yaml").read_text(encoding="utf-8"))
    assert aulas == esperado
    esperado_encontros = yaml.safe_load(
        (TESTES / "esperados" / "ed2-encontros-TA.yaml").read_text(encoding="utf-8")
    )
    assert documento_encontros(encontros, {}, "0.1.0", datetime(2026, 10, 22)) == esperado_encontros


def test_cli_importar_cria_duas_propostas_sem_gravar(capsys, semestre_sintetico):
    import json
    from acad import esquemas
    from acad.cli import main

    planejamento = semestre_sintetico / "01 - Disc A - 3º Período" / "01 - Planejamento"
    (planejamento / "Cronograma - Disc A.xlsx").write_bytes(XLSX.read_bytes())
    (planejamento / "turma-TA.yaml").write_text(
        esquemas.para_yaml({"versao_esquema": 1, "turma": TURMA}), encoding="utf-8"
    )
    codigo = main(["cronograma", "importar", "01", "--turma", "TA", "--raiz", str(semestre_sintetico), "--json"])
    resultado = json.loads(capsys.readouterr().out)
    assert codigo == 0
    assert {item["destino"].split("/")[-1] for item in resultado["proposta"]["itens"]} == {"encontros-TA.yaml", "aulas.yaml"}
    assert not (planejamento / "aulas.yaml").exists()


def test_cli_avisa_quando_dia_nao_esta_no_horario(capsys, semestre_sintetico):
    import json
    from acad import esquemas
    from acad.cli import main

    planejamento = semestre_sintetico / "01 - Disc A - 3º Período" / "01 - Planejamento"
    (planejamento / "Cronograma - Disc A.xlsx").write_bytes(XLSX.read_bytes())
    turma = {**TURMA, "horarios": [{"dia_semana": 1, "inicio": "19:00", "fim": "20:40"}]}
    (planejamento / "turma-TA.yaml").write_text(
        esquemas.para_yaml({"versao_esquema": 1, "turma": turma}), encoding="utf-8"
    )
    codigo = main(["cronograma", "importar", "01", "--turma", "TA", "--raiz", str(semestre_sintetico), "--json"])
    resultado = json.loads(capsys.readouterr().out)
    assert codigo == 0 and any("horário" in aviso for aviso in resultado["avisos"])
