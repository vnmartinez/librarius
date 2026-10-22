from __future__ import annotations

import hashlib
from datetime import date, datetime, timedelta

from icalendar import Calendar

from acad.arquivos.caminhos import sem_acento
from acad.calendario.modelo import Calendario, DiaEspecial, Evento


def _data(valor) -> date:
    return valor.date() if isinstance(valor, datetime) else valor


def importar_ics(conteudo: bytes, semestre: str, inicio: date, fim: date) -> Calendario:
    dias = []
    eventos = []
    calendario = Calendar.from_ical(conteudo)
    for componente in calendario.walk("VEVENT"):
        primeira = _data(componente.decoded("DTSTART"))
        ultima_exclusiva = _data(componente.decoded("DTEND", default=primeira + timedelta(days=1)))
        ultima = max(primeira, ultima_exclusiva - timedelta(days=1))
        descricao = str(componente.get("SUMMARY", ""))
        nome = sem_acento(descricao)
        if "feriado" in nome:
            tipo = "feriado"
        elif "recesso" in nome:
            tipo = "recesso"
        elif "sabado letivo" in nome:
            tipo = "sabado-letivo"
        else:
            tipo = "outro"
        if tipo in ("feriado", "recesso"):
            atual = primeira
            while atual <= ultima:
                dias.append(DiaEspecial(atual, tipo, descricao))
                atual += timedelta(days=1)
        elif primeira < ultima:
            eventos.append(Evento(primeira, ultima,
                                  "semana-academica" if "semana" in nome else "outro", descricao))
        else:
            dias.append(DiaEspecial(primeira, tipo, descricao))
    return Calendario(
        semestre, inicio, fim, "rascunho", dias, eventos,
        {"tipo": "ics", "sha256": "sha256:" + hashlib.sha256(conteudo).hexdigest()},
    )
