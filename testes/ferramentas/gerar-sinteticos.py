"""Gera planilhas fictícias para os testes e um modelo vazio de calendário."""

from pathlib import Path

import openpyxl


def gerar() -> None:
    raiz = Path(__file__).resolve().parents[2]
    cabecalho = ["Data", "Tipo", "Descrição", "Equivale a"]
    amostra = openpyxl.Workbook()
    planilha = amostra.active
    planilha.append(cabecalho)
    planilha.append(["12/10/2026", "Feriado", "Nossa Senhora Aparecida", None])
    planilha.append(["19/11/2026 a 21/11/2026", "Recesso", "Recesso", None])
    planilha.append(["17/10/2026", "Sábado letivo", "Sábado letivo", None])
    planilha.append(["21/09/2026 a 25/09/2026", "Semana acadêmica", "SETECH", None])
    destino = raiz / "testes" / "amostras" / "sinteticos" / "calendario-2026-2.xlsx"
    destino.parent.mkdir(parents=True, exist_ok=True)
    amostra.save(destino)

    modelo = openpyxl.Workbook()
    modelo.active.append(cabecalho)
    (raiz / "modelos").mkdir(exist_ok=True)
    modelo.save(raiz / "modelos" / "calendario.xlsx")


if __name__ == "__main__":
    gerar()
