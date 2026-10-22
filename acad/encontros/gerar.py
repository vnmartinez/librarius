from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

from acad.calendario.modelo import Calendario, dia, dia_semana_efetivo, letivo


@dataclass
class Encontro:
    id: str
    data: date
    inicio: str
    fim: str
    status: str
    aulas: list[str] = field(default_factory=list)
    funcao: str = "conteudo"
    origem: str = "horario"
    motivo: str | None = None

    @property
    def minutos(self) -> int:
        hora_inicio, minuto_inicio = map(int, self.inicio.split(":"))
        hora_fim, minuto_fim = map(int, self.fim.split(":"))
        return (hora_fim * 60 + minuto_fim) - (hora_inicio * 60 + minuto_inicio)


def gerar_encontros(calendario: Calendario, turma: dict,
                    anteriores: list[Encontro] | None = None) -> list[Encontro]:
    encontros = []
    cancelamentos = {
        date.fromisoformat(item["data"]): item
        for item in turma.get("excecoes", []) if item["tipo"] == "cancelamento"
    }
    cancelados_calendario = set()
    data = calendario.inicio
    while data <= calendario.fim:
        especial = dia(calendario, data)
        if letivo(calendario, data) or (especial and especial.tipo in ("feriado", "recesso")):
            dia_efetivo = dia_semana_efetivo(calendario, data)
            for horario in turma["horarios"]:
                if horario["dia_semana"] != dia_efetivo:
                    continue
                status = "previsto"
                motivo = None
                if especial and especial.tipo in ("feriado", "recesso"):
                    status = "cancelado"
                    motivo = especial.descricao or especial.tipo
                    cancelados_calendario.add((data, horario["inicio"]))
                elif data in cancelamentos:
                    status = "cancelado"
                    motivo = cancelamentos[data].get("motivo") or "cancelamento"
                origem = "sabado-letivo" if especial and especial.tipo in ("sabado-letivo", "troca-de-dia") else "horario"
                encontros.append(Encontro("", data, horario["inicio"], horario["fim"],
                                          status, [], "conteudo", origem, motivo))
        data += timedelta(days=1)

    for excecao in turma.get("excecoes", []):
        if excecao["tipo"] == "reposicao":
            encontros.append(Encontro("", date.fromisoformat(excecao["data"]),
                                      excecao["inicio"], excecao["fim"], "previsto", [],
                                      "conteudo", "reposicao"))

    anteriores_por_chave = {(encontro.data, encontro.inicio): encontro
                            for encontro in anteriores or []}
    encontros.sort(key=lambda encontro: (encontro.data, encontro.inicio))
    largura = 3 if len(encontros) > 99 else 2
    for indice, encontro in enumerate(encontros, 1):
        anterior = anteriores_por_chave.get((encontro.data, encontro.inicio))
        if anterior and (encontro.data, encontro.inicio) not in cancelados_calendario:
            encontro.status = anterior.status
            encontro.aulas = list(anterior.aulas)
            encontro.funcao = anterior.funcao
        encontro.id = f"E{indice:0{largura}d}"
    return encontros
