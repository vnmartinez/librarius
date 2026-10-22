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


def validar_codex(raiz: Path) -> list[str]:
    import jsonschema

    achados: list[str] = []
    raiz_json = _json(raiz / "plugin.json", achados)
    if raiz_json is not None:
        esquema = json.loads((raiz / "plataformas" / "codex" / "plugin.schema.json").read_text(encoding="utf-8"))
        for erro in jsonschema.Draft202012Validator(esquema).iter_errors(raiz_json):
            achados.append(f"plugin.json da raiz: {erro.message}")
        extras = sorted(set(raiz_json) - {"$schema", "name", "description"})
        if extras:
            achados.append("plugin.json da raiz só pode ter $schema, name e description (Antigravity): " + ", ".join(extras))
    m = _json(raiz / ".codex-plugin" / "plugin.json", achados)
    if m is not None:
        for chave in ("name", "version", "description"):
            if not m.get(chave):
                achados.append(f".codex-plugin: falta {chave}")
        if m.get("skills") != "./skills/":
            achados.append(".codex-plugin: skills deve ser ./skills/")
        interface = m.get("interface") if isinstance(m.get("interface"), dict) else {}
        for chave in ("displayName", "category"):
            if not interface.get(chave):
                achados.append(f".codex-plugin: falta interface.{chave}")
    mk = _json(raiz / ".agents" / "plugins" / "marketplace.json", achados)
    if mk is not None:
        if not mk.get("name"):
            achados.append("marketplace do Codex sem name")
        plugins = mk.get("plugins")
        if not isinstance(plugins, list) or not plugins:
            achados.append("marketplace do Codex sem plugins")
        else:
            p = plugins[0]
            if p.get("name") != "librarius":
                achados.append("plugins[0].name deve ser librarius")
            if p.get("source") != {"source": "local", "path": "./"}:
                achados.append("plugins[0].source deve ser local com path ./")
            politica = p.get("policy") if isinstance(p.get("policy"), dict) else {}
            if politica.get("installation") not in ("AVAILABLE", "INSTALLED_BY_DEFAULT", "NOT_AVAILABLE"):
                achados.append("policy.installation inválido")
            if not politica.get("authentication"):
                achados.append("falta policy.authentication")
            if not p.get("category"):
                achados.append("falta category")
    return achados


def validar_antigravity(raiz: Path) -> list[str]:
    achados: list[str] = []
    m = _json(raiz / "plugin.json", achados)
    if m is not None:
        extras = sorted(set(m) - {"$schema", "name", "description"})
        if extras:
            achados.append("plugin.json só pode ter $schema, name e description: " + ", ".join(extras))
        if not isinstance(m.get("name"), str) or not re.match(r"^[a-zA-Z0-9-_]+$", m["name"]):
            achados.append("name deve casar com ^[a-zA-Z0-9-_]+$")
    skills = raiz / "skills"
    pastas = [p for p in skills.iterdir() if p.is_dir()] if skills.exists() else []
    if not pastas:
        achados.append("não há skills/")
    for p in pastas:
        if not (p / "SKILL.md").exists():
            achados.append(f"falta SKILL.md em skills/{p.name}")
    return achados


def validar_opencode(raiz: Path) -> list[str]:
    achados: list[str] = []
    m = _json(raiz / "opencode.json", achados)
    if m is not None:
        skills = m.get("skills")
        if not isinstance(skills, list) or not all(isinstance(x, str) for x in skills):
            achados.append("opencode.json: skills deve ser uma lista de textos")
        else:
            for c in skills:
                if c.startswith(("http://", "https://", "~/")) or Path(c).is_absolute():
                    continue
                if not (raiz / c).exists():
                    achados.append(f"opencode.json: caminho de skills não existe: {c}")
    roteiro = raiz / ".opencode" / "INSTALAR.md"
    if not roteiro.exists():
        achados.append("falta .opencode/INSTALAR.md")
    else:
        t = roteiro.read_text(encoding="utf-8")
        if "`skills`" not in t or "mklink /J" not in t:
            achados.append("INSTALAR.md deve cobrir a versão 2 (opção skills) e a estável (junção)")
    return achados


def validar_todos(raiz: Path) -> dict[str, list[str]]:
    return {"claude": validar_claude(raiz), "codex": validar_codex(raiz), "antigravity": validar_antigravity(raiz),
            "opencode": validar_opencode(raiz)}
