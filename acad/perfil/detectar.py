from __future__ import annotations

import re
from pathlib import Path

from acad.arquivos.caminhos import relativo_posix
from acad.arquivos.privacidade import Workspace


_PERIODO = {"Primeiro": 1, "Segundo": 2}


def detectar(raiz: Path, perfil) -> dict:
    raiz = Path(raiz).resolve()
    ws = Workspace(raiz, perfil.exclusao)
    semestres = []
    if raiz.name in ("Primeiro Semestre", "Segundo Semestre") and raiz.parent.name.isdigit():
        semestres = [raiz]
        raiz_fasoft = raiz.parent.parent
    else:
        raiz_fasoft = raiz if raiz.name.lower() == "fasoft" else None
        for ano in ws.listar(raiz):
            if ano.is_dir() and re.fullmatch(r"\d{4}", ano.name):
                for pasta in ws.listar(ano):
                    if pasta.is_dir() and pasta.name in ("Primeiro Semestre", "Segundo Semestre"):
                        semestres.append(pasta)
    saida = {"raiz_fasoft": str(raiz_fasoft) if raiz_fasoft else None,
             "semestres": [], "disciplinas": [], "pasta_avaliacoes": None, "pasta_modelos": None}
    for semestre in semestres:
        saida["semestres"].append({"pasta": relativo_posix(semestre, raiz_fasoft) if raiz_fasoft else str(semestre),
                                    "ano": int(semestre.parent.name), "periodo": _PERIODO[semestre.name.split()[0]]})
        ws_sem = Workspace(semestre, perfil.exclusao)
        for pasta in ws_sem.listar(semestre):
            if not pasta.is_dir():
                continue
            if perfil.pasta_avaliacoes.match(pasta.name):
                saida["pasta_avaliacoes"] = pasta.name
            elif perfil.pasta_modelos.match(pasta.name):
                saida["pasta_modelos"] = pasta.name
            else:
                match = perfil.disciplina_pasta.match(pasta.name)
                if not match or not (pasta / perfil.subpastas_disciplina[0]).is_dir():
                    continue
                planejamento = pasta / "01 - Planejamento"
                tem_cronograma = any(item.name.startswith("Cronograma") and item.suffix.lower() == ".xlsx"
                                    for item in ws_sem.listar(planejamento))
                saida["disciplinas"].append({
                    "pasta": relativo_posix(pasta, semestre), "numero": match["num"],
                    "nome": match["nome"], "periodo": match["periodo"],
                    "tem_cronograma": tem_cronograma,
                    "subpastas_faltando": [nome for nome in perfil.subpastas_disciplina
                                           if not (pasta / nome).is_dir()],
                })
    return saida
