# Instalar o Librarius no OpenCode

Roteiro para o próprio assistente seguir, conversando com o professor em português simples. Faça uma etapa de cada vez e não mostre comandos nem caminhos longos ao professor.

## Etapa 1 — Baixar o Librarius

1. Pergunte ao professor em qual pasta do computador quer guardar o Librarius. Sugira `%USERPROFILE%\librarius` (no Windows) ou `~/librarius`. Nunca use a pasta do Google Drive nem a pasta dos materiais das disciplinas.
2. Baixe o projeto: `git clone https://github.com/vnmartinez/librarius <pasta>`. Se `git` não existir, ofereça instalar e só instale com o "sim" do professor; se ele preferir, baixe o arquivo zip do GitHub e extraia na mesma pasta.

## Etapa 2 — Deixar o OpenCode enxergar as skills

Escolha conforme a versão do OpenCode (`opencode --version`).

**Versão 2 (aceita a opção `skills`):** acrescente o caminho absoluto de `<pasta>/skills` à lista `skills` do arquivo `opencode.json` global (`~/.config/opencode/opencode.json`), sem apagar o que já existir lá.

**Versão estável (sem a opção `skills`):** crie um atalho de cada pasta de `<pasta>/skills/` em `~/.config/opencode/skills/<nome>`.
No Windows use junção, que não precisa de permissão especial: `mklink /J "%USERPROFILE%\.config\opencode\skills\<nome>" "<pasta>\skills\<nome>"`. Em outros sistemas use `ln -s`. Se não for possível criar atalhos, copie as pastas e avise o professor de que, a cada atualização, será preciso copiar de novo.

## Etapa 3 — Conferir

Rode `python <pasta>/scripts/acad.py ambiente verificar` (no Windows, se `python` não existir, tente `py -3`). Na primeira vez ele prepara o que precisa e pode demorar alguns minutos.

## Etapa 4 — Avisar o professor

Diga, em português simples, que terminou e como pedir ajuda: por exemplo, "O que você consegue fazer por mim?". Peça que abra uma conversa nova para as skills aparecerem.
