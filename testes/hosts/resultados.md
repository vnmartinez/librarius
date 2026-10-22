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

## Critério de pronto do MVP (briefing §15)

- [x] `acad validar` sobre o Segundo Semestre de 2026 real, somente leitura, sem LLM (`pytest -m drive`, 22/10/2026).
- [x] `acad cronograma consultar` reproduz a skill `cronograma` no Drive real (`pytest -m drive`, 22/10/2026).
- [ ] Mesmo comando de consulta em Claude Code, Cowork, Codex, Antigravity (app, IDE, CLI) e OpenCode — **pendente de autorização do professor** (instalar altera a configuração dos agentes).
- [ ] Skills carregam no ChatGPT — **pendente** (formato do envio não confirmado; ver `plataformas/chatgpt/FONTE.md`).
- [ ] Primeiro caso de uso completo (ED2 2027-1, quatro primeiras aulas com material) — **pendente** só do calendário 2027-1 (D3 e D4 fechadas em 22/10/2026; o gerador de slides já existe).
- [ ] Teste com dois professores sem formação técnica — **pendente** (etapa humana).

## Pontos em aberto da spec §12 (a confirmar na matriz)

- Codex aceita `path: "./"` no marketplace e substitui `${CLAUDE_PLUGIN_ROOT}` no `.mcp.json`? Qual dos dois (`mcp.json` portátil ou `.mcp.json`) carrega?
- Antigravity aceita o `plugin.json` da raiz com `$schema` Agent Plugins? (`agy plugin validate` já aceita como Agent Plugins; falta o teste de instalação.) Sem a flag `enable-agent-plugins-spec`, o MCP nativo (`mcp_config.json`) não foi criado por falta de documentação da variável da raiz.
- OpenCode do professor: estável ou v2? (a máquina de desenvolvimento tem a v2.1.3.)
- Cowork carrega MCP stdio?
- Formato do envio de skills ao ChatGPT.
- No Windows, `python` pode não existir no PATH (usar `py -3`); o `.mcp.json` assume `python`.
