from __future__ import annotations

import re
from collections import defaultdict
from datetime import date
from pathlib import Path

from acad.arquivos.caminhos import sem_acento
from acad.calendario.modelo import Calendario, letivo
from acad.cronograma.consulta import _materiais
from acad.encontros.gerar import Encontro
from acad.manifestos.hashes import hash_entrada
from acad.manifestos.manifesto import divergencias
from acad.validacao.achados import Achado


def regra_dia_nao_letivo(encontros: list[Encontro], cal: Calendario) -> list[Achado]:
    return [Achado("encontro-em-dia-nao-letivo", "erro",
                   f"O encontro {encontro.id} está em dia não letivo ({encontro.data:%d/%m}).")
            for encontro in encontros if encontro.status in {"previsto", "realizado"}
            and encontro.origem != "reposicao" and not letivo(cal, encontro.data)]


def regra_prerequisitos(aulas: list[dict], encontros: list[Encontro]) -> list[Achado]:
    primeiras = {}
    for encontro in encontros:
        if encontro.status == "cancelado":
            continue
        for id_aula in encontro.aulas:
            primeiras[id_aula] = min(primeiras.get(id_aula, encontro.data), encontro.data)
    achados = []
    for aula in aulas:
        dia = primeiras.get(aula["id"])
        if dia is None:
            continue
        for requisito in aula.get("prerequisitos", []):
            anterior = primeiras.get(requisito)
            if anterior is None or dia <= anterior:
                achados.append(Achado("aula-antes-de-prerequisito", "erro",
                                       f"{aula['id']} começa antes de {requisito}."))
    return achados


def regra_cobertura(disciplina: dict, aulas: list[dict], avaliacoes: list[dict]) -> list[Achado]:
    objetivos = [item["id"] if isinstance(item, dict) else item
                 for item in disciplina.get("objetivos", [])]
    em_aulas = {id_obj for aula in aulas for id_obj in aula.get("objetivos", [])}
    em_avaliacoes = {id_obj for avaliacao in avaliacoes for id_obj in avaliacao.get("objetivos", [])}
    achados = []
    for objetivo in objetivos:
        if objetivo not in em_aulas:
            achados.append(Achado("objetivo-sem-aula", "aviso", f"O objetivo {objetivo} não está em nenhuma aula."))
        if avaliacoes and objetivo not in em_avaliacoes:
            achados.append(Achado("objetivo-sem-avaliacao", "aviso",
                                   f"O objetivo {objetivo} não está em nenhuma avaliação."))
    return achados


def regra_avaliacao_nao_ministrada(avaliacao: dict, aulas: list[dict],
                                   encontros: list[Encontro]) -> list[Achado]:
    limite = date.fromisoformat(avaliacao["data"])
    ministradas = {aula["id"] for aula in aulas if aula.get("status") == "ministrada"}
    anteriores = {id_aula for encontro in encontros
                  if encontro.status in {"previsto", "realizado"} and encontro.data < limite
                  for id_aula in encontro.aulas}
    return [Achado("avaliacao-sobre-aula-nao-ministrada", "erro",
                   f"A prova {avaliacao['etapa']} cobre {id_aula}, que não terá sido dada até {limite:%d/%m}.")
            for id_aula in avaliacao.get("aulas_cobertas", [])
            if id_aula not in ministradas and id_aula not in anteriores]


def regra_numero_repetido(ws, pasta_aulas: Path) -> list[Achado]:
    if not ws.existe(pasta_aulas):
        return []
    temas = defaultdict(set)
    nomes = defaultdict(list)
    for arquivo in ws.listar(pasta_aulas):
        if arquivo.suffix.lower() != ".pptx":
            continue
        encontrado = re.match(r"^Aula\s+(\d+)\s*[-–]\s*(.+)$", arquivo.stem, re.IGNORECASE)
        if not encontrado:
            continue
        numero = f"Aula {int(encontrado.group(1)):02d}"
        tema = sem_acento(encontrado.group(2))
        tema = re.sub(r"^(slides|roteiro de aula|resumo de aula|guia de estudo|atividades complementares)\s*[-–]\s*", "", tema)
        temas[numero].add(tema)
        nomes[numero].append(arquivo.name)
    return [Achado("numero-aula-repetido", "aviso",
                   f"“{numero}” aparece em slides de temas diferentes: {', '.join(nomes[numero])}.")
            for numero in sorted(temas) if len(temas[numero]) > 1]


def _descricao_entrada(chave: str) -> str:
    if "aulas.yaml#" in chave:
        return "o plano da aula"
    if "modelo" in sem_acento(chave):
        return "o modelo de slides"
    if "programa" in sem_acento(chave):
        return "o programa da disciplina"
    return chave


def regra_manifestos(ws, semestre: Path, disc: Path, aulas: list[dict]) -> list[Achado]:
    achados = []
    itens = {aula["id"]: aula for aula in aulas}
    for aula in aulas:
        manifesto = aula.get("manifesto")
        if not manifesto:
            continue
        for artefato in manifesto.get("artefatos", []):
            if not ws.existe(Path(semestre) / artefato):
                achados.append(Achado("artefato-ausente", "erro",
                                       f"O artefato de {aula['id']} não existe: {artefato}.", artefato))
        mudancas = divergencias(manifesto, lambda chave: hash_entrada(ws, semestre, chave, itens))
        if mudancas:
            descricoes = list(dict.fromkeys(_descricao_entrada(chave) for chave in mudancas))
            achados.append(Achado("manifesto-desatualizado", "aviso",
                                   f"{aula['id']} precisa ser atualizado: mudou {', '.join(descricoes)}."))
    return achados


def regra_slide_divergente(ws, disc: Path, aulas: list[dict], perfil=None) -> list[Achado]:
    if perfil is None:
        from acad import contexto
        perfil = contexto.perfil()
    achados = []
    for aula in aulas:
        numero = re.search(r"\d+", aula["id"])
        if not numero:
            continue
        materiais = _materiais(ws, disc, numero.group().zfill(2), aula.get("tema", ""), perfil)
        if not materiais["slides"] and materiais["slides_divergentes"]:
            achados.append(Achado("slide-numeracao-divergente", "aviso",
                                   f"{aula['id']} tem slides de tema parecido com outra numeração: "
                                   f"{', '.join(materiais['slides_divergentes'])}."))
    return achados
