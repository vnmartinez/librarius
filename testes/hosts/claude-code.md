# Matriz — Claude Code

Versão do plugin testada: 0.1.0. Anote os resultados em [resultados.md](resultados.md). **Não instale nada sem a autorização do professor.**

## Pré-requisitos

- Claude Code instalado e com login feito.
- Python 3.11 ou mais novo no computador (gratuito; o assistente ajuda a instalar).

## Caminho do professor (sem terminal)

1. Abra o Claude Code e escreva: "Instale o Librarius a partir de github.com/vnmartinez/librarius".
2. Responda "sim" quando o assistente pedir autorização para cada passo.
3. Abra uma conversa nova (para as skills carregarem).

> O fluxo gráfico não está documentado em `FONTE.md`; por isso o caminho do professor é pedir ao próprio assistente.

## Caminho avançado (terminal)

- `claude plugin marketplace add vnmartinez/librarius`
- `claude plugin install librarius@librarius`

## Checagens (spec §15)

| # | Checagem | Resultado esperado |
|---|---|---|
| 1 | Plugin aparece instalado | `claude plugin list` mostra `librarius`. |
| 2 | A skill `usando-agente-academico` carrega | Ao perguntar "o que você sabe fazer?", o assistente apresenta as skills em português simples, sem jargão. |
| 3 | `acad ambiente verificar` roda pelo lançador | O assistente roda `python "<raiz>/scripts/acad.py" ambiente verificar --json` e responde que está tudo pronto (saída 0). Na primeira vez prepara o ambiente e pode demorar alguns minutos. |
| 4 | "Qual a aula de hoje de Estrutura de Dados 2?" bate com o oráculo | `python scripts/acad.py cronograma consultar --data 2026-07-28 --raiz testes/amostras/fasoft --json` (amostra do repositório) deve dar o mesmo que `python testes/referencia/verificar_cronograma.py --dir testes/amostras/fasoft --data 2026-07-28 --json`: 1 aula, "Estrutura de Dados 2 — Aula 01: Apresentação da Disciplina/Ementa/Cronograma". |
| 5 | Leitura do Drive real, somente leitura | Com autorização do professor, a consulta de uma data real do semestre devolve a aula; nada é criado, movido ou apagado em `G:\Meu Drive\Fasoft` (conferir `git`/data de modificação não mudou). Nunca abrir pastas de alunos. |
| 6 | Ferramentas MCP aparecem | Ferramentas `ambiente-verificar`, `cronograma-consultar`, `validar` … aparecem no comando `/mcp` (servidor `librarius`, vindo de `.mcp.json`). |

## Onde anotar

Preencha a linha deste host em [resultados.md](resultados.md) (data, versão do host, versão do plugin, resultado: ok / falhou / não se aplica, observação). Fonte oficial consultada: `plataformas/claude/FONTE.md`.
