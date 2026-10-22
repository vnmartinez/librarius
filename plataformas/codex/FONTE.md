# Fonte — Codex (app, CLI, extensão IDE)

Consulta: 22/10/2026. Reconfirmar antes de gerar ou alterar qualquer manifesto.

| Assunto | URL |
|---|---|
| Skills (URL do briefing redireciona com 308) | https://developers.openai.com/codex/skills.md → https://learn.chatgpt.com/docs/build-skills.md |
| Construir plugins | https://developers.openai.com/codex/plugins/build.md |
| Campos aceitos na submissão | https://developers.openai.com/plugins/deploy/submission |
| Esquema Agent Plugins (manifesto portátil na raiz) | https://agent-plugins.org/schemas/1.0.0/plugin.schema.json |
| Referência prática (não oficial) | https://github.com/obra/superpowers (`.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`) |

## Fatos verificados

- Esquema Agent Plugins baixado em 22/10/2026 para `plataformas/codex/plugin.schema.json` (usado por `validar_codex`). `category`/`capabilities` não têm lista de valores na página de construção (exemplos: `Productivity`, `Read`, `Write`); `policy.authentication` só mostra `ON_INSTALL`. Marketplace de repositório também é lido em `.claude-plugin/marketplace.json` (compatibilidade).

- Skill = pasta com `SKILL.md` (frontmatter `name` e `description` obrigatórios). Opcionais: `scripts/`, `references/`, `assets/`, `agents/openai.yaml` (`interface`, `policy.allow_implicit_invocation`, `dependencies.tools`).
- Descoberta de skills de repositório: `.agents/skills` do diretório atual até a raiz do repositório; usuário em `$HOME/.agents/skills`.
- Manifesto portátil canônico: `plugin.json` **na raiz**, esquema Agent Plugins (obrigatórios `$schema` e `name`; propriedades permitidas: `$schema`, `name`, `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords`, `extensions`; `additionalProperties: false`). Skills descobertas em `skills/` sem campo no manifesto.
- `.codex-plugin/plugin.json` continua aceito como camada de compatibilidade; se `plugin.json` da raiz não tiver `extensions.com.openai`, a camada `.codex-plugin` fornece as configurações OpenAI (`interface`, etc.). As duas não são mescladas.
- Campos usados em `.codex-plugin/plugin.json` (scaffold oficial e superpowers): `name`, `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords`, `skills: "./skills/"`, `hooks`, `interface` (`displayName`, `shortDescription`, `longDescription`, `developerName`, `category`, `capabilities`, `defaultPrompt`, `websiteURL`, `privacyPolicyURL`, `termsOfServiceURL`, `brandColor`, `composerIcon`, `logo`, `screenshots`).
- Marketplace de repositório em `$REPO_ROOT/.agents/plugins/marketplace.json`: `name`, `interface.displayName`, `plugins[]` com `name`, `source` (`{"source": "local", "path": "./..."}`, caminho relativo à raiz do marketplace, começando com `./`), `policy` (`installation`: `AVAILABLE` | `INSTALLED_BY_DEFAULT` | `NOT_AVAILABLE`; `authentication`), `category` (obrigatório).
- Instalação avançada: `codex plugin marketplace add vnmartinez/librarius` (aceita `--ref`). Também `list`, `upgrade`, `remove`.
- Hooks recebem `PLUGIN_ROOT` e `PLUGIN_DATA`; Codex também define `CLAUDE_PLUGIN_ROOT` e `CLAUDE_PLUGIN_DATA` por compatibilidade.
- MCP: scaffold de compatibilidade usa `.mcp.json` com `mcpServers`; o formato portátil usa `mcp.json` na raiz (esquema Agent Plugins).

## Não verificado (reconfirmar na fase de matriz)

- Se `path: "./"` (plugin = raiz do marketplace) é aceito; o superpowers usa `{"source": "url", "url": "./"}`.
- Se `${CLAUDE_PLUGIN_ROOT}` é substituído em `args` do `.mcp.json` e no corpo de `SKILL.md` no Codex.
- Comando de validação estrutural oficial: a página não documenta nenhum.

## MCP (Tarefa 40, 22/10/2026)

- O manifesto portátil usa `mcp.json` na raiz (esquema Agent Plugins, `plataformas/codex/mcp.schema.json`, `${PLUGIN_ROOT}`); o mesmo arquivo serve ao Antigravity. `.mcp.json` (formato do Claude) fica como compatibilidade. Reconfirmar na matriz qual dos dois o Codex carrega.
