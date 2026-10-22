# Fonte — Antigravity 2.0 (app), Antigravity IDE e Antigravity CLI (`agy`)

Consulta: 22/10/2026. Reconfirmar antes de gerar ou alterar qualquer manifesto.

| Assunto | URL |
|---|---|
| Plugins (app, IDE, CLI) | https://antigravity.google/docs/plugins?tab=cli |
| URL do briefing para a CLI (só redireciona para a anterior) | https://www.antigravity.google/docs/cli/plugins |
| Esquema citado nos exemplos (HTTP 404 em 22/10/2026) | https://antigravity.google/schemas/v1/plugin.json |
| Referência prática (não oficial) | https://github.com/obra/superpowers (`.antigravity-plugin/plugin.json`) |

## Fatos verificados

- Estrutura: `plugin.json` **na raiz do plugin** ("required marker and manifest file"), `mcp_config.json`, `hooks.json`, `skills/<nome>/SKILL.md`, `agents/<nome>.md`, `rules/<nome>.md`.
- Campos do manifesto: `name` (obrigatório na CLI; padrão `^[a-zA-Z0-9-_]+$`), `description` (opcional). Exemplos incluem `$schema`. O esquema declara `additionalProperties: false`: **não pôr `version`, `author` etc. no `plugin.json` da raiz.**
- Locais de instalação: projeto `.agents/plugins/`; global `~/.gemini/config/plugins/`; staging da CLI `~/.gemini/antigravity-cli/plugins/<nome>/`.
- CLI: `agy plugin install https://github.com/<owner>/<repo>`, `agy plugin install <caminho-local>`, `agy plugin list [--json]`, `enable`, `disable`, `uninstall`.
- Nenhum comando de validação documentado.

## Verificado na CLI instalada (22/10/2026, sem instalar nada)

- `agy plugin --help`: `list [--json]`, `import`, `install <alvo>` (aceita `plugin[@marketplace]`), `uninstall`, `enable`, `disable`, **`validate [path] [--strict] [--json]`** (lê só arquivos), `link`.
- `agy plugin validate <raiz> --json` no repositório: manifesto `plugin.json` aceito como Agent Plugins (`agentPluginsSpec: true`), 7 skills detectadas, nenhum erro. Aviso (não bloqueia): `AGENTS.md` da raiz "nunca é carregado" pelo Antigravity (regras só vêm de `rules/`); mantido na raiz porque é o texto de reserva para os outros hosts. Com `--strict` esse aviso falha; por isso o teste usa o modo normal.
- Nota: `plugin.json` com o `$schema` Agent Plugins carrega como plugin Agent Plugins enquanto a flag `enable-agent-plugins-spec` estiver ligada, e como plugin nativo caso contrário.
- `agy plugin list --json` devolve lista de objetos `name`, `enabled`, `version`, `source`, `path`, `skills`.
- Atenção: `.agents/plugins/` é também o local de instalação manual do Antigravity no projeto; nele o repositório guarda `marketplace.json` do Codex. Não afeta a validação; reconfirmar na matriz.

## Conflito a resolver na implementação

- O `plugin.json` da raiz também é o manifesto portátil do Codex (esquema Agent Plugins, que exige `$schema`). Um arquivo só com `$schema`, `name` e `description` satisfaz os dois esquemas no papel. O superpowers usa `.antigravity-plugin/plugin.json`, com campos fora do esquema oficial (`displayName`, `version`, `logo`…), o que a documentação não descreve. A spec adota a raiz e testa as duas formas na fase de matriz.

## Não verificado

- Formato exato de `mcp_config.json` e de `hooks.json`; variável de ambiente com a raiz do plugin.
- Se o Antigravity rejeita `$schema` apontando para o esquema Agent Plugins.
