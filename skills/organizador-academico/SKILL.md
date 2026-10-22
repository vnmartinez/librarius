---
name: organizador-academico
description: "Configura o assistente na primeira vez (instituição, pasta dos materiais, disciplinas, turmas e horários) e confere a organização das pastas do semestre contra as regras de nomes. Use quando o professor começar a usar o assistente, pedir para organizar ou conferir pastas, ou perguntar quais arquivos estão fora do padrão."
compatibility: "Precisa do assistente instalado no computador do professor e de Python 3.11 ou mais novo (o assistente ajuda a instalar)."
metadata:
  autor: "Vinicius Martinez"
  projeto: "librarius"
---

# Organizador academico

## Quando usar

- Primeira vez que o professor usa o assistente.
- Novo semestre ou nova disciplina para cadastrar.
- O professor pede para organizar ou conferir as pastas.

## Como conversar com o professor

- Uma pergunta por vez, em português simples e sem termos técnicos.
- Antes de gravar, diga em uma ou duas frases o que vai acontecer ("vou criar 3 arquivos na pasta 02 - Aulas e atualizar o cronograma") e espere o "sim".
- Nunca mostre caminhos longos, código ou arquivos técnicos.
- Se algo der errado, explique o que houve e o que fazer em seguida.
- As decisões pedagógicas e as notas são sempre do professor.

## Passo a passo

1. Rode `acad perfil detectar` e mostre ao professor o que foi encontrado (instituição, pasta dos materiais). Confirme antes de seguir.
2. Com o "sim" dele, rode `acad iniciar` com a opção `--confirmar` para registrar o semestre.
3. Para cada disciplina, rode `acad disciplina criar`; depois `acad turma criar`, perguntando os horários um de cada vez.
4. Rode `acad disciplina estrutura`: ela devolve uma proposta com as subpastas padrão. Mostre o resumo e só aplique com o "sim".
5. Rode `acad validar` e conte as divergências em linguagem simples. Não corrija nada sem confirmação; cada correção vira uma proposta.

## Exemplos de pedidos

- Quero começar a usar o assistente.
- Cadastre minha disciplina nova de Banco de Dados.
- Quais arquivos estão fora do padrão neste semestre?
- Organize as pastas do semestre.

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
