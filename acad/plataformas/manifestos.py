"""Validação estrutural dos manifestos de cada host (só lê arquivos; não instala nada)."""
from __future__ import annotations

import json
import re
from pathlib import Path

CHAVES_CLAUDE = {
    "$schema", "name", "displayName", "version", "description", "author", "homepage", "repository",
    "license", "keywords", "metadata", "icon", "documentationUrl", "supportUrl", "privacyPolicyUrl",
    "termsOfServiceUrl", "defaultEnabled", "dependencies", "settings", "userConfig", "types", "channels",
    "skills", "commands", "agents", "hooks", "mcpServers", "lspServers", "outputStyles", "workflows",
    "experimental",
}
CAMINHOS_CLAUDE = ("skills", "commands", "agents", "hooks", "lspServers", "outputStyles", "workflows")
_KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_RESERVADO = re.compile(r"^(claude|anthropic|anthropics|cc-plugin)(-|$)")


def _json(caminho: Path, achados: list[str]) -> dict | None:
    if not caminho.exists():
        achados.append(f"falta o arquivo {caminho.name}")
        return None
    try:
        dado = json.loads(caminho.read_text(encoding="utf-8"))
    except ValueError as erro:
        achados.append(f"{caminho.name} não é um JSON válido: {erro}")
        return None
    if not isinstance(dado, dict):
        achados.append(f"{caminho.name} deve ser um objeto")
        return None
    return dado


def _caminhos(valor) -> list[str]:
    if isinstance(valor, str):
        return [valor]
    if isinstance(valor, list):
        return [v for v in valor if isinstance(v, str)]
    return []


def validar_claude(raiz: Path) -> list[str]:
    achados: list[str] = []
    pasta = raiz / ".claude-plugin"
    if (raiz / "bin").exists():
        achados.append("a pasta bin/ na raiz impede a instalação no claude.ai e no Cowork")
    if pasta.exists():
        extras = sorted(p.name for p in pasta.iterdir() if p.name not in ("plugin.json", "marketplace.json"))
        if extras:
            achados.append("arquivos a mais em .claude-plugin/: " + ", ".join(extras))
    m = _json(pasta / "plugin.json", achados)
    if m is not None:
        nome = m.get("name")
        if not isinstance(nome, str) or not _KEBAB.match(nome):
            achados.append("name deve estar em kebab-case")
        elif nome != "librarius":
            achados.append("name deve ser librarius")
        elif _RESERVADO.match(nome):
            achados.append("name reservado")
        for chave in ("version", "description"):
            if not m.get(chave):
                achados.append(f"falta {chave}")
        autor = m.get("author")
        if not isinstance(autor, dict) or not autor.get("name"):
            achados.append("falta author.name")
        for chave in sorted(set(m) - CHAVES_CLAUDE):
            achados.append(f"chave desconhecida em plugin.json: {chave}")
        for chave in CAMINHOS_CLAUDE:
            for c in _caminhos(m.get(chave)):
                if not c.startswith("./"):
                    achados.append(f"{chave}: o caminho '{c}' deve começar com ./")
                elif ".." in Path(c).parts or not (raiz / c).exists():
                    achados.append(f"{chave}: caminho inexistente ou fora da raiz: {c}")
    mk = _json(pasta / "marketplace.json", achados)
    if mk is not None:
        if not mk.get("name"):
            achados.append("marketplace sem name")
        if not (isinstance(mk.get("owner"), dict) and mk["owner"].get("name")):
            achados.append("marketplace sem owner.name")
        plugins = mk.get("plugins")
        if not isinstance(plugins, list) or not plugins:
            achados.append("marketplace sem plugins")
        else:
            p = plugins[0]
            if p.get("name") != "librarius":
                achados.append("plugins[0].name deve ser librarius")
            if p.get("source") != "./":
                achados.append("plugins[0].source deve ser ./")
    return achados


def validar_todos(raiz: Path) -> dict[str, list[str]]:
    return {"claude": validar_claude(raiz)}
