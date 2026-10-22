# Fonte — padrão aberto Agent Skills (`SKILL.md`)

Consulta: 22/10/2026.

| Assunto | URL |
|---|---|
| Especificação | https://agentskills.io/specification |
| Implementação em clientes (citada no briefing) | https://agentskills.io/client-implementation/adding-skills-support.md |
| Validador de referência | https://github.com/agentskills/agentskills/tree/main/skills-ref |

## Fatos verificados

- `name`: obrigatório, 1–64, só `a-z`, `0-9` e `-`, sem começar/terminar com `-`, sem `--`, igual ao nome da pasta.
- `description`: obrigatório, 1–1024, diz o que faz e quando usar.
- Opcionais: `license`, `compatibility` (1–500), `metadata` (mapa string→string), `allowed-tools` (experimental).
- Pastas opcionais: `scripts/`, `references/`, `assets/`. Referências por caminho relativo à raiz da skill, um nível de profundidade.
- Corpo recomendado < 500 linhas / < 5000 tokens.
- Validação: `skills-ref validate ./minha-skill`.
