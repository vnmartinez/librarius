# Resultados da matriz de instalação

Versão do plugin: 0.1.0. Preencher só depois de seguir o roteiro de cada host, com autorização do professor.

## Verificações automáticas (não invasivas, 22/10/2026)

Comando: `python -m pytest -m hosts testes/integracao/test_hosts.py`. Só lê; nada é instalado nem alterado.

| Verificação | Versão do host | Resultado |
|---|---|---|
| `claude plugin validate . --strict` | Claude Code 2.1.302 | ok ("Validation passed") |
| `codex plugin marketplace --help` e `list` | codex-cli 0.163.0 | ok |
| `agy plugin list --json` | agy 1.4.5 | ok |
| `agy plugin validate . --json` | agy 1.4.5 | ok; 7 skills e 1 servidor MCP; avisos conhecidos: `AGENTS.md` da raiz não é carregado pelo Antigravity e `mcp.json` só vale com a flag `enable-agent-plugins-spec` ligada |
| `opencode --version` | OpenCode 2.1.3 | ok |

## Matriz host × checagem

Legenda: ok / falhou / não se aplica / **pendente** (aguardando autorização do professor).

| Host | Data | Versão do host | Versão do plugin | 1 Instalado | 2 Skill carrega | 3 Ambiente | 4 Aula de hoje | 5 Drive (leitura) | 6 MCP | Observação |
|---|---|---|---|---|---|---|---|---|---|---|
| Claude Code | — | — | 0.1.0 | pendente | pendente | pendente | pendente | pendente | pendente | |
| Claude Cowork (aplicativo Claude) | — | — | 0.1.0 | pendente | pendente | pendente | pendente | pendente | pendente | |
| Codex (aplicativo, terminal e extensão do editor) | — | — | 0.1.0 | pendente | pendente | pendente | pendente | pendente | pendente | |
| Antigravity — aplicativo | — | — | 0.1.0 | pendente | pendente | pendente | pendente | pendente | pendente | |
| Antigravity — editor (IDE) | — | — | 0.1.0 | pendente | pendente | pendente | pendente | pendente | pendente | |
| Antigravity — terminal (`agy`) | — | — | 0.1.0 | pendente | pendente | pendente | pendente | pendente | pendente | |
| OpenCode (terminal, aplicativo e extensão do editor) | — | — | 0.1.0 | pendente | pendente | pendente | pendente | pendente | pendente | |
| ChatGPT | — | — | 0.1.0 | pendente | pendente | não se aplica | não se aplica | não se aplica | não se aplica | |
