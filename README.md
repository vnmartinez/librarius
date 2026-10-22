# Librarius

Assistente de IA para professores universitários. Ajuda a planejar o semestre, preparar aulas e provas e conferir a organização das pastas, **sem conhecimento de programação**: você conversa, o Librarius explica o que vai fazer e só grava depois do seu "sim".

O nome vem do *librarius* romano — o copista e escritor de livros.

## O que faz

- Responde "qual é a minha aula de hoje?" e "tem slide pronto?" a partir do cronograma.
- Importa o calendário da instituição e a planilha do cronograma, gera os encontros de cada turma e leva as aulas para a agenda.
- Distribui o programa da disciplina pelos encontros e refaz o plano quando uma aula é cancelada.
- Prepara o material da aula (roteiro, código de exemplo, lista de exercícios) e provas com gabarito, em versões diferentes.
- Confere carga horária, feriados, nomes de arquivos e materiais desatualizados. Essas conferências são feitas por programa, não por opinião da IA.

## Para quem

Professores do ensino superior, sem formação técnica. Tudo é dito em português simples.

## Privacidade

- **Fica no seu computador:** suas pastas, planilhas, o histórico do que foi alterado e o botão de desfazer.
- **Vai para o serviço de IA que você usa:** só o texto necessário para cada pedido, como o tema de uma aula ou a lista de datas.
- **Nunca é lido:** qualquer coisa de alunos (notas, trabalhos, pastas de TFC, relatórios, entregas). Esta versão não trabalha com dados de alunos.
- Nada é gravado sem a sua aprovação, nada é apagado (o que é substituído vai para uma pasta de arquivo) e tudo pode ser desfeito.

## Programas de IA suportados

Claude Code e aplicativo Claude (Cowork), Codex, Antigravity (aplicativo, editor e terminal), OpenCode e, de forma limitada (só conversar e redigir), ChatGPT. Veja [INSTALAR.md](INSTALAR.md).

## Estado do projeto

MVP em construção. O núcleo, as sete skills e os arquivos de instalação por programa estão prontos e conferidos por testes automáticos. Os slides saem no padrão visual da UniRV (os logotipos vêm do modelo que fica nas suas pastas, não deste repositório), e a instalação real em cada programa ainda será testada na matriz de verificação.

## Licença

MIT — veja [LICENSE](LICENSE).
