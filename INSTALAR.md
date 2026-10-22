# Como instalar o Librarius

Escolha o programa de IA que você já usa. Em todos os casos o caminho mais simples é pedir para o próprio assistente instalar: abra uma conversa e escreva

> Instale o Librarius a partir de github.com/vnmartinez/librarius

O assistente vai explicar cada passo e pedir o seu "sim" antes de instalar qualquer coisa. Para funcionar, o computador precisa do Python 3.11 ou mais novo (gratuito); se faltar, o assistente avisa e ajuda a instalar.

## Claude Code

1. Abra o Claude Code.
2. Peça: "Instale o Librarius a partir de github.com/vnmartinez/librarius".
3. Abra uma conversa nova e pergunte: "O que você consegue fazer por mim?".

## Aplicativo Claude (Cowork)

Pelo aplicativo, adicione o Librarius como plugin, informando o endereço github.com/vnmartinez/librarius na tela de plugins (o nome exato do menu varia com a versão). Se não achar o menu, peça ao assistente a ajuda de instalação acima. Esta forma ainda será confirmada com o professor; o plugin foi montado sem a pasta que impede a instalação no aplicativo.

## Codex

1. Abra o Codex (aplicativo, terminal ou extensão do editor).
2. Peça: "Instale o Librarius a partir de github.com/vnmartinez/librarius".
3. Abra uma conversa nova e pergunte: "O que você consegue fazer por mim?".

## Antigravity (aplicativo, editor e terminal)

1. Abra o Antigravity.
2. Peça: "Instale o plugin Librarius a partir de github.com/vnmartinez/librarius".
3. Abra uma conversa nova e pergunte: "O que você consegue fazer por mim?".

## OpenCode

1. Abra o OpenCode.
2. Peça: "Siga o roteiro .opencode/INSTALAR.md do repositório github.com/vnmartinez/librarius para instalar o Librarius". O assistente pergunta em que pasta guardar o projeto, baixa tudo e conecta as skills.
3. Abra uma conversa nova e pergunte: "O que você consegue fazer por mim?".

## ChatGPT

No ChatGPT as skills funcionam só para conversar, planejar e redigir textos: ele não enxerga as pastas do seu computador. Para gravar arquivos e conferir datas, use um dos programas acima. Os arquivos das skills para enviar ao ChatGPT são gerados pelo desenvolvedor do projeto; peça-os a ele. O envio para o ChatGPT ainda será confirmado.

## Para usuários avançados

Comandos de terminal para quem prefere instalar por conta própria.

```text
claude plugin marketplace add vnmartinez/librarius
claude plugin install librarius@librarius

codex plugin marketplace add vnmartinez/librarius

agy plugin install https://github.com/vnmartinez/librarius
```

OpenCode: siga o roteiro em `.opencode/INSTALAR.md` (versão 2: opção `skills` no `opencode.json`; versão estável: junção das pastas em `~/.config/opencode/skills`).

ChatGPT: `python scripts/empacotar-chatgpt.py` gera um `.zip` por skill em `dist/chatgpt/`.

Conferir o núcleo sem agente: `python scripts/acad.py ambiente verificar`. Conferir os arquivos de instalação: `python scripts/validar-manifestos.py`.
