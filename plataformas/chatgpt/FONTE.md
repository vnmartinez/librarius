# Fonte — ChatGPT

Consulta: 22/10/2026. Reconfirmar antes de gerar o empacotador.

| Assunto | URL | Situação |
|---|---|---|
| Skills in ChatGPT (citada no briefing) | https://help.openai.com/en/articles/20001066-skills-in-chatgpt | **HTTP 403 em 22/10/2026 — não lida** |
| Plugins in ChatGPT | https://help.openai.com/en/articles/20001256-plugins-in-chatgpt | só o resumo da busca |
| Skills na API (formato do pacote) | https://developers.openai.com/api/docs/guides/tools-skills | resumo da busca |
| Skills na API (cookbook) | https://developers.openai.com/cookbook/examples/skills_in_api | resumo da busca |

## Fatos (fonte secundária, reconfirmar)

- API: pacote `.zip` com **uma única pasta de topo** e exatamente um `SKILL.md`; limite de 50 MB.
- Help Center (resumo de busca): ChatGPT web aceita upload de plugin em zip quando a opção existe; plugin pode incluir apps, skills ou os dois.

## Bloqueios

- Formato exato do upload de skill no app ChatGPT não confirmado: a tarefa do empacotador começa relendo a página oficial. Se continuar inacessível, avisar o professor em vez de presumir.
- Acesso ao Drive pelo ChatGPT depende das decisões em aberto D1 e D2 da spec.

## Reconsulta na Tarefa 38 (22/10/2026)

- A página oficial do Help Center continua com HTTP 403. O empacotador (`scripts/empacotar-chatgpt.py`) segue o formato da API (uma pasta de topo, um `SKILL.md`, até 50 MB). **Pendência:** confirmar com o professor, na matriz, se o app ChatGPT aceita esse zip no upload de skill; se não aceitar, ajustar o empacotador.
- Nos pacotes, o trecho "Como chamar o núcleo" é trocado por `scripts/trechos/chamar-nucleo-chatgpt.md` (o ChatGPT não acessa o computador do professor).
