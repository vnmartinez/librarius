---
name: validador-academico
description: "Confere, sem depender de opinião da IA, carga horária, feriados, cobertura dos objetivos, pré-requisitos, nomes de arquivos e materiais desatualizados, e explica cada problema em linguagem simples. Use quando o professor pedir para conferir, revisar ou validar o semestre ou uma disciplina."
compatibility: "Precisa do assistente instalado no computador do professor e de Python 3.11 ou mais novo (o assistente ajuda a instalar)."
metadata:
  autor: "Vinicius Martinez"
  projeto: "librarius"
---

# Validador academico

## Quando usar

- O professor pede para conferir ou validar o semestre ou uma disciplina.
- Ele quer saber se a carga horária fecha ou se há aula em feriado.
- Ele quer achar arquivos fora do padrão ou material desatualizado.

## Como conversar com o professor

- Uma pergunta por vez, em português simples e sem termos técnicos.
- Antes de gravar, diga em uma ou duas frases o que vai acontecer ("vou criar 3 arquivos na pasta 02 - Aulas e atualizar o cronograma") e espere o "sim".
- Nunca mostre caminhos longos, código ou arquivos técnicos.
- Se algo der errado, explique o que houve e o que fazer em seguida.
- As decisões pedagógicas e as notas são sempre do professor.

## Passo a passo

1. Rode `acad validar` (informe a disciplina quando ele pedir só uma).
2. Agrupe os achados por assunto e explique cada um em linguagem simples, dizendo o que fazer.
3. Ofereça corrigir só o que o professor escolher; cada correção vira uma proposta, aplicada com `acad aplicar` depois do "sim".
4. Lembre que as conferências são feitas pelo programa, não por opinião da IA.

## Exemplos de pedidos

- Confira o semestre inteiro.
- A carga horária de Redes fecha?
- Tem aula marcada em feriado?
- Quais materiais estão desatualizados?
- Valide só a disciplina de Banco de Dados.

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
