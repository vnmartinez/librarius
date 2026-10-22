# Fonte — OpenCode (TUI, desktop, extensão IDE)

Consulta: 22/10/2026. Reconfirmar antes de gerar ou alterar qualquer arquivo de configuração.

| Assunto | URL |
|---|---|
| Skills (v2, citada no briefing) | https://opencode.ai/v2/docs/skills/ |
| Skills (documentação estável) | https://opencode.ai/docs/skills/ |
| Servidores MCP | https://opencode.ai/docs/mcp-servers/ |
| Referência prática (não oficial) | https://github.com/obra/superpowers (`.opencode/INSTALL.md`, `.opencode/plugins/`) |

## Fatos verificados

- Skills lidas de `.opencode/skills/<nome>/SKILL.md`, `.claude/skills/…`, `.agents/skills/…` (projeto, subindo até a raiz do worktree) e de `~/.config/opencode/skills`, `~/.claude/skills`, `~/.agents/skills` (global).
- Estável: `name` obrigatório, 1–64, `^[a-z0-9]+(-[a-z0-9]+)*$`, igual ao nome da pasta; `description` 1–1024. Opcionais `license`, `compatibility`, `metadata`.
- v2: opção `skills` no `opencode.json` aceita caminhos locais e URLs de catálogo HTTP(S); caminhos relativos resolvem a partir do diretório de trabalho. A documentação estável **não** documenta essa opção.
- Permissões: `permission.skill` com padrões (`allow` | `deny` | `ask`).
- MCP local: chave `mcp` → `{ "<nome>": { "type": "local", "command": ["..."], "enabled": true, "environment": {...} } }`.
- Lê `AGENTS.md`.

## Não verificado

- Qual versão (estável ou v2) o professor terá; o roteiro `.opencode/INSTALAR.md` cobre as duas (opção `skills` na v2; cópia/link em `~/.config/opencode/skills` na estável).

## MCP (Tarefa 40, 22/10/2026)

- `opencode.json` do repositório declara `mcp.librarius` (`type: local`, `command` em lista, `enabled: true`), com caminho relativo `./scripts/acad.py` que resolve a partir do diretório de trabalho (OpenCode aberto na raiz do clone). Para uso global, usar o caminho absoluto do clone.
