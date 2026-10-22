from __future__ import annotations

import re
from pathlib import Path

from acad.arquivos.caminhos import nfc, relativo_posix
from acad.validacao.achados import Achado
from acad.validacao.nomenclatura import disciplinas

_BLOCO = re.compile(r"```(?:text)?\r?\n(.*?)```", re.S)
_ITEM = re.compile(r"^[├└]── (.+?)/\s*$")


def pastas_do_readme(texto: str) -> list[str]:
    inicio = texto.find("Estrutura principal")
    bloco = _BLOCO.search(texto, inicio if inicio >= 0 else 0)
    if not bloco:
        return []
    return [nfc(resultado[1]) for linha in bloco.group(1).splitlines()
            if (resultado := _ITEM.match(linha.strip()))]


def validar_estrutura(ws, semestre: Path, perfil) -> list[Achado]:
    achados: list[Achado] = []
    readme = semestre / "README.md"
    reais = {caminho.name for caminho in ws.listar(semestre) if caminho.is_dir()}
    reais.update(protegida.split("/")[0] for protegida in ws.protegidas)
    if ws.existe(readme):
        citadas = set(pastas_do_readme(ws.ler_texto(readme)))
        faltam, sobram = sorted(reais - citadas), sorted(citadas - reais)
        if faltam or sobram:
            partes = []
            if faltam:
                partes.append("existem mas não estão no guia: " + ", ".join(faltam))
            if sobram:
                partes.append("estão no guia mas não existem: " + ", ".join(sobram))
            achados.append(Achado(
                "readme-desatualizado", "aviso",
                "O guia de pastas do semestre está desatualizado — " + "; ".join(partes) + ".",
                "README.md",
            ))
    for disciplina in disciplinas(ws, semestre, perfil):
        ws.listar(disciplina)
        for subpasta in perfil.subpastas_disciplina:
            relativo = relativo_posix(disciplina / subpasta, semestre)
            if not ws.existe(disciplina / subpasta) and relativo not in ws.protegidas:
                achados.append(Achado(
                    "subpasta-padrao-ausente", "aviso",
                    f"A disciplina “{disciplina.name}” não tem a pasta “{subpasta}”.",
                    relativo_posix(disciplina, semestre),
                ))
    return achados
