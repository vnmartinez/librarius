import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

from acad.cronograma.consulta import consultar
from acad.cronograma.planilha import ler_cronograma
from acad.perfil.perfil import carregar_perfil

TESTES = Path(__file__).resolve().parents[1]
AMOSTRA = TESTES / "amostras" / "fasoft"
ORACULO = TESTES / "referencia" / "verificar_cronograma.py"
XLSX = AMOSTRA / "2026/Segundo Semestre/04 - Estrutura de Dados 2 - 5º Período/01 - Planejamento/Cronograma - Estrutura de Dados 2.xlsx"
IGNORAR = {"disciplina_dir", "cronograma_path", "tipo"}


def _oraculo(raiz: Path, alvo: date) -> dict:
    resultado = subprocess.run(
        [sys.executable, str(ORACULO), "--dir", str(raiz), "--data", alvo.isoformat(), "--json"],
        capture_output=True, text=True, encoding="utf-8", check=True,
    )
    return json.loads(resultado.stdout)


def _normalizar(resultado: dict) -> list[dict]:
    saida = []
    for aula in resultado["aulas"]:
        registro = {chave: valor for chave, valor in aula.items() if chave not in IGNORAR}
        registro["materiais"] = {chave: sorted(valor) for chave, valor in aula["materiais"].items()}
        saida.append(registro)
    return sorted(saida, key=lambda registro: (registro["disciplina"], registro["linha"]))


def _datas():
    datas = {linha.data for linha in ler_cronograma(XLSX.read_bytes(), 2026) if linha.data}
    return sorted(datas | {min(datas) - timedelta(days=1)})


@pytest.mark.parametrize("alvo", _datas(), ids=str)
def test_paridade_com_oraculo_nas_amostras(alvo):
    esperado = _oraculo(AMOSTRA, alvo)
    obtido = consultar(AMOSTRA, alvo, carregar_perfil("fasoft"))
    assert obtido["quantidade_aulas"] == esperado["quantidade_aulas"]
    assert _normalizar(obtido) == _normalizar(esperado)


@pytest.mark.drive
def test_paridade_no_drive_real():
    raiz = Path(r"G:\Meu Drive\Fasoft")
    if not raiz.exists():
        pytest.skip("Drive ausente")
    obtido = consultar(raiz, date(2026, 7, 28), carregar_perfil("fasoft"))
    assert any(
        aula["disciplina"] == "04 - Estrutura de Dados 2 - 5º Período"
        and aula["aula"] == "Aula 01"
        for aula in obtido["aulas"]
    )
