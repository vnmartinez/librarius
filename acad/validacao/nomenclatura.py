from __future__ import annotations

from pathlib import Path

from acad.arquivos.caminhos import relativo_posix
from acad.arquivos.privacidade import Workspace
from acad.perfil.perfil import Perfil
from acad.validacao.achados import Achado


def disciplinas(ws: Workspace, semestre: Path, perfil: Perfil) -> list[Path]:
    return [
        caminho for caminho in ws.listar(semestre)
        if caminho.is_dir()
        and perfil.disciplina_pasta.match(caminho.name)
        and not perfil.pasta_avaliacoes.match(caminho.name)
        and not perfil.pasta_modelos.match(caminho.name)
        and ws.existe(caminho / perfil.pasta("planejamento"))
    ]


def _no_arquivo_morto(relativo: str, perfil: Perfil) -> bool:
    return f"/{perfil.pasta_arquivo}/" in f"/{relativo}/"


def validar_nomes(ws: Workspace, semestre: Path, perfil: Perfil) -> list[Achado]:
    achados: list[Achado] = []

    def rel(caminho: Path) -> str:
        return relativo_posix(caminho, semestre)

    topo = ws.listar(semestre)
    nomes = {caminho.name for caminho in topo if caminho.is_dir()}
    nomes.update(protegida.split("/")[0] for protegida in ws.protegidas)
    for nome in sorted(nomes):
        if not perfil.re_pasta.match(nome):
            achados.append(Achado("pasta-sem-prefixo", "erro",
                                  f"A pasta “{nome}” não começa com número e traço (ex.: “11 - …”).", nome))

    for disciplina in disciplinas(ws, semestre, perfil):
        for subpasta in ws.listar(disciplina):
            if subpasta.is_dir() and not perfil.re_pasta.match(subpasta.name):
                achados.append(Achado("pasta-sem-prefixo", "erro",
                                      f"A pasta “{subpasta.name}” não começa com número e traço.", rel(subpasta)))
        aulas = disciplina / perfil.pasta("aulas")
        listas = disciplina / perfil.pasta("atividades")
        if ws.existe(aulas):
            for caminho in ws.listar(aulas):
                if caminho.is_dir() and not perfil.re_pasta.match(caminho.name):
                    achados.append(Achado("pasta-sem-prefixo", "erro",
                                          f"A pasta “{caminho.name}” dentro das aulas não começa com número e traço.", rel(caminho)))
                elif caminho.is_file() and not perfil.re_aula.match(caminho.name):
                    achados.append(Achado("nome-aula-sem-prefixo", "erro",
                                          f"O arquivo “{caminho.name}” não começa com “Aula XX - ”.", rel(caminho)))
        if ws.existe(listas):
            for caminho in ws.listar(listas):
                if caminho.is_file() and not perfil.re_lista.match(caminho.name):
                    achados.append(Achado("nome-lista-sem-prefixo", "erro",
                                          f"O arquivo “{caminho.name}” não começa com “Lista XX - ” ou “Atividade XX - ”.", rel(caminho)))

    for caminho in ws.percorrer(semestre):
        relativo = rel(caminho)
        if (caminho.is_file() and not _no_arquivo_morto(relativo, perfil)
                and any(regra.search(caminho.name) for regra in perfil.sufixos_proibidos)):
            achados.append(Achado(
                "sufixo-proibido", "erro",
                f"“{caminho.name}” parece uma cópia ou versão antiga. O certo é ficar só o arquivo oficial, "
                f"e a versão antiga ir para “{perfil.pasta_arquivo}”.", relativo,
            ))
    return achados
