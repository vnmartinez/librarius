from __future__ import annotations

from datetime import datetime, time
from zoneinfo import ZoneInfo

from icalendar import Calendar, Event

from acad.encontros.gerar import Encontro
from acad.geracao.nomes import slug


def exportar_ics(encontros: list[Encontro], disciplina_nome: str, turma: str,
                 fuso: str, aulas: dict[str, str]) -> bytes:
    calendario = Calendar()
    calendario.add("prodid", "-//Librarius//acad//PT")
    calendario.add("version", "2.0")
    zona = ZoneInfo(fuso)
    for encontro in encontros:
        if encontro.status == "cancelado":
            continue
        evento = Event()
        evento.add("uid", f"{slug(disciplina_nome)}-{turma}-{encontro.data.isoformat()}-{encontro.inicio.replace(':', '')}@librarius")
        if encontro.funcao == "avaliacao":
            descricao = "Avaliação"
        elif encontro.aulas:
            descricao = "; ".join(f"{id_aula}: {aulas.get(id_aula, '')}".rstrip(": ")
                                  for id_aula in encontro.aulas)
        else:
            descricao = "Encontro"
        evento.add("summary", f"{disciplina_nome} ({turma}) — {descricao}")
        evento.add("dtstart", datetime.combine(encontro.data, time.fromisoformat(encontro.inicio), zona))
        evento.add("dtend", datetime.combine(encontro.data, time.fromisoformat(encontro.fim), zona))
        calendario.add_component(evento)
    return calendario.to_ical()
