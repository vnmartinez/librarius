from __future__ import annotations

import random
import re
from copy import deepcopy
from datetime import date

from acad.geracao.nomes import limpar_tema
from acad.geracao.latex import escapar_latex


def versoes(questoes: list[dict], semente: int, n: int) -> list[list[dict]]:
    saida = []
    for indice in range(n):
        itens = deepcopy(questoes)
        if indice:
            sorteio = random.Random(f"{semente}-{indice}")
            sorteio.shuffle(itens)
            for item in itens:
                alternativas = item.get("alternativas")
                if alternativas:
                    resposta = item.get("resposta")
                    correta = alternativas[resposta] if isinstance(resposta, int) and not isinstance(resposta, bool) else resposta
                    sorteio.shuffle(alternativas)
                    if isinstance(resposta, int) and not isinstance(resposta, bool):
                        item["resposta"] = alternativas.index(correta)
        saida.append(itens)
    return saida


def nome_arquivo(disciplina_nome: str, etapa: str, descricao: str, turma: str,
                 versao: str | None, gabarito: bool, ext: str) -> str:
    partes = [limpar_tema(disciplina_nome), etapa, limpar_tema(descricao), turma]
    if versao:
        partes.append(f"Versão {versao}")
    if gabarito:
        partes.append("Gabarito")
    return " - ".join(partes) + "." + ext.lstrip(".")


def _corpo(questoes: list[dict], gabarito: bool) -> str:
    linhas = [r"\begin{enumerate}"]
    for questao in questoes:
        linhas.append(r"\item " + escapar_latex(str(questao["enunciado"])))
        if questao.get("alternativas"):
            linhas.append(r"\begin{enumerate}")
            for alternativa in questao["alternativas"]:
                linhas.append(r"\item " + escapar_latex(str(alternativa)))
            linhas.append(r"\end{enumerate}")
        if gabarito:
            resposta = questao["resposta"]
            if isinstance(resposta, int) and not isinstance(resposta, bool) and questao.get("alternativas"):
                resposta = questao["alternativas"][resposta]
            linhas.append(r"\par\textbf{" + escapar_latex(str(resposta)) + "}")
    linhas.append(r"\end{enumerate}")
    return "\n".join(linhas)


def renderizar(modelo: str, dados: dict, questoes: list[dict], gabarito: bool) -> str:
    texto = modelo
    campos = {"Titulo": dados["titulo"], "Disciplina": dados["disciplina"],
              "Professor": dados.get("professor", ""),
              "Data": date.fromisoformat(dados["data"]).strftime("%d/%m/%Y")}
    for campo, valor in campos.items():
        padrao = r"(\\avaliacao" + campo + r"\{)[^}]*\}"
        texto = re.sub(padrao, lambda achado: achado.group(1) + escapar_latex(str(valor)) + "}", texto)
    corpo = _corpo(questoes, gabarito)
    if "%% CORPO %%" in texto:
        return texto.replace("%% CORPO %%", corpo)
    linhas = texto.splitlines(keepends=True)
    for indice, linha in enumerate(linhas):
        if "A partir daqui entra o corpo da prova" in linha:
            linhas.insert(indice + 1, "\n" + corpo + "\n")
            return "".join(linhas)
    return texto.replace(r"\end{document}", corpo + "\n" + r"\end{document}")
