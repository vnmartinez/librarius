# Fonte — Claude Code e Claude Cowork / app Claude

Consulta: 22/10/2026. Reconfirmar antes de gerar ou alterar qualquer manifesto.

| Assunto | URL |
|---|---|
| Manifesto `plugin.json` (campos, caminhos, variáveis) | https://code.claude.com/docs/en/plugins-reference |
| Marketplace `marketplace.json` | https://code.claude.com/docs/en/plugin-marketplaces |
| Visão geral de plugins (citada no briefing) | https://code.claude.com/docs/en/plugins/overview |
| Restrição de `bin/` em claude.ai e Cowork (citada na referência) | https://claude.com/docs/plugins/org-sync#keep-executables-out-of-the-top-level-bin-directory |

## Fatos verificados

- Manifesto em `.claude-plugin/plugin.json`; é opcional. Único campo obrigatório: `name` (kebab-case). Campos usados aqui: `name`, `displayName`, `version`, `description`, `author` (`name` obrigatório), `homepage`, `repository`, `license`, `keywords`.
- Campos de topo desconhecidos são removidos com aviso; `claude plugin validate <dir>` é a checagem oficial (`--strict` transforma aviso em falha).
- Layout padrão na raiz do plugin: `skills/<nome>/SKILL.md`, `commands/`, `agents/`, `hooks/hooks.json`, `.mcp.json`. Nada além do manifesto dentro de `.claude-plugin/`.
- Caminhos de componente começam com `./` e não podem sair da raiz (`..` é erro).
- `${CLAUDE_PLUGIN_ROOT}` (raiz instalada, muda a cada atualização), `${CLAUDE_PLUGIN_DATA}` (`~/.claude/plugins/data/<id>/`, persiste entre atualizações; usar para ambiente Python), `${CLAUDE_PROJECT_DIR}`.
- `${...}` é substituído no corpo Markdown de skills, em `command`/`args`/`env` de servidores MCP stdio e em hooks. Não existe no ambiente dos comandos que o modelo roda pelo Bash.
- MCP em `.mcp.json` na raiz (mapa `mcpServers`) ou inline em `mcpServers`.
- Hooks: arquivo `hooks/hooks.json` com envoltório `{"hooks": {...}}`.
- **claude.ai e Cowork não instalam plugin que tenha a pasta `bin/` na raiz.** Não usar `bin/`.
- Marketplace: `.claude-plugin/marketplace.json` com `name`, `owner` (`name`), `plugins[]` (`name`, `source`, `description`). `source: "./"` aponta para a raiz do marketplace. Nome da entrada igual ao `name` do `plugin.json`.
- Nomes reservados: não começar com `claude-`, `anthropic-` etc. `librarius` é permitido.
- Instalação avançada: `claude plugin marketplace add vnmartinez/librarius` e `claude plugin install librarius@<marketplace>`.

## Não verificado (reconfirmar na fase de matriz)

- Fluxo gráfico do app Claude/Cowork para adicionar marketplace ou enviar zip, e quais componentes Cowork carrega (MCP stdio? hooks?).

## MCP (Tarefa 40, 22/10/2026)

- `.mcp.json` na raiz com `mcpServers.librarius` (`command: python`, `args: ["${CLAUDE_PLUGIN_ROOT}/scripts/acad.py", "mcp"]`); `${CLAUDE_PLUGIN_ROOT}` expande em `command`/`args`/`env` de MCP stdio. `claude plugin validate . --strict` aceita (v2.1.302). No Windows o comando `python` pode não existir; reconfirmar na matriz.
