# Matriz — ChatGPT

Versão do plugin testada: 0.1.0. Anote os resultados em [resultados.md](resultados.md). **Não instale nada sem a autorização do professor.**

## Pré-requisitos

- Conta do ChatGPT com opção de enviar skills ou plugins (a página oficial de ajuda está bloqueada para leitura; formato do envio **não confirmado**).
- Os zips de `dist/chatgpt/`, gerados pelo desenvolvedor com `python scripts/empacotar-chatgpt.py`.

## Caminho do professor (sem terminal)

1. Envie cada zip como skill (menu de skills/plugins do ChatGPT; anote o caminho exato que usou).
2. Abra uma conversa nova e confirme que a skill aparece.

> Só as checagens 1 e 2 se aplicam. Sem acesso ao computador, o ChatGPT apenas conversa, planeja e redige.

## Caminho avançado (terminal)

- `python scripts/empacotar-chatgpt.py` (gera um zip por skill em `dist/chatgpt/`).

## Checagens (spec §15)

| # | Checagem | Resultado esperado |
|---|---|---|
| 1 | Plugin aparece instalado | As skills aparecem na lista de skills do ChatGPT. |
| 2 | A skill `usando-agente-academico` carrega | Ao perguntar "o que você sabe fazer?", o assistente apresenta as skills em português simples, sem jargão. |
| 3 | `acad ambiente verificar` | Não se aplica (sem acesso ao computador). |
| 4 | Consulta do cronograma | Não se aplica (D1/D2). |
| 5 | Leitura do Drive | Não se aplica (D1/D2). |
| 6 | Ferramentas MCP | Não se aplica. |

## Onde anotar

Preencha a linha deste host em [resultados.md](resultados.md) (data, versão do host, versão do plugin, resultado: ok / falhou / não se aplica, observação). Fonte oficial consultada: `plataformas/chatgpt/FONTE.md`.
