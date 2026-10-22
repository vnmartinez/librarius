---
name: gerador-aulas
description: "Prepara o material de uma aula: slides no modelo da instituição, roteiro do professor, código de exemplo e lista de exercícios, sempre com aprovação do professor antes de gravar. Use quando o professor pedir para preparar, revisar ou aprovar uma aula."
compatibility: "Precisa do assistente instalado no computador do professor e de Python 3.11 ou mais novo (o assistente ajuda a instalar)."
metadata:
  autor: "Vinicius Martinez"
  projeto: "librarius"
---

# Gerador aulas

## Quando usar

- O professor pede para preparar a aula de um dia ou de um tema.
- Ele quer revisar ou aprovar uma aula já preparada.
- Ele pergunta em que situação está o material de uma aula.

## Como conversar com o professor

- Uma pergunta por vez, em português simples e sem termos técnicos.
- Antes de gravar, diga em uma ou duas frases o que vai acontecer ("vou criar 3 arquivos na pasta 02 - Aulas e atualizar o cronograma") e espere o "sim".
- Nunca mostre caminhos longos, código ou arquivos técnicos.
- Se algo der errado, explique o que houve e o que fazer em seguida.
- As decisões pedagógicas e as notas são sempre do professor.

## Passo a passo

1. Confirme a aula e o tema com o professor.
2. Escreva o conteúdo (roteiro, exemplos, lista) numa pasta temporária fora dos materiais do professor, seguindo o formato que o núcleo pede.
3. Rode `acad gerar aula` com `--aula` e `--conteudo`; mostre o resumo e, com o "sim", aplique com `acad aplicar`.
4. Mudar a situação da aula para revisada ou aprovada: `acad aula status`, somente quando o professor disser.
5. Se a resposta avisar que os slides ficam para depois, diga isso ao professor e siga com o restante.

## Exemplos de pedidos

- Prepare a aula de quinta.
- Gere o roteiro e a lista de exercícios da aula 7.
- Considero a aula 5 revisada.
- Aprovo a aula de ontem.
- Quais aulas ainda não têm material?

<!-- inicio:chamar-nucleo -->
## Como chamar o núcleo

1. Raiz do plugin: `${CLAUDE_PLUGIN_ROOT}`. Se o texto anterior não virou um caminho de pasta, a raiz é a pasta dois níveis acima deste `SKILL.md`.
2. Antes do primeiro uso na conversa, rode `python "<raiz>/scripts/acad.py" ambiente verificar --json` (no Windows, se `python` não existir, tente `py -3`). Se nenhum dos dois existir, explique ao professor que falta um programa gratuito chamado Python, ofereça instalar e só instale com o "sim" dele.
3. Rode sempre `python "<raiz>/scripts/acad.py" <comando> --json` e leia a resposta: mostre ao professor apenas o campo `mensagem` e os `avisos`, com suas palavras, em português simples. Nunca mostre caminhos longos, códigos, nomes de arquivo técnicos nem o conteúdo bruto da resposta.
4. Se a resposta trouxer `proposta`, mostre o `resumo` em uma ou duas frases e pergunte se pode continuar. Só depois de um "sim" claro, rode `acad aplicar <id>`. Para voltar atrás: `acad desfazer`.
5. Saída 3: falta algo no computador — explique e ofereça ajuda. Saída 4: falta uma decisão do professor — diga qual e siga com o resto.
6. Sem acesso ao computador do professor (ChatGPT ou versão web): diga que essa parte precisa do assistente instalado no computador e pare.
7. Arquivos de alunos (notas, pastas de TFC, relatórios, entregas) nunca são abertos, nem se pedirem de passagem; se o professor pedir de forma explícita, explique que esta versão não trabalha com dados de alunos.
<!-- fim:chamar-nucleo -->
