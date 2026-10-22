from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Iterable

from acad.arquivos.caminhos import sem_acento
from acad.arquivos.privacidade import Workspace
from acad.cronograma.classificar import tipo_linha
from acad.cronograma.planilha import linhas_na_data

STOPWORDS = {
    "para", "como", "sobre", "pela", "pelo", "com", "sem", "das", "dos",
    "uma", "este", "esta", "aula", "parte", "secao", "secoes",
}
EXT_SLIDE = (".pptx", ".ppt", ".pdf", ".key", ".odp")
EXT_DOC = (".md", ".docx", ".doc", ".txt")
DIAS = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]


def encontrar_raiz(inicio: Path) -> Path | None:
    atual = Path(inicio).resolve()
    while True:
        arquivo = atual / "AGENTS.md"
        if arquivo.exists():
            try:
                if "Fasoft" in arquivo.read_text(encoding="utf-8"):
                    return atual
            except OSError:
                pass
        if atual.name.lower() == "fasoft" and ((atual / ".agents").exists() or (atual / "2026").exists()):
            return atual
        if atual.parent == atual:
            return None
        atual = atual.parent


def palavras_chave(texto: str) -> list[str]:
    return [palavra for palavra in re.findall(r"\b[a-z]{4,}\b", sem_acento(texto or ""))
            if palavra not in STOPWORDS]


def _materiais(ws: Workspace, disciplina: Path, numero: str | None, topico: str) -> dict:
    materiais = {chave: [] for chave in (
        "slides", "slides_divergentes", "roteiros_resumos", "atividades",
        "atividades_relacionadas", "codigos",
    )}
    palavras = palavras_chave(topico)

    def combina(nome: str) -> bool:
        return sum(1 for palavra in palavras if palavra in sem_acento(nome)) >= 2

    aulas = disciplina / "02 - Aulas"
    if ws.existe(aulas):
        for arquivo in ws.listar(aulas):
            nome = arquivo.name
            baixo = nome.lower()
            if numero and f"Aula {numero}" in nome:
                if baixo.endswith(EXT_SLIDE):
                    materiais["slides"].append(nome)
                elif baixo.endswith(EXT_DOC):
                    materiais["roteiros_resumos"].append(nome)
            elif baixo.endswith(EXT_SLIDE) and combina(nome):
                materiais["slides_divergentes"].append(nome)

    atividades = disciplina / "03 - Atividades e Listas"
    if ws.existe(atividades):
        for arquivo in ws.listar(atividades):
            if numero and f"Aula {numero}" in arquivo.name:
                materiais["atividades"].append(arquivo.name)
            elif combina(arquivo.name):
                materiais["atividades_relacionadas"].append(arquivo.name)

    codigos = disciplina / "06 - Código e Exemplos"
    if ws.existe(codigos):
        materiais["codigos"] = [arquivo.name for arquivo in ws.listar(codigos)
                                if numero and f"aula-{numero}" in arquivo.name.lower()]
    return materiais


def _cronogramas(ws: Workspace, pasta: Path):
    for caminho in ws.listar(pasta):
        if caminho.is_dir():
            if not caminho.name.startswith(".") and caminho.name != "99 - Arquivo":
                yield from _cronogramas(ws, caminho)
        elif "Cronograma" in caminho.name and caminho.name.endswith(".xlsx"):
            yield caminho


def consultar(raiz: Path, alvo: date, exclusao: Iterable[str]) -> dict:
    raiz = Path(raiz).resolve()
    ws = Workspace(raiz, exclusao)
    aulas = []
    for cronograma in _cronogramas(ws, raiz):
        disciplina = cronograma.parent.parent
        for linha in linhas_na_data(ws.ler_bytes(cronograma), alvo):
            aulas.append({
                "disciplina": disciplina.name,
                "disciplina_dir": str(disciplina),
                "cronograma_path": str(cronograma),
                "semana": linha.semana,
                "aula": linha.aula,
                "aula_num": linha.aula_num,
                "topico": linha.topico,
                "linha": linha.linha,
                "materiais": _materiais(ws, disciplina, linha.aula_num, linha.topico),
                "tipo": tipo_linha(linha.aula, linha.topico),
            })
    return {"projeto": str(raiz), "data": alvo.isoformat(),
            "quantidade_aulas": len(aulas), "aulas": aulas}


def resumo_texto(resultado: dict) -> str:
    data = date.fromisoformat(resultado["data"])
    cabecalho = f"{DIAS[data.weekday()]}, {data:%d/%m/%Y} — "
    if not resultado["aulas"]:
        return cabecalho + "nenhuma aula marcada nos cronogramas."
    linhas = [cabecalho + f"{len(resultado['aulas'])} disciplina(s) com aula."]
    for aula in resultado["aulas"]:
        nome = re.sub(r"^\d{2} - ", "", aula["disciplina"])
        linhas.append(f"\n{nome} — {aula['aula']}: {aula['topico']}")
        if aula["tipo"] == "sem-aula":
            linhas.append("  Sem aula regular (feriado, recesso ou evento).")
            continue
        if aula["tipo"] == "avaliacao":
            linhas.append("  Dia de avaliação.")
            continue
        materiais = aula["materiais"]
        if materiais["slides"]:
            linhas.append("  Slides: prontos — " + "; ".join(materiais["slides"]))
        elif materiais["slides_divergentes"]:
            linhas.append("  Slides: achei com outro número — " + "; ".join(materiais["slides_divergentes"]))
        else:
            linhas.append("  Slides: ainda não existem.")
        if materiais["roteiros_resumos"]:
            linhas.append("  Roteiro ou resumo: " + "; ".join(materiais["roteiros_resumos"]))
        if materiais["atividades"]:
            linhas.append("  Atividade: " + "; ".join(materiais["atividades"]))
        elif materiais["atividades_relacionadas"]:
            linhas.append("  Atividades do mesmo tema: " + "; ".join(materiais["atividades_relacionadas"]))
        if materiais["codigos"]:
            linhas.append("  Código de exemplo: " + "; ".join(materiais["codigos"]))
    return "\n".join(linhas)
