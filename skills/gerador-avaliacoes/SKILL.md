---
name: gerador-avaliacoes
description: "Monta provas e atividades com gabarito no modelo da instituição, só com conteúdo já dado até a data da prova, e gera versões diferentes de forma reproduzível. Use quando o professor pedir uma prova, avaliação N1/N2/N3, simulado ou gabarito."
compatibility: "Precisa do assistente instalado no computador do professor e de Python 3.11 ou mais novo (o assistente ajuda a instalar)."
metadata:
  autor: "Vinicius Martinez"
  projeto: "librarius"
---

# Gerador avaliacoes

## Quando usar

- O professor pede a prova da N1, N2 ou N3.
- Ele quer um simulado ou lista avaliativa.
- Ele precisa de versões diferentes da mesma prova e do gabarito.

## Como conversar com o professor

- Uma pergunta por vez, em português simples e sem termos técnicos.
- Antes de gravar, diga em uma ou duas frases o que vai acontecer ("vou criar 3 arquivos na pasta 02 - Aulas e atualizar o cronograma") e espere o "sim".
- Nunca mostre caminhos longos, código ou arquivos técnicos.
- Se algo der errado, explique o que houve e o que fazer em seguida.
- As decisões pedagógicas e as notas são sempre do professor.

## Passo a passo

1. Confirme etapa, turma, data da prova e o conteúdo coberto.
2. Escreva as questões no formato que o núcleo pede, numa pasta temporária fora dos materiais.
3. Rode `acad gerar avaliacao`; indique quantas versões o professor quer.
4. Se o núcleo recusar por haver aula ainda não dada, explique e proponha ajustar a cobertura.
5. Mostre o resumo e aplique com `acad aplicar` somente com o "sim". A nota final é sempre do professor.

## Exemplos de pedidos

- Monte a prova da N2 de Estruturas de Dados.
- Preciso de 3 versões da prova com gabarito.
- Faça um simulado só com o que já dei.
- Gere o gabarito da N1.

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
