from __future__ import annotations

from acad.encontros.gerar import Encontro
from acad.erros import ErroAcad
from acad.validacao.achados import Achado


def minutos_validos(encontros: list[Encontro]) -> int:
    return sum(encontro.minutos for encontro in encontros if encontro.status != "cancelado")


def em_unidade(minutos: int, unidade: str, minutos_hora_aula: int | None) -> float:
    if unidade == "hora_relogio":
        return minutos / 60
    if unidade == "hora_aula" and minutos_hora_aula and minutos_hora_aula > 0:
        return minutos / minutos_hora_aula
    raise ErroAcad("unidade-invalida", "Falta confirmar como contar a carga horária da disciplina.")


def _numero(valor: float) -> str:
    return f"{valor:.1f}".replace(".", ",").removesuffix(",0")


def verificar_carga(encontros: list[Encontro], carga_horaria: dict) -> list[Achado]:
    unidade = carga_horaria.get("unidade")
    if unidade is None:
        return [Achado(
            "carga-unidade-nao-confirmada", "aviso",
            "Ainda falta você me dizer se a carga da disciplina é contada em hora-aula ou em hora cheia.",
        )]
    calculado = em_unidade(minutos_validos(encontros), unidade,
                           carga_horaria.get("minutos_hora_aula"))
    esperado = float(carga_horaria["valor"])
    diferenca = esperado - calculado
    if abs(diferenca) <= 0.01:
        return []
    situacao = "faltam" if diferenca > 0 else "sobram"
    nome_unidade = "hora-aula" if unidade == "hora_aula" else "hora cheia"
    return [Achado(
        "carga-horaria-incompativel", "erro",
        f"Na carga da disciplina, {situacao} {_numero(abs(diferenca))} h ({nome_unidade}).",
    )]
