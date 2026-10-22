from datetime import date, datetime
from pathlib import Path
import io

import openpyxl
import pytest

from acad.cronograma.planilha import ler_cronograma, linhas_na_data, parse_data
from acad.erros import ErroAcad

XLSX = (
    Path(__file__).resolve().parents[1] / "amostras" / "fasoft" / "2026" / "Segundo Semestre"
    / "04 - Estrutura de Dados 2 - 5º Período" / "01 - Planejamento"
    / "Cronograma - Estrutura de Dados 2.xlsx"
)


@pytest.mark.parametrize("valor,esperado", [
    (datetime(2026, 7, 28), date(2026, 7, 28)),
    ("28/07/2026", date(2026, 7, 28)),
    ("2026-07-28", date(2026, 7, 28)),
    ("28/7", date(2026, 7, 28)),
    ("x", None), (None, None), ("31/02", None),
])
def test_parse_data(valor, esperado):
    assert parse_data(valor, 2026) == esperado


def test_linha_do_primeiro_dia():
    [linha] = linhas_na_data(XLSX.read_bytes(), date(2026, 7, 28))
    assert (linha.linha, linha.semana, linha.aula, linha.aula_num) == (4, "Semana 1", "Aula 01", "01")
    assert linha.topico.startswith("Apresenta")


def test_segunda_linha_sem_semana_no_modo_oraculo():
    [linha] = linhas_na_data(XLSX.read_bytes(), date(2026, 7, 31))
    assert linha.semana == "" and linha.aula == "Aula 02"


def test_leitura_por_cabecalho_herda_semana():
    linhas = ler_cronograma(XLSX.read_bytes(), 2026)
    assert linhas[0].data == date(2026, 7, 28)
    assert linhas[1].semana == "Semana 1"
    assert any(linha.topico.upper().startswith("PRIMEIRA AVALIA") for linha in linhas)


def test_sem_cabecalho():
    pasta = openpyxl.Workbook()
    pasta.active["A1"] = "nada"
    dados = io.BytesIO()
    pasta.save(dados)
    with pytest.raises(ErroAcad) as erro:
        ler_cronograma(dados.getvalue(), 2026)
    assert erro.value.codigo == "planilha-sem-cabecalho"
