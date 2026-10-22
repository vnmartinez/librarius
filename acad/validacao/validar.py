from __future__ import annotations

from pathlib import Path

import yaml

from acad import esquemas, mensagens
from acad.arquivos.caminhos import relativo_posix
from acad.calendario.modelo import de_documento
from acad.encontros.carga import verificar_carga
from acad.erros import ErroAcad
from acad.planejamento.arquivos import ler_encontros
from acad.validacao.achados import Achado
from acad.validacao.estrutura import validar_estrutura
from acad.validacao.nomenclatura import disciplinas, validar_nomes
from acad.validacao import regras


def validar_semestre(ws, semestre: Path, perfil, disciplina: Path | None = None) -> list[Achado]:
    semestre = Path(semestre)
    achados = validar_nomes(ws, semestre, perfil) + validar_estrutura(ws, semestre, perfil)
    if disciplina is not None:
        prefixo = relativo_posix(disciplina, semestre) + "/"
        achados = [a for a in achados if not a.caminho or a.caminho.startswith(prefixo)
                   or a.caminho == prefixo[:-1]]

    def documento(arquivo: Path, esquema: str):
        if not ws.existe(arquivo):
            return None
        try:
            dados = esquemas.carregar_yaml(ws.ler_texto(arquivo))
            esquemas.validar_ou_falhar(esquema, dados)
            return dados
        except (ErroAcad, yaml.YAMLError, UnicodeError, TypeError, ValueError) as erro:
            achados.append(Achado("esquema-invalido", "erro",
                                   f"{arquivo.name} está inválido: {erro}.",
                                   relativo_posix(arquivo, semestre)))
            return None

    calendario = None
    administracao = next((p for p in ws.listar(semestre)
                          if p.is_dir() and p.name.startswith("00 - ")), None)
    if administracao:
        dados_cal = documento(administracao / "calendario.yaml", "calendario")
        if dados_cal:
            calendario = de_documento(dados_cal)
    if calendario is None:
        achados.append(Achado("calendario-nao-cadastrado", "info",
                               "O calendário ainda não está cadastrado; pulei as regras de dias letivos."))

    for disc in ([disciplina] if disciplina is not None else disciplinas(ws, semestre, perfil)):
        planejamento = disc / "01 - Planejamento"
        documento_disc = documento(planejamento / "disciplina.yaml", "disciplina")
        documento_aulas = documento(planejamento / "aulas.yaml", "aula")
        aulas = (documento_aulas or {}).get("aulas", [])
        avaliacoes = []
        pasta_avaliacoes = planejamento / "avaliacoes"
        if ws.existe(pasta_avaliacoes):
            for arquivo in ws.listar(pasta_avaliacoes):
                if arquivo.suffix.lower() == ".yaml":
                    item = documento(arquivo, "avaliacao")
                    if item:
                        avaliacoes.append(item["avaliacao"])
        encontros = []
        for arquivo in ws.listar(planejamento):
            if arquivo.suffix.lower() != ".yaml":
                continue
            if arquivo.name.startswith("turma-"):
                documento(arquivo, "turma")
            elif arquivo.name.startswith("encontros-"):
                if documento(arquivo, "encontro"):
                    id_turma = arquivo.stem.removeprefix("encontros-")
                    encontros.extend(ler_encontros(ws, disc, id_turma))
        if documento_disc:
            dados_disc = documento_disc["disciplina"]
            achados += regras.regra_cobertura(dados_disc, aulas, avaliacoes)
            if encontros and dados_disc.get("carga_horaria"):
                achados += verificar_carga(encontros, dados_disc["carga_horaria"])
        if calendario:
            achados += regras.regra_dia_nao_letivo(encontros, calendario)
        achados += regras.regra_prerequisitos(aulas, encontros)
        for avaliacao in avaliacoes:
            achados += regras.regra_avaliacao_nao_ministrada(avaliacao, aulas, encontros)
        achados += regras.regra_manifestos(ws, semestre, disc, aulas)
        achados += regras.regra_numero_repetido(ws, disc / "02 - Aulas")
        achados += regras.regra_slide_divergente(ws, disc, aulas)
    prioridade = {"erro": 0, "aviso": 1, "info": 2}
    return sorted(achados, key=lambda a: (prioridade[a.nivel], a.caminho, a.codigo))


def resumo_validacao(achados: list[Achado], protegidas: int) -> str:
    erros = sum(a.nivel == "erro" for a in achados)
    avisos = sum(a.nivel == "aviso" for a in achados)
    linhas = [f"Encontrei {erros} problemas e {avisos} avisos."]
    linhas += [f"{a.mensagem}" for a in achados[:10]]
    if protegidas:
        linhas.append(mensagens.msg("pastas-protegidas", n=protegidas))
    return "\n".join(linhas)
