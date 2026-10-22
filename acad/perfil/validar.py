"""Problemas do perfil em portugues simples."""
from __future__ import annotations

import re

from jsonschema import Draft202012Validator

from acad import esquemas
from acad.erros import ErroAcad

NOMES = {
    "versao_esquema": "a versão do perfil", "perfil": "o perfil", "id": "o identificador do perfil",
    "instituicao": "o nome da instituição", "disciplina_pasta": "a regra que reconhece as pastas das disciplinas",
    "subpastas_disciplina": "a lista de pastas de cada disciplina", "pasta_arquivo": "a pasta de arquivo morto",
    "pasta_avaliacoes": "a regra da pasta de avaliações", "pasta_modelos": "a regra da pasta de modelos",
    "etapas_avaliacao": "as etapas de avaliação", "nomenclatura": "as regras de nomes",
    "aula": "a regra do nome das aulas", "lista": "a regra do nome das listas",
    "pasta": "a regra do nome das pastas", "sufixos_proibidos": "os finais de nome proibidos",
    "carga_horaria": "a carga horária", "unidade": "a unidade da carga horária",
    "minutos_hora_aula": "os minutos da hora-aula", "exclusao": "a lista de pastas protegidas",
    "estrutura": "a estrutura de pastas", "semestre": "a regra que reconhece a pasta do semestre",
    "periodos": "os nomes dos períodos", "administracao": "a regra da pasta de administração",
    "papeis": "os nomes das pastas da disciplina", "modelos": "os modelos da instituição",
    "slides": "o padrão visual dos slides",
}
REGRAS = [("disciplina_pasta",), ("pasta_avaliacoes",), ("pasta_modelos",),
          ("nomenclatura", "aula"), ("nomenclatura", "lista"), ("nomenclatura", "pasta"),
          ("estrutura", "semestre"), ("estrutura", "administracao")]
GRUPOS = {("estrutura", "semestre"): ("ano", "periodo"), ("disciplina_pasta",): ("nome",)}


def _nome(campo: str) -> str:
    return NOMES.get(campo, f"“{campo}”")


def _frase_do_esquema(erro) -> str:
    campos = [parte for parte in erro.absolute_path if isinstance(parte, str)]
    ultimo = campos[-1] if campos else "perfil"
    if erro.validator == "required":
        falta = re.findall(r"'([^']+)'", erro.message)[0]
        return f"Falta {_nome(falta)}."
    if erro.validator == "additionalProperties":
        extras = re.findall(r"'([^']+)'", erro.message)
        return f"O perfil tem uma informação que não conheço: “{extras[0]}”."
    if erro.validator == "pattern" and "paleta" in campos:
        return f"A cor “{erro.instance}” não é válida; use seis letras ou números, como 1F3A5F."
    if ultimo == "versao_esquema":
        return "A versão do perfil não é conhecida."
    texto = _nome(ultimo)
    return f"{texto[0].upper()}{texto[1:]} não está no formato esperado."


def problemas_do_perfil(documento: dict) -> list[str]:
    validador = Draft202012Validator(esquemas.carregar_esquema("perfil"))
    erros = sorted(validador.iter_errors(documento), key=lambda erro: [str(p) for p in erro.absolute_path])
    problemas = list(dict.fromkeys(_frase_do_esquema(erro) for erro in erros))
    perfil = documento.get("perfil") if isinstance(documento, dict) else None
    if not isinstance(perfil, dict):
        return problemas or ["O perfil está vazio."]
    for caminho in REGRAS:
        valor = perfil
        for parte in caminho:
            valor = valor.get(parte) if isinstance(valor, dict) else None
        if not isinstance(valor, str):
            continue
        texto = _nome(caminho[-1])
        try:
            regra = re.compile(valor)
        except re.error:
            problemas.append(f"{texto[0].upper()}{texto[1:]} não funciona.")
            continue
        faltando = [grupo for grupo in GRUPOS.get(caminho, ()) if grupo not in regra.groupindex]
        if faltando:
            problemas.append(f"{texto[0].upper()}{texto[1:]} precisa separar {' e '.join(faltando)}.")
    return problemas


def validar_perfil_ou_falhar(documento: dict) -> None:
    problemas = problemas_do_perfil(documento)
    if problemas:
        raise ErroAcad("perfil-invalido",
                       f"O perfil da instituição tem problemas: {' '.join(problemas[:3])}",
                       "; ".join(esquemas.validar("perfil", documento)) or "; ".join(problemas), saida=1)
