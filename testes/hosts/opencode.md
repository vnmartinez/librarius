# Matriz — OpenCode (terminal, aplicativo e extensão do editor)

Versão do plugin testada: 0.1.0. Anote os resultados em [resultados.md](resultados.md). **Não instale nada sem a autorização do professor.**

## Pré-requisitos

- OpenCode instalado (versão da verificação automática: 2.1.3, ou seja, a v2).
- Python 3.11 ou mais novo no computador.
- Git instalado (ou o zip do GitHub).

## Caminho do professor (sem terminal)

1. Abra o OpenCode e escreva: "Siga o roteiro .opencode/INSTALAR.md do repositório github.com/vnmartinez/librarius para instalar o Librarius".
2. Diga a pasta onde guardar o projeto (fora do Google Drive) e responda "sim" aos passos.
3. Abra uma conversa nova.

> O roteiro cobre a v2 (opção `skills`) e a estável (junção em `~/.config/opencode/skills`). Registrar qual foi usada.

## Caminho avançado (terminal)

- `git clone https://github.com/vnmartinez/librarius <pasta>`
- v2: acrescentar `<pasta>/skills` à lista `skills` de `~/.config/opencode/opencode.json`.
- estável: `mklink /J "%USERPROFILE%\.config\opencode\skills\<nome>" "<pasta>\skills\<nome>"` para cada skill.

## Checagens (spec §15)

| # | Checagem | Resultado esperado |
|---|---|---|
| 1 | Plugin aparece instalado | O OpenCode lista as sete skills do Librarius. |
| 2 | A skill `usando-agente-academico` carrega | Ao perguntar "o que você sabe fazer?", o assistente apresenta as skills em português simples, sem jargão. |
| 3 | `acad ambiente verificar` roda pelo lançador | O assistente roda `python "<raiz>/scripts/acad.py" ambiente verificar --json` e responde que está tudo pronto (saída 0). Na primeira vez prepara o ambiente e pode demorar alguns minutos. |
| 4 | "Qual a aula de hoje de Estrutura de Dados 2?" bate com o oráculo | `python scripts/acad.py cronograma consultar --data 2026-07-28 --raiz testes/amostras/fasoft --json` (amostra do repositório) deve dar o mesmo que `python testes/referencia/verificar_cronograma.py --dir testes/amostras/fasoft --data 2026-07-28 --json`: 1 aula, "Estrutura de Dados 2 — Aula 01: Apresentação da Disciplina/Ementa/Cronograma". |
| 5 | Leitura do Drive real, somente leitura | Com autorização do professor, a consulta de uma data real do semestre devolve a aula; nada é criado, movido ou apagado em `G:\Meu Drive\Fasoft` (conferir `git`/data de modificação não mudou). Nunca abrir pastas de alunos. |
| 6 | Ferramentas MCP aparecem | Com o OpenCode aberto na pasta do clone, o servidor `librarius` (`opencode.json`, bloco `mcp`) aparece como ativo. |

## Onde anotar

Preencha a linha deste host em [resultados.md](resultados.md) (data, versão do host, versão do plugin, resultado: ok / falhou / não se aplica, observação). Fonte oficial consultada: `plataformas/opencode/FONTE.md`.
