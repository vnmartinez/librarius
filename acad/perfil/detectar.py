from __future__ import annotations

from pathlib import Path

from acad.arquivos.caminhos import relativo_posix
from acad.arquivos.privacidade import Workspace


def _semestres(raiz: Path, perfil) -> list[Path]:
    if perfil.semestre_de(raiz) is not None:
        return [raiz]
    achados = []
    ws = Workspace(raiz, perfil.exclusao)
    for filho in ws.listar(raiz):
        if not filho.is_dir():
            continue
        if perfil.semestre_de(filho) is not None:
            achados.append(filho)
        else:
            achados += [neto for neto in ws.listar(filho)
                        if neto.is_dir() and perfil.semestre_de(neto) is not None]
    return sorted(achados)


def detectar(raiz: Path, perfil) -> dict:
    raiz = Path(raiz).resolve()
    semestres = _semestres(raiz, perfil)
    base = perfil.base_semestre(semestres[0]) if semestres else None
    saida = {"raiz": str(base) if base else None, "raiz_fasoft": str(base) if base else None,
             "semestres": [], "disciplinas": [], "pasta_avaliacoes": None, "pasta_modelos": None}
    for semestre in semestres:
        ano, periodo = perfil.semestre_de(semestre)
        saida["semestres"].append({"pasta": relativo_posix(semestre, base), "ano": ano, "periodo": periodo})
        ws_sem = Workspace(semestre, perfil.exclusao)
        for pasta in ws_sem.listar(semestre):
            if not pasta.is_dir():
                continue
            if perfil.pasta_avaliacoes.match(pasta.name):
                saida["pasta_avaliacoes"] = pasta.name
            elif perfil.pasta_modelos.match(pasta.name):
                saida["pasta_modelos"] = pasta.name
            elif perfil.re_administracao.match(pasta.name):
                continue
            else:
                partes = perfil.partes_disciplina(pasta.name)
                planejamento = pasta / perfil.pasta("planejamento")
                if not partes or not planejamento.is_dir():
                    continue
                tem_cronograma = any(item.name.startswith("Cronograma") and item.suffix.lower() == ".xlsx"
                                     for item in ws_sem.listar(planejamento))
                saida["disciplinas"].append({
                    "pasta": relativo_posix(pasta, semestre), "numero": partes["num"],
                    "nome": partes["nome"], "periodo": partes["periodo"], "tem_cronograma": tem_cronograma,
                    "subpastas_faltando": [nome for nome in perfil.subpastas_disciplina
                                           if not (pasta / nome).is_dir()],
                })
    return saida
