"""Conformidade das skills com o padrão aberto Agent Skills."""
from __future__ import annotations

import re
from pathlib import Path

import yaml

SKILLS = (
    "usando-agente-academico",
    "organizador-academico",
    "planejador-semestre",
    "distribuidor-ementa",
    "gerador-aulas",
    "gerador-avaliacoes",
    "validador-academico",
)

CHAVES_PERMITIDAS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
SECOES = ("## Quando usar", "## Como conversar com o professor", "## Passo a passo", "## Exemplos de pedidos")
INICIO = "<!-- inicio:chamar-nucleo -->"
FIM = "<!-- fim:chamar-nucleo -->"
_NOME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_COMANDO = re.compile(r"`acad ([a-z-]+(?: [a-z-]+)?)")
RAIZ = Path(__file__).resolve().parents[2]
TRECHO = RAIZ / "scripts" / "trechos" / "chamar-nucleo.md"


def ler_skill(pasta: Path) -> tuple[dict, str]:
    texto = (pasta / "SKILL.md").read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)$", texto, re.S)
    if not m:
        return {}, texto
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def trecho_comum() -> str:
    return TRECHO.read_text(encoding="utf-8").strip()


def bloco_entre_marcas(corpo: str) -> str | None:
    if INICIO not in corpo or FIM not in corpo:
        return None
    return corpo.split(INICIO, 1)[1].split(FIM, 1)[0].strip()


def problemas(pasta: Path) -> list[str]:
    achados: list[str] = []
    if not (pasta / "SKILL.md").exists():
        return ["falta o arquivo SKILL.md"]
    meta, corpo = ler_skill(pasta)
    nome = meta.get("name")
    if not isinstance(nome, str) or not 1 <= len(nome) <= 64 or not _NOME.match(nome):
        achados.append("nome fora do padrão (1 a 64 letras minúsculas, números e hífen)")
    elif nome != pasta.name:
        achados.append("o nome precisa ser igual ao da pasta")
    desc = meta.get("description")
    if not isinstance(desc, str) or not 1 <= len(desc) <= 1024:
        achados.append("descrição deve ter de 1 a 1024 caracteres")
    comp = meta.get("compatibility")
    if comp is not None and (not isinstance(comp, str) or not 1 <= len(comp) <= 500):
        achados.append("compatibilidade deve ter até 500 caracteres")
    extras = set(meta) - CHAVES_PERMITIDAS
    if extras:
        achados.append("chaves não permitidas: " + ", ".join(sorted(extras)))
    if len(corpo.splitlines()) >= 500:
        achados.append("corpo com 500 linhas ou mais")
    for secao in SECOES:
        if not re.search(rf"^{re.escape(secao)}\s*$", corpo, re.M):
            achados.append(f"falta a seção '{secao[3:]}'")
    bloco = bloco_entre_marcas(corpo)
    if bloco is None:
        achados.append("falta o trecho comum 'chamar-nucleo'")
    elif bloco != trecho_comum():
        achados.append("trecho comum 'chamar-nucleo' fora de sincronia")
    return achados


def comandos_citados(corpo: str) -> set[str]:
    return set(_COMANDO.findall(corpo))
