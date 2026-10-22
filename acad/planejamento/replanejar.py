from __future__ import annotations

from collections import defaultdict
from dataclasses import replace
from datetime import date

from acad.encontros.gerar import Encontro
from acad.erros import ErroAcad


def cancelar(encontros: list[Encontro], d: date, motivo: str) -> list[Encontro]:
    encontrados = False
    saida = []
    for encontro in encontros:
        if encontro.data == d:
            encontrados = True
            saida.append(replace(encontro, status="cancelado", motivo=motivo, aulas=[]))
        else:
            saida.append(replace(encontro, aulas=list(encontro.aulas)))
    if not encontrados:
        raise ErroAcad("sem-encontro-na-data", f"Não há aula dessa turma em {d:%d/%m}.")
    return saida


def _mapa(encontros: list[Encontro]) -> dict[str, list[str]]:
    datas = defaultdict(list)
    for encontro in encontros:
        if encontro.status == "cancelado":
            continue
        for id_aula in encontro.aulas:
            datas[id_aula].append(encontro.data.isoformat())
    return dict(datas)


def diff(antes: list[Encontro], depois: list[Encontro], avaliacoes: list[dict]) -> dict:
    anterior, posterior = _mapa(antes), _mapa(depois)
    deslocadas = []
    comprimidas = []
    sem_encontro = []
    for id_aula, datas in anterior.items():
        novas = posterior.get(id_aula, [])
        if not novas:
            sem_encontro.append(id_aula)
        elif datas != novas:
            deslocadas.append({"aula": id_aula, "de": datas, "para": novas})
        if len(novas) < len(datas):
            comprimidas.append(id_aula)
    afetadas = []
    for avaliacao in avaliacoes:
        data_prova = date.fromisoformat(avaliacao["data"])
        aulas = [id_aula for id_aula in avaliacao.get("aulas_cobertas", [])
                 if id_aula not in posterior or date.fromisoformat(posterior[id_aula][-1]) > data_prova]
        if aulas:
            afetadas.append({"etapa": avaliacao["etapa"], "data": avaliacao["data"], "aulas": aulas})
    return {"deslocadas": deslocadas, "comprimidas": comprimidas,
            "sem_encontro": sem_encontro, "avaliacoes_afetadas": afetadas}


def resumo_diff(d: dict) -> str:
    partes = []
    deslocadas = d["deslocadas"]
    if deslocadas:
        mudancas = []
        for item in deslocadas:
            origem = " e ".join(date.fromisoformat(valor).strftime("%d/%m") for valor in item["de"])
            destino = " e ".join(date.fromisoformat(valor).strftime("%d/%m") for valor in item["para"])
            mudancas.append(f"{item['aula']} sai de {origem} para {destino}")
        partes.append(f"{len(deslocadas)} aulas mudam de dia: " + "; ".join(mudancas) + ".")
    if d["comprimidas"]:
        partes.append("Aulas com menos encontros: " + ", ".join(d["comprimidas"]) + ".")
    if d["sem_encontro"]:
        partes.append("Aulas sem encontro: " + ", ".join(d["sem_encontro"]) + ".")
    for item in d["avaliacoes_afetadas"]:
        data_prova = date.fromisoformat(item["data"]).strftime("%d/%m")
        partes.append(f"A avaliação {item['etapa']} de {data_prova} passaria a cobrir "
                      f"{', '.join(item['aulas'])}, que ainda não teria sido dada.")
    return " ".join(partes) or "Nenhuma aula muda de dia."
