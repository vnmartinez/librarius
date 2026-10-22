"""Monta o perfil da instituicao pela organizacao da pasta do semestre."""
from __future__ import annotations

import copy
import re
from pathlib import Path

from acad.arquivos.caminhos import sem_acento
from acad.arquivos.privacidade import Workspace
from acad.erros import ErroAcad
from acad.geracao.identidade import paleta_de_cor
from acad.perfil.padroes import ESTRUTURA_V1
from acad.perfil.perfil import ler_documento_perfil

FORMAS_SEMESTRE = [
    (ESTRUTURA_V1["semestre"], ESTRUTURA_V1["periodos"]),
    (r"^(?P<ano>\d{4})/(?P<periodo>[12])(?:º|o)?(?: [Ss]emestre)?$", None),
    (r"^(?P<ano>\d{4})[-._ ](?P<periodo>[12])$", None),
]
PAPEIS = [("planejamento", r"planej"), ("aulas", r"aula"), ("atividades", r"ativ|lista|exerc"),
          ("projetos", r"proj|entreg|trabalho"), ("referencias", r"refer|biblio|material"),
          ("codigo", r"codig|exemplo|fonte"), ("arquivo", r"arquivo|antig|morto")]
COM_NUMERO = r"^(?P<num>\d{2}) - (?P<nome>.+?)(?: - (?P<periodo>.+ Período))?$"


def _semestre(semestre: Path):
    for padrao, periodos in FORMAS_SEMESTRE:
        alvo = f"{semestre.parent.name}/{semestre.name}" if "/" in padrao else semestre.name
        correspondencia = re.fullmatch(padrao, alvo)
        if correspondencia:
            texto = correspondencia["periodo"]
            return padrao, periodos, int(correspondencia["ano"]), (periodos[texto] if periodos else int(texto))
    raise ErroAcad("semestre-nao-reconhecido",
                   "Não reconheci o ano e o período pelo nome da pasta do semestre. "
                   "Renomeie para algo como 2027-1 ou me diga qual é.", semestre.name, saida=4)


def inferir_perfil(semestre: Path, id: str, instituicao: str, cor: str | None = None,
                   rodape: list[str] | None = None, local: str | None = None) -> tuple[dict, dict]:
    semestre = Path(semestre).resolve()
    documento = copy.deepcopy(ler_documento_perfil("neutro"))
    perfil = documento["perfil"]
    padrao, periodos, ano, periodo = _semestre(semestre)
    ws = Workspace(semestre, perfil["exclusao"])
    especiais = [re.compile(perfil[chave]) for chave in ("pasta_avaliacoes", "pasta_modelos")]
    especiais.append(re.compile(perfil["estrutura"]["administracao"]))
    pastas = [p for p in ws.listar(semestre) if p.is_dir() and not p.name.startswith((".", "~", "_"))]
    disciplinas = {}
    for pasta in pastas:
        if any(regra.match(pasta.name) for regra in especiais):
            continue
        subpastas = [s.name for s in ws.listar(pasta) if s.is_dir()] + [
            Path(p).name for p in ws.protegidas if Path(p).parent.name == pasta.name]
        if len(set(subpastas)) >= 2:
            disciplinas[pasta.name] = sorted(set(subpastas))
    if not disciplinas:
        raise ErroAcad("disciplinas-nao-encontradas",
                       "Não encontrei pastas de disciplina nesse semestre.", str(semestre), saida=4)
    contagem = {}
    for nomes in disciplinas.values():
        for nome in nomes:
            contagem[nome] = contagem.get(nome, 0) + 1
    subpastas = sorted(nome for nome, vezes in contagem.items() if vezes * 2 >= len(disciplinas))
    papeis, criados = {}, []
    for papel, regra in PAPEIS:
        achado = next((nome for nome in subpastas if nome not in papeis.values()
                       and re.search(regra, sem_acento(nome).lower())), None)
        if achado is None:
            achado = papel
            criados.append(papel)
            subpastas.append(papel)
        papeis[papel] = achado
    numeradas = all(re.match(r"^\d{2} - ", nome) for nome in disciplinas)
    perfil.update({"id": id, "instituicao": instituicao, "subpastas_disciplina": subpastas,
                   "pasta_arquivo": papeis["arquivo"]})
    if numeradas:
        perfil["disciplina_pasta"] = COM_NUMERO
        perfil["nomenclatura"]["pasta"] = r"^\d{2} - "
    perfil["estrutura"] = {"semestre": padrao, "administracao": perfil["estrutura"]["administracao"],
                           "papeis": papeis, **({"periodos": periodos} if periodos else {})}
    projetos = f"*/{papeis['projetos']}"
    if projetos not in perfil["exclusao"]:
        perfil["exclusao"].append(projetos)
    modelos = _modelos(ws, semestre, re.compile(perfil["pasta_modelos"]))
    if modelos:
        perfil["modelos"] = modelos
    slides = {}
    if cor:
        slides["paleta"] = paleta_de_cor(cor)
    if rodape is not None or local is not None:
        slides["capa"] = {**({"linhas": list(rodape)} if rodape is not None else {}),
                          **({"local": local} if local is not None else {})}
    if slides:
        perfil["slides"] = slides
    resumo = {"ano": ano, "periodo": periodo, "disciplinas": sorted(disciplinas), "papeis_criados": criados}
    return documento, resumo


def _modelos(ws: Workspace, semestre: Path, regra) -> dict:
    pasta = next((p for p in ws.listar(semestre) if p.is_dir() and regra.match(p.name)), None)
    if pasta is None:
        return {}
    modelos = {}
    filhos = [p for p in ws.listar(pasta) if p.is_dir()]
    slides = next((p for p in filhos if "slide" in sem_acento(p.name).lower()), None)
    if slides:
        modelos["slides"] = slides.name
    for candidato in [pasta, *filhos]:
        tex = next((a for a in ws.listar(candidato)
                    if a.is_file() and a.suffix == ".tex" and "prova" in a.name.lower()), None)
        if tex:
            modelos["prova"] = tex.relative_to(pasta).as_posix()
            break
    return modelos
