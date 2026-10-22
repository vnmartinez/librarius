from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime

from acad import esquemas
from acad.erros import ErroAcad


@dataclass
class DiaEspecial:
    data: date
    tipo: str
    descricao: str = ""
    equivale_a: int | None = None


@dataclass
class Evento:
    inicio: date
    fim: date
    tipo: str
    descricao: str = ""


@dataclass
class Calendario:
    semestre: str
    inicio: date
    fim: date
    status: str
    dias: list[DiaEspecial]
    eventos: list[Evento]
    fonte: dict
    confirmado_em: str | None = None


def de_documento(documento: dict, validar: bool = True) -> Calendario:
    if validar:
        esquemas.validar_ou_falhar("calendario", documento)
    dados = documento["calendario"]
    return Calendario(
        semestre=dados["semestre"], inicio=date.fromisoformat(dados["inicio"]),
        fim=date.fromisoformat(dados["fim"]), status=dados["status"],
        dias=[DiaEspecial(date.fromisoformat(item["data"]), item["tipo"],
                          item.get("descricao", ""), item.get("equivale_a")) for item in dados["dias"]],
        eventos=[Evento(date.fromisoformat(item["inicio"]), date.fromisoformat(item["fim"]),
                        item["tipo"], item.get("descricao", "")) for item in dados["eventos"]],
        fonte=dados["fonte"], confirmado_em=dados.get("confirmado_em"),
    )


def para_documento(calendario: Calendario) -> dict:
    dias = []
    for item in calendario.dias:
        registro = {"data": item.data.isoformat(), "tipo": item.tipo}
        if item.descricao:
            registro["descricao"] = item.descricao
        if item.equivale_a is not None:
            registro["equivale_a"] = item.equivale_a
        dias.append(registro)
    eventos = []
    for item in calendario.eventos:
        registro = {"inicio": item.inicio.isoformat(), "fim": item.fim.isoformat(), "tipo": item.tipo}
        if item.descricao:
            registro["descricao"] = item.descricao
        eventos.append(registro)
    return {"versao_esquema": 1, "calendario": {
        "semestre": calendario.semestre,
        "inicio": calendario.inicio.isoformat(), "fim": calendario.fim.isoformat(),
        "fonte": calendario.fonte, "status": calendario.status,
        "confirmado_em": calendario.confirmado_em,
        "dias": dias, "eventos": eventos,
    }}


def dia(calendario: Calendario, data: date) -> DiaEspecial | None:
    return next((item for item in calendario.dias if item.data == data), None)


def letivo(calendario: Calendario, data: date) -> bool:
    if not calendario.inicio <= data <= calendario.fim:
        return False
    especial = dia(calendario, data)
    if especial and especial.tipo in ("feriado", "recesso"):
        return False
    if especial and especial.tipo == "sabado-letivo":
        return True
    return data.isoweekday() <= 5


def dia_semana_efetivo(calendario: Calendario, data: date) -> int:
    especial = dia(calendario, data)
    if especial and especial.tipo in ("sabado-letivo", "troca-de-dia") and especial.equivale_a:
        return especial.equivale_a
    return data.isoweekday()


def confirmar(calendario: Calendario, agora: datetime) -> Calendario:
    if calendario.status != "rascunho":
        raise ErroAcad("calendario-incompleto", "Esse calendário já está confirmado.")
    for especial in calendario.dias:
        if especial.tipo in ("sabado-letivo", "troca-de-dia") and especial.equivale_a is None:
            raise ErroAcad(
                "calendario-incompleto",
                f"Falta dizer qual dia da semana o sábado letivo de {especial.data:%d/%m} substitui.",
            )
    return replace(calendario, status="confirmado", confirmado_em=agora.isoformat())
