# Organização do Segundo Semestre

Este documento define a estrutura padrão de pastas do segundo semestre de 2026.

## Estrutura principal

```text
Segundo Semestre/
├── 00 - Administração Acadêmica/
├── 01 - Lógica Aplicada à Computação - 3º Período/
├── 02 - Segurança de Software - 3º Período/
├── 03 - Estrutura de Dados 1 - 4º Período/
├── 04 - Estrutura de Dados 2 - 5º Período/
├── 05 - Interface Humano-Computador - 5º Período/
├── 06 - TFC 1/
├── 07 - Avaliações/
└── 08 - Modelos/
```

Os prefixos numéricos mantêm a ordem visual das disciplinas e das áreas no Explorador de Arquivos.

## Estrutura padrão das disciplinas

Cada disciplina deve conter as mesmas categorias principais:

```text
[Disciplina]/
├── 01 - Planejamento/
├── 02 - Aulas/
├── 03 - Atividades e Listas/
├── 04 - Projetos e Entregáveis/
├── 05 - Materiais de Referência/
├── 06 - Código e Exemplos/
└── 99 - Arquivo/
```

### Finalidade das categorias

- **01 - Planejamento**: programa da disciplina, cronogramas e documentos de organização.
- **02 - Aulas**: slides, roteiros, resumos e materiais utilizados nas aulas.
- **03 - Atividades e Listas**: exercícios, listas, atividades e gabaritos que não sejam avaliações formais.
- **04 - Projetos e Entregáveis**: trabalhos, projetos, instruções, modelos e documentos de entrega.
- **05 - Materiais de Referência**: livros, capítulos, artigos e leituras complementares.
- **06 - Código e Exemplos**: código-fonte, projetos de programação e exemplos práticos.
- **99 - Arquivo**: versões antigas, duplicatas, materiais históricos ou itens cuja classificação ainda não foi definida.

As pastas que não tiverem conteúdo devem ser mantidas para que todas as disciplinas conservem o mesmo padrão.

## Avaliações

Todas as avaliações ficam centralizadas, fora das pastas das disciplinas:

```text
07 - Avaliações/
├── N1/
├── N2/
└── N3/
```

Não devem ser criadas pastas de avaliações dentro das disciplinas.

Os nomes dos arquivos de avaliação devem começar pelo nome da disciplina e identificar a etapa, a turma, a versão e o gabarito quando aplicável:

```text
[Disciplina] - N1 - [descrição] - [turma/versão].extensão
[Disciplina] - N1 - [descrição] - Gabarito.extensão
```

Exemplos:

```text
Estrutura de Dados 1 - N1 - Avaliação - TA.docx
Estrutura de Dados 1 - N1 - Avaliação - TA - Gabarito.docx
Interface Humano-Computador - N2 - Avaliação - TB.pdf
```

Avaliações antigas devem permanecer na pasta correspondente à sua etapa, preservando no nome o ano, a turma e a versão original.

## Administração acadêmica

`00 - Administração Acadêmica` reúne documentos gerais do semestre, como matriz curricular e horários docentes.

## TFC 1

```text
06 - TFC 1/
├── 01 - Orientações e Modelos/
├── 02 - Alunos/
│   └── [Nome do aluno]/
├── 03 - Entregas/
└── 04 - Referências/
```

Cada aluno deve ter uma pasta própria dentro de `02 - Alunos`.

## Modelos

`08 - Modelos` reúne modelos reutilizáveis de provas, cabeçalhos e documentos LaTeX. Esses arquivos não pertencem a uma disciplina específica.

## Regras gerais

1. Não alterar o conteúdo dos documentos ao reorganizá-los.
2. Preferir mover arquivos para a categoria correta em vez de duplicá-los.
3. Manter versões, anos, turmas e gabaritos identificáveis no nome do arquivo.
4. Usar `99 - Arquivo` quando a classificação não puder ser determinada com segurança.
5. Não remover materiais antigos sem confirmação; eles devem ser arquivados.
6. Sempre seguir ordem numérica com prefixo de dois dígitos em todos os arquivos de aulas (`Aula 01 - ...`, `Aula 15 - ...`), listas (`Lista 01 - ...`) e pastas.
7. Não manter versões soltas duplicadas (como `(Revisado)` ou arquivos sem número); arquivos revisados assumem o nome oficial numerado e versões obsoletas anteriores são descartadas imediatamente.
