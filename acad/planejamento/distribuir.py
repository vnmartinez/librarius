from __future__ import annotations

from dataclasses import replace
from heapq import heappop, heappush

from acad.encontros.gerar import Encontro
from acad.erros import ErroAcad


def ordenar_por_prerequisitos(aulas: list[dict]) -> list[dict]:
    por_id = {aula["id"]: aula for aula in aulas}
    posicoes = {aula["id"]: indice for indice, aula in enumerate(aulas)}
    pendencias = {id_aula: 0 for id_aula in por_id}
    sucessoras = {id_aula: [] for id_aula in por_id}
    for aula in aulas:
        for requisito in aula.get("prerequisitos", []):
            if requisito not in por_id:
                raise ErroAcad("prerequisito-desconhecido", f"A aula {aula['id']} depende de {requisito}, que não existe.")
            pendencias[aula["id"]] += 1
            sucessoras[requisito].append(aula["id"])
    disponiveis = []
    for id_aula, grau in pendencias.items():
        if grau == 0:
            heappush(disponiveis, (posicoes[id_aula], id_aula))
    ordenadas = []
    while disponiveis:
        _, id_aula = heappop(disponiveis)
        ordenadas.append(por_id[id_aula])
        for sucessora in sucessoras[id_aula]:
            pendencias[sucessora] -= 1
            if pendencias[sucessora] == 0:
                heappush(disponiveis, (posicoes[sucessora], sucessora))
    if len(ordenadas) != len(aulas):
        presas = [id_aula for id_aula, grau in pendencias.items() if grau]
        raise ErroAcad("prerequisitos-em-ciclo", "Duas aulas dependem uma da outra: " + ", ".join(presas))
    return ordenadas


def distribuir(aulas: list[dict], encontros: list[Encontro]) -> tuple[list[Encontro], list[str]]:
    saida = [replace(encontro, aulas=list(encontro.aulas)) for encontro in encontros]
    disponiveis = []
    for encontro in saida:
        if encontro.status == "previsto" and encontro.funcao == "conteudo":
            encontro.aulas = []
            disponiveis.append(encontro)
    ministradas = {aula["id"] for aula in aulas if aula.get("status") == "ministrada"}
    ocupadas = {id_aula for encontro in saida if encontro.status == "realizado" for id_aula in encontro.aulas}
    cursor = 0
    sobra = []
    for aula in ordenar_por_prerequisitos(aulas):
        id_aula = aula["id"]
        if id_aula in ministradas or id_aula in ocupadas:
            continue
        quantidade = aula.get("encontros_necessarios", 1)
        if cursor + quantidade > len(disponiveis):
            sobra.append(id_aula)
            continue
        for encontro in disponiveis[cursor:cursor + quantidade]:
            encontro.aulas = [id_aula]
        cursor += quantidade
    return saida, sobra
