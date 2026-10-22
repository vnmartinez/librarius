# Plugin de IA para Professores Universitários — Prompt Inicial do Projeto

Oct 22, 2026 · @Vinicius

## 0. Instruções para o agente executor

Este documento é o prompt inicial do projeto `agente-academico`. Leia-o inteiro antes de criar qualquer arquivo.

Objetivo: um único repositório que produz um plugin instalável em Claude Code, Claude Cowork, Codex, Antigravity, Antigravity IDE, OpenCode e ChatGPT, tanto nas versões instaladas localmente quanto nas versões web/app, com as mesmas skills, a mesma CLI `acad` e o mesmo modelo de dados.

Regras obrigatórias:

1. Não inventar APIs, campos de manifesto ou caminhos de instalação. Antes de gerar cada adaptador, consultar a documentação oficial vigente da plataforma (seção Fontes) e registrar URL e data da consulta em `plataformas/<nome>/FONTE.md`. A tabela da seção 4 reflete o estado verificado em 22/10/2026 e pode ter mudado.
2. Nomes de skills, pastas, subcomandos e campos em português, minúsculos, sem acento, com hífen (seção 5).
3. Não criar, mover, renomear ou excluir nada em `G:\Meu Drive\Fasoft` sem confirmação explícita do professor. Testes usam cópias em `testes/amostras/`.
4. Não ler dados de alunos (lista de exclusão da seção 6).
5. Toda regra verificável é implementada em código e coberta por teste; o LLM não valida datas, carga horária, nomenclatura nem referências.
6. Uma decisão em aberto bloqueia apenas a parte que depende dela; o restante segue. Todo texto exibido ao professor segue a seção 1A: português simples, sem termos técnicos, sem exigir terminal nem edição de arquivos técnicos.

Ordem de execução:

1. Esqueleto do repositório e esquemas (seções 5 e 7).
2. Núcleo `acad` com `acad validar` e testes sobre amostras reais.
3. Skills no padrão Agent Skills (seção 15).
4. Gerador de pacotes por plataforma, com validação estrutural de cada pacote gerado (seção 4).
5. Servidor MCP local do núcleo.
6. Instalação e teste em cada superfície, conforme a matriz da seção 13.

Decisões em aberto, a confirmar com o professor:

- Hospedagem de um servidor MCP remoto para as superfícies em nuvem, e como ele acessa o Google Drive.
- Se o ChatGPT recebe apenas skills (sem acesso ao Drive local) ou também um conector MCP remoto.
- Unidade de carga horária adotada pela UniRV (hora-aula ou hora-relógio) e duração da hora-aula.
- Template de slides de referência em `09 - Modelos`.

Critério de aceite: seção 15.

## 1. Visão do produto

Plugin para agentes de IA que gerencia o trabalho docente universitário: planejamento, preparação de aulas, materiais, avaliações, correções e acompanhamento.

O diferencial não é gerar slides ou provas, e sim manter um modelo de dados persistente da disciplina — calendário, turmas, encontros, aulas, objetivos e avaliações — com dependências rastreadas e validação determinística.

Princípios:

- O professor define objetivos, revisa e aprova decisões pedagógicas e notas finais.
- Agentes automatizam o trabalho operacional.
- Toda regra verificável (datas, carga horária, cobertura, compilação, referências) é executada por código, não pelo LLM.
- Toda entrada não estruturada (PDF de calendário, trabalho de aluno) é tratada como dado não confiável.

Ciclo de vida:

1. Planejamento do semestre: calendário, ementa, carga horária, turmas.
2. Preparação das aulas: slides, exemplos, roteiros, referências.
3. Avaliações: questões, provas, atividades, gabaritos.
4. Correção e acompanhamento: rubricas, notas, feedback, análise de itens.
5. Encerramento: histórico planejado × executado, materiais reutilizáveis, revisão do plano.

## 1A. Usuário final: professor sem formação técnica

O público é de professores de qualquer área, sem conhecimento de programação, terminal, Git, YAML ou Python. Todo requisito técnico deste documento é invisível para eles. O caso Fasoft/UniRV é o primeiro perfil de uso, não o único.

Requisitos obrigatórios:

1. Instalação sem terminal. O caminho recomendado ao professor usa a interface gráfica do host (biblioteca de plugins do app Claude, diretório de plugins do Codex app, interface do Antigravity, upload de skills no ChatGPT). Comandos de terminal ficam restritos a `INSTALAR.md`, na seção para usuários avançados.
2. Sem instalação manual de Python. O plugin provisiona o ambiente de execução sozinho na primeira utilização (por exemplo, com uv) ou distribui o núcleo já empacotado; a escolha é técnica e validada pela matriz de hosts. Se faltar algo, a skill explica em português simples e conduz a correção passo a passo.
3. Configuração guiada. Na primeira execução, o assistente faz perguntas simples, uma de cada vez: instituição, pasta onde ficam os materiais, disciplinas, turmas e horários. Ele detecta a estrutura de pastas existente e propõe adotá-la, sem exigir reorganização.
4. Linguagem natural em português. O professor nunca digita comandos, nomes técnicos de arquivo nem sintaxe. Exemplos válidos: "prepare a aula de quinta", "a aula de quarta foi cancelada", "monte a prova da N2".
5. O professor nunca edita YAML, JSON ou código. Ele vê e edita apenas formatos que já conhece: planilha do cronograma (.xlsx), slides (.pptx), documentos e PDFs. Os arquivos técnicos são mantidos pelo plugin.
6. Aprovações em linguagem comum. Antes de gravar, o assistente mostra um resumo curto do que vai criar ou mudar ("vou criar 3 arquivos na pasta 02 - Aulas e atualizar o cronograma"), nunca diffs, hashes ou caminhos longos.
7. Nada se perde. O plugin não exclui arquivos do professor; substituições movem a versão anterior para `99 - Arquivo` (ou equivalente do perfil). Sempre existe "desfazer a última alteração".
8. Erros explicados. Mensagens de erro dizem, em português simples, o que aconteceu e o que fazer; detalhes técnicos ficam num registro para suporte.
9. Ajuda sempre disponível. "O que você sabe fazer?" e "como faço para...?" retornam respostas curtas com exemplos.
10. Privacidade explicada sem juridiquês: o que fica no computador, o que vai para o serviço de IA e o que nunca é lido.

Perfis institucionais: a estrutura de pastas, as regras de nomenclatura, as etapas de avaliação (N1, N2, N3) e os modelos são configuráveis por perfil. O perfil Fasoft (seção 6) vem pronto; outras instituições são criadas pela configuração guiada a partir das pastas que o professor já usa.

## 2. Módulos funcionais

### 2.1. Planejamento acadêmico

- Importar calendário institucional. ICS e XLSX: importação direta. PDF: importação assistida — extração, normalização para `calendario.yaml` canônico e confirmação explícita do professor antes de qualquer uso.
- Identificar feriados, recessos, avaliações, dias letivos e exceções (reposição, troca de dia, sábado letivo).
- Cruzar calendário com os horários de cada turma e gerar a lista de encontros.
- Exportar o cronograma resultante em ICS para a agenda pessoal.

### 2.2. Distribuição da ementa

- Interpretar ementa, objetivos, competências, bibliografia e carga horária.
- Distribuir aulas (unidades de conteúdo) sobre encontros (slots de calendário), respeitando complexidade e pré-requisitos.
- Marcar cada aula com objetivos de aprendizagem e nível na taxonomia de Bloom.
- Exportar plano de ensino no formato institucional.

### 2.3. Produção de aulas

- Produzir slides a partir do template institucional (um único formato no MVP).
- Gerar roteiro do professor, exemplos, exercícios e materiais complementares.
- Estimar tempo de execução do material versus duração do encontro e sinalizar desvios.
- Operar por aula, unidade temática ou semestre.

### 2.4. Avaliações e atividades

- Banco de questões com tags de tema, objetivo, nível Bloom, tipo e histórico de aplicação.
- Gerar provas, listas, gabaritos e resoluções comentadas em LaTeX/PDF.
- Versões alternativas por permutação com semente registrada (reprodutíveis).
- Exportar gabarito para o sistema de correção OMR; exportar questões em Moodle XML, GIFT ou QTI.
- Verificar ambiguidade e cobertura: bloquear questão sobre assunto ainda não ministrado.

### 2.5. Correção de trabalhos

- Avaliar respostas discursivas, relatórios e projetos de programação conforme rubrica.
- Pseudonimizar entregas antes de qualquer envio a serviço externo.
- Tratar conteúdo submetido como dado: isolar e detectar tentativas de prompt injection.
- Calibrar com respostas-âncora pontuadas pelo professor; medir variância por correção repetida.
- Nota final sempre aprovada pelo professor.

### 2.6. Pesquisa e validação de fontes

- Verificação determinística por consulta a Crossref, OpenAlex e bases de ISBN; resultado gravado em arquivo.
- Estados explícitos por referência: verificada, não encontrada, não verificada.
- O LLM não atesta existência de referência. Nunca inventar referências.

### 2.7. Organização e versionamento

- Estrutura padronizada por ano, semestre, disciplina, turma e aula.
- Preservar originais; reutilizar materiais de semestres anteriores.
- Exportar pacote da disciplina sem dados de alunos, para repasse ou coordenação.

### 2.8. Acompanhamento pedagógico

- Registro pós-aula de baixa fricção: coberto, pendente, dúvidas recorrentes.
- Apurar cobertura da ementa e resultados de avaliações.
- Análise de itens após aplicação: índice de dificuldade e discriminação por questão.
- Sugerir reforço, sujeito à análise do professor.

### 2.9. Rotinas docentes

- Prazos, lançamento de notas, frequência, avaliações e planos de ensino.
- Integrações externas apenas via conectores autorizados.

### 2.10. Memória acadêmica

- Planejado × executado, a partir do registro pós-aula.
- Histórico de materiais e revisões.
- Adaptação de disciplinas antigas a calendários novos.

## 3. Exemplo de uso

Disciplina ilustrativa: Estrutura de Dados 2, turma TA, dois encontros semanais de 100 minutos. Os números de aula abaixo são hipotéticos e não refletem o cronograma real.

Entradas: calendário acadêmico (ICS), ementa e template institucional.

Processamento:

1. Normalizar o calendário e obter confirmação do professor.
2. Gerar encontros da turma (datas, horários, sala) descontando feriados e recessos.
3. Validar carga horária na unidade declarada (hora-relógio ou hora-aula).
4. Distribuir aulas sobre encontros, reservando revisões e avaliações; obter aprovação.
5. Criar diretórios, plano de ensino e manifestos.
6. Gerar slides, códigos e exercícios por aula.
7. Registrar cada encontro como ministrado, com o conteúdo efetivamente coberto.
8. Gerar avaliações apenas sobre aulas com status ministrada ou planejada antes da data da prova.

Cronograma hipotético (aula = conteúdo; encontro = slot de calendário):

| Encontro | Aula | Tema | Artefatos |
| --- | --- | --- | --- |
| E01 | Aula 01 | Revisão de árvores binárias | slides, exercícios |
| E02 | Aula 02 | Árvores AVL | slides, implementação |
| E03 | Aula 03 | Rotações AVL | slides, prática |
| E04 | Aula 04 | Árvores B | slides, exemplos |
| E05–E06 | Aula 05 | Inserção em árvores B | slides, laboratório (2 encontros) |
| E07 | Aula 06 | Tabelas hash | slides, exercícios |

A relação encontro–aula é N:M: uma aula pode ocupar vários encontros e um encontro pode cobrir mais de uma aula. Cancelar E04 desloca o mapeamento, não renomeia aulas nem invalida artefatos.

## 4. Arquitetura

O próprio repositório é o plugin. Os manifestos de cada plataforma ficam lado a lado na raiz e apontam para a mesma pasta `skills/`; a instalação é feita diretamente a partir do repositório GitHub, sem etapa de build obrigatória. É o padrão adotado por [obra/superpowers](https://github.com/obra/superpowers) e [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail). O único artefato gerado é o zip de skills para o ChatGPT.

O conteúdo é idêntico em todas as plataformas: skills no padrão aberto Agent Skills (`SKILL.md`), a CLI Python `acad` e um servidor MCP com as mesmas operações. Skills são finas e chamam o núcleo; a lógica fica no código.

Superfícies-alvo e mecanismo de distribuição (verificado em 22/10/2026; reconfirmar na implementação):

| Superfície | Execução | Mecanismo | Arquivo na raiz do repositório |
| --- | --- | --- | --- |
| Claude Code | local (terminal, IDE, desktop) | Plugin instalado por marketplace; carrega skills, comandos, subagentes, hooks e MCP | `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` |
| Claude Cowork / app Claude | app e nuvem | Mesmo formato do Claude Code; carrega um subconjunto dos componentes; instalação pela biblioteca de plugins ou upload de zip | mesmos arquivos acima |
| Codex (app, CLI, extensão IDE) | local e app | Plugin instalado por marketplace; skills em `.agents/skills` | `.codex-plugin/plugin.json` + `.agents/plugins/marketplace.json` |
| Antigravity 2.0 (app) | local | Plugin com `plugin.json`; instalação pela interface | `plugin.json` (conferir: superpowers usa `.antigravity-plugin/`) |
| Antigravity IDE | local | Plugins em `.agents/plugins/` do projeto ou globais; skills em `.agents/skills` | mesmo manifesto Antigravity |
| Antigravity CLI | local | `agy plugin install` com a URL do repositório GitHub | mesmo manifesto Antigravity |
| OpenCode (TUI, desktop, extensão IDE) | local | Sem marketplace de plugins no formato dos demais. Skills lidas de `.opencode/skills`, com compatibilidade para `.agents/skills` e `.claude/skills`, ou de caminhos e URLs listados em `skills` no `opencode.json`; MCP declarado em `mcp`; lê `AGENTS.md`; plugins nativos são módulos JS/TS em `.opencode/plugins` ou pacotes npm | `opencode.json` de exemplo + `.opencode/INSTALAR.md`, instruções que o próprio agente segue, como no superpowers |
| ChatGPT | nuvem | Skills no padrão Agent Skills por upload; nenhum formato de plugin equivalente verificado | `dist/chatgpt/<skill>.zip`, gerado por script |

Camadas:

- `skills/`: fonte única das skills, lida por todos os manifestos.
- Skill de entrada `usando-agente-academico`: apresenta as demais skills e quando usar cada uma, como o `using-superpowers`. É injetada no início da sessão por hook onde houver suporte; nos demais hosts, sua descrição leva o modelo a carregá-la.
- `AGENTS.md` na raiz: versão compacta das regras para hosts que só leem arquivo de instruções, como no ponytail.
- Núcleo `acad` (Python): esquemas, validação, encontros, distribuição, manifestos, compilação, exportadores. As skills chamam `acad` pelo caminho de instalação do plugin, resolvido por host, e verificam Python e dependências antes do primeiro uso.
- Servidor MCP (`acad mcp`): mesmas operações como ferramentas, local (stdio) e, opcionalmente, remoto.
- `scripts/sincronizar-versao`: mantém a mesma versão em todos os manifestos, como o `.version-bump.json` do superpowers.
- `INSTALAR.md`: instruções de instalação por host.
- Hooks e subagentes são opcionais por host; nenhuma função depende deles.

Comandos ilustrativos do núcleo:

```
acad iniciar 2026-2
acad calendario importar calendario.ics
acad calendario confirmar
acad encontros gerar ED2 --turma TA
acad plano distribuir ED2
acad validar ED2
acad gerar ED2 --aula 03
acad exportar ics ED2
```

Acesso aos dados por tipo de superfície:

- Local (Claude Code, Codex CLI/app/IDE, Antigravity app/IDE/CLI, OpenCode, app Claude com pasta conectada): lê e grava `G:\Meu Drive\Fasoft` diretamente e executa `acad` com o Python da máquina.
- Nuvem (ChatGPT, Claude web, execuções em nuvem do Codex): não acessa o disco local. Opera por conector do Google Drive ou por servidor MCP remoto; a forma depende das decisões em aberto da seção 0.
- Em ambos os casos, o núcleo grava somente após confirmação do professor e respeita a lista de exclusão de dados de alunos.

Diferença em relação aos exemplos: superpowers e ponytail são quase só prompts; este projeto depende de Python e de acesso ao sistema de arquivos. A matriz de testes da seção 13 confirma, por host, que a skill encontra o `acad`, que o Python está disponível e que a leitura do Drive funciona.

## 5. Estrutura do repositório

A raiz do repositório é o plugin instalável em todos os hosts. O repositório fica fora do Google Drive; a pasta `G:\Meu Drive\Fasoft` recebe o plugin pela instalação de cada host, e não por cópia manual. A skill `cronograma` existente é absorvida pelo `planejador-semestre` como comando de consulta, eliminando as cópias paralelas atuais em `.agents` e `.claude`.

Nomes de skills, pastas e subcomandos ficam em português, minúsculos, sem acento e com hífen, para evitar problemas de codificação em caminhos e na CLI. Ficam em inglês apenas os nomes exigidos pelos hosts: `SKILL.md`, `skills/`, `plugin.json`, `marketplace.json`, as pastas de manifesto (`.claude-plugin`, `.codex-plugin`, `.agents`), `AGENTS.md`, `README.md` e o sufixo `.schema.json`.

```
agente-academico/
├── .claude-plugin/
│   ├── plugin.json                # Claude Code e Claude Cowork
│   └── marketplace.json
├── .codex-plugin/
│   └── plugin.json                # Codex app, CLI e IDE
├── .agents/
│   └── plugins/
│       └── marketplace.json       # marketplace Codex
├── plugin.json                    # Antigravity (local exato a confirmar)
├── .opencode/
│   └── INSTALAR.md                # roteiro que o OpenCode segue para instalar
├── opencode.json                  # exemplo: skills + servidor MCP para OpenCode
├── AGENTS.md                      # regras compactas para hosts só de instruções
├── INSTALAR.md                    # instalação por host
├── README.md
├── skills/
│   ├── usando-agente-academico/SKILL.md   # skill de entrada
│   ├── organizador-academico/SKILL.md
│   ├── planejador-semestre/SKILL.md
│   ├── distribuidor-ementa/SKILL.md
│   ├── gerador-aulas/SKILL.md
│   ├── gerador-avaliacoes/SKILL.md
│   ├── validador-academico/SKILL.md
│   ├── verificador-fontes/SKILL.md        # v2
│   ├── assistente-correcao/SKILL.md       # v2
│   └── revisao-semestre/SKILL.md          # v3
├── comandos/                      # comandos de barra, onde o host suporta
├── agentes/                       # subagentes, v2+
│   ├── pesquisador-conteudo.md
│   ├── autor-materiais.md
│   ├── revisor-pedagogico.md
│   └── revisor-correcao.md
├── hooks/                         # injeção da skill de entrada, onde suportado
├── acad/                          # núcleo Python (CLI + biblioteca + MCP)
│   ├── cli.py
│   ├── mcp.py
│   ├── calendario/
│   ├── encontros/
│   ├── planejamento/
│   ├── geracao/
│   ├── fontes/
│   ├── exportadores/
│   └── validacao/
├── esquemas/
│   ├── semestre.schema.json
│   ├── calendario.schema.json
│   ├── disciplina.schema.json
│   ├── turma.schema.json
│   ├── encontro.schema.json
│   ├── aula.schema.json
│   ├── questao.schema.json
│   ├── avaliacao.schema.json
│   └── manifesto.schema.json
├── modelos/
│   ├── slides/
│   ├── provas/
│   ├── atividades/
│   ├── planos-de-aula/
│   └── feedback/
├── scripts/
│   ├── sincronizar-versao         # mesma versão em todos os manifestos
│   ├── empacotar-chatgpt          # gera dist/chatgpt/<skill>.zip
│   └── validar-manifestos         # validação estrutural por host
├── testes/
│   ├── amostras/                  # calendários e programas reais anonimizados
│   ├── esperados/                 # cronogramas de referência
│   └── hosts/                     # roteiro da matriz de instalação por host
└── pyproject.toml
```

Responsabilidades:

- Manifestos: um por host, todos apontando para `skills/`; nenhum duplica conteúdo.
- Skills: quando chamar o núcleo e como conduzir a aprovação do professor.
- Núcleo `acad`: toda operação determinística e toda validação; também exposto como servidor MCP.
- Hooks e subagentes: opcionais por host.
- Esquemas: contrato único entre núcleo, skills e hosts.
- Scripts: versão, empacotamento do ChatGPT e validação dos manifestos.

## 6. Workspace do professor (G:\\Meu Drive\\Fasoft)

O plugin adota a estrutura existente em vez de impor uma nova. As regras de `AGENTS.md` (prefixo ` NN -  `, ` Aula XX -  `, ` Lista XX -  `, sem sufixos de versão, obsoletos em `99 - Arquivo/`) e do `README.md` do semestre passam a ser regras de validação do núcleo. Os dados estruturados do plugin entram como arquivos novos nas pastas já existentes; nenhuma pasta é renomeada.

Estrutura atual, com os acréscimos propostos marcados com `+`:

```
G:\Meu Drive\Fasoft\
├── AGENTS.md                          # regras de nomenclatura (já existe)
├── .agents\
│   ├── rules\ordem-numerica.md
│   └── skills\cronograma\             # skill + scripts\verificar_cronograma.py
├── .claude\
│   ├── commands\cronograma.md
│   └── skills\cronograma\             # cópia paralela da skill
├── .codex\tmp\
├── Documentos\
├── + Banco de Questões\               # proposto: questões reutilizáveis entre semestres
│   └── [Disciplina]\questoes.yaml
└── 2026\
    └── Segundo Semestre\
        ├── README.md                  # padrão do semestre
        ├── 2026 - Notas N1            # planilha Google (dado de aluno)
        ├── 2026 - NOTAS N2            # planilha Google (dado de aluno)
        ├── 00 - Administração Acadêmica\
        │   ├── Horários Docentes 2026-02.pdf
        │   ├── Ficha Carga Horária - 2026-2.*
        │   ├── Matriz Curricular - Engenharia de Software.pdf
        │   └── + calendario.yaml      # calendário canônico confirmado
        ├── 01 - Lógica Aplicada à Computação - 3º Período\
        ├── 02 - Segurança de Software - 3º Período\
        ├── 03 - Estrutura de Dados 1 - 4º Período\
        ├── 04 - Estrutura de Dados 2 - 5º Período\
        │   ├── 01 - Planejamento\
        │   │   ├── Programa de Disciplina - Estrutura de Dados 2.pdf
        │   │   ├── Cronograma - Estrutura de Dados 2.xlsx
        │   │   ├── + disciplina.yaml
        │   │   ├── + turma-TA.yaml
        │   │   ├── + encontros-TA.yaml   # gerado pelo núcleo
        │   │   └── + aulas.yaml          # status e manifesto por aula
        │   ├── 02 - Aulas\
        │   │   ├── Aula XX - Tema.pptx
        │   │   ├── Aula XX - Roteiro de Aula - Tema.md
        │   │   └── _ferramentas\
        │   ├── 03 - Atividades e Listas\     # Lista XX - / Atividade XX -
        │   ├── 04 - Projetos e Entregáveis\
        │   ├── 05 - Materiais de Referência\
        │   │   └── + referencias.yaml     # status de verificação
        │   ├── 06 - Código e Exemplos\       # aula-XX-*
        │   └── 99 - Arquivo\
        ├── 05 - Interface Humano-Computador - 5º Período\
        ├── 06 - Gerenciamento de Redes - Turma Especial\
        ├── 07 - TFC 1\
        │   └── 02 - Alunos\[Nome do aluno]\  # dado de aluno
        ├── 08 - Avaliações\
        │   ├── N1\  N2\  N3\
        │   └── Ata de prova\
        ├── 09 - Modelos\                  # templates de prova, cabeçalhos, LaTeX
        ├── 10 - Estágio\
        └── 11-Relatórios\
```

Regras de mapeamento:

- Avaliações ficam centralizadas em `08 - Avaliações/N1|N2|N3`, nunca dentro da disciplina, com o nome `[Disciplina] - N1 - [descrição] - [turma/versão]` e `- Gabarito` quando aplicável.
- O identificador da aula é o prefixo `Aula XX` (dois dígitos), já usado pela skill cronograma e pelo `.xlsx` de cada disciplina.
- `Cronograma - [Disciplina].xlsx` continua sendo a visão editável pelo professor. Na transição, o núcleo importa o `.xlsx` para `encontros-TA.yaml` e `aulas.yaml`; depois, o `.xlsx` passa a ser regenerado a partir dos YAML.
- Templates de slides e provas são lidos de `09 - Modelos`.
- Dados de alunos (planilhas `Notas`, `07 - TFC 1/02 - Alunos`, `11-Relatórios`, entregas em `04 - Projetos e Entregáveis`) entram numa lista de exclusão: o agente só os lê com pedido explícito, e sempre pseudonimizados antes de envio a serviço externo.
- O workspace fica no Google Drive, sem Git. O código do plugin fica num repositório fora do Drive (seção 5): sincronização do Drive sobre `.git` é fonte conhecida de conflito e corrupção.

Divergências encontradas na estrutura atual:

- `README.md` do semestre desatualizado: lista `06 - TFC 1`, `07 - Avaliações`, `08 - Modelos`; as pastas reais são `07 - TFC 1`, `08 - Avaliações`, `09 - Modelos`, e há `06 - Gerenciamento de Redes - Turma Especial`, `10 - Estágio` e `11-Relatórios` não documentadas.
- `11-Relatórios` viola o padrão ` NN -  ` (falta o espaço e o hífen separado).
- `Cronograma - Estrutura de Dados 2.xlsx.bak` em `01 - Planejamento`: obsoleto na pasta ativa, contra a regra 3 do `AGENTS.md`.
- `Recepção dos Calouros (1).xlsx`: sufixo de duplicata.
- `_ferramentas` em `02 - Aulas`: subpasta sem prefixo numérico.
- Acentuação inconsistente nos nomes de aula (`Aula 22 - Arvores B` versus `Aula 23 - Árvores B`); o núcleo precisa normalizar acentos ao casar tema e arquivo.
- Skill cronograma duplicada em `.agents/skills` e `.claude/skills`, e o `SKILL.md` aponta para o script em `.agents`: duas cópias tendem a divergir.

As divergências são relatadas pelo `acad validar`; nenhuma correção é aplicada sem confirmação, conforme a regra 5 do `README.md`.

## 7. Modelo de dados

Quatro entidades centrais: disciplina, turma, encontro e aula. Todos os arquivos ficam em 01 - Planejamento/ da disciplina. Valores abaixo são ilustrativos.

`disciplina.yaml`:

```
disciplina:
  codigo: ED2
  nome: Estrutura de Dados II
  semestre: "2026-2"
  carga_horaria:
    valor: 60
    unidade: hora_relogio        # hora_relogio | hora_aula
    minutos_hora_aula: null      # obrigatório se unidade = hora_aula (ex.: 50)
  objetivos:
    - id: OBJ-01
      descricao: Implementar árvores balanceadas
      bloom: aplicar
  configuracao:
    template_slides: institucional
    template_provas: latex-padrao
    idioma: pt-BR
  planejamento:
    status: rascunho             # rascunho | aprovado
    aprovado_em: null
```

`01 - Planejamento/turma-TA.yaml`:

```
turma:
  id: TA
  disciplina: ED2
  fuso: America/Sao_Paulo
  horarios:
    - dia_semana: 1              # ISO 8601: 1 = segunda
      inicio: "19:00"
      fim: "20:40"
      sala: B-204
    - dia_semana: 3
      inicio: "19:00"
      fim: "20:40"
      sala: B-204
  excecoes:
    - tipo: cancelamento
      data: 2026-10-12
      motivo: feriado
    - tipo: reposicao
      data: 2026-10-17
      inicio: "08:00"
      fim: "09:40"
      repoe: 2026-10-12
```

`01 - Planejamento/encontros-TA.yaml` (gerado pelo núcleo, não editado à mão):

```
encontros:
  - id: E01
    data: 2026-08-03
    inicio: "19:00"
    fim: "20:40"
    status: realizado            # previsto | realizado | cancelado
    aulas: [Aula 01]
    funcao: conteudo             # conteudo | revisao | avaliacao
```

`01 - Planejamento/aulas.yaml (entrada da Aula 03)`:

```
aula:
  id: Aula 03
  tema: Rotações AVL
  slides: "02 - Aulas/Aula 03 - Rotações AVL.pptx"
  roteiro: "02 - Aulas/Aula 03 - Roteiro de Aula - Rotações AVL.md"
  codigo: "06 - Código e Exemplos/aula-03-rotacoes-avl"
  objetivos: [OBJ-01]
  prerequisitos: [Aula 02]
  duracao_estimada_min: 100
  status: aprovada               # planejada | rascunho | revisada | aprovada | ministrada
  ministrada_em: []              # ids de encontros
```

Regras de validação:

- Carga horária dos encontros previstos incompatível com a exigida, na unidade declarada.
- Encontro sobre feriado ou recesso sem exceção registrada.
- Objetivo da ementa sem aula ou sem avaliação correspondente.
- Avaliação sobre aula não ministrada até a data da prova.
- Aula antes de seu pré-requisito.
- Artefato com hash de entrada divergente do manifesto (seção 8).

## 8. Dependências e ciclo de status

Cada artefato gerado tem um `manifesto.json` com o hash de todas as entradas. A validação recalcula os hashes e marca como desatualizado o que divergir, no modelo de um sistema de build. No Drive, os manifestos ficam agregados em 01 - Planejamento/aulas.yaml, sem arquivos extras em 02 - Aulas.

```
{
  "artefato": "02 - Aulas/Aula 03 - Rotações AVL.pptx",
  "gerado_em": "2026-10-20T14:02:00-03:00",
  "entradas": {
    "01 - Planejamento/aulas.yaml#Aula 03": "sha256:…",
    "09 - Modelos/[template de slides]": "sha256:…",
    "01 - Planejamento/Programa de Disciplina - Estrutura de Dados 2.pdf": "sha256:…"
  },
  "aprovado": true
}
```

Ciclo de status da aula:

1. planejada — existe no plano, sem material.
2. rascunho — material gerado.
3. revisada — revisão técnica e pedagógica concluída.
4. aprovada — professor aprovou; artefato imutável até revisão explícita.
5. ministrada — registro pós-aula gravado; alimenta cobertura e memória.

Mudança em entrada de artefato aprovado não o regera automaticamente: gera alerta e exige nova aprovação.

Replanejamento (cancelamento, reposição) produz um relatório de diff: aulas deslocadas, aulas comprimidas, avaliações que passaram a cobrir assunto não ministrado. O professor aprova o diff, não o cronograma inteiro.

## 9. Orquestração e custo

Execução sequencial é o caminho padrão e completo. Paralelismo por subagentes é otimização pós-MVP, com saída equivalente.

Fases:

1. Planejamento sequencial: normalizar calendário, gerar encontros, distribuir ementa, obter aprovação.
2. Produção: aulas em lotes; cada lote recebe contrato de entrada (aula.yaml + objetivos + template) e devolve contrato de saída (artefatos + manifesto).
3. Validação: `acad validar` (estrutura, carga, cobertura, compilação, referências), seguida de revisão pedagógica e aprovação docente.

Modos:

- Aula individual: preparação pontual, custo distribuído.
- Semestre completo: geração por lotes, custo concentrado.
- Híbrido (padrão recomendado): plano completo e rascunhos do semestre; refinamento próximo de cada aula.

Controle de custo:

- Orçamento de tokens por lote, com interrupção ao estourar.
- Contexto da disciplina (ementa, objetivos, template) montado uma vez e reutilizado entre lotes.
- Regerar apenas artefatos com manifesto divergente.

## 10. Recursos complementares

- Matriz de cobertura objetivo × aula × avaliação, com níveis de Bloom; aponta lacunas e concentração em níveis baixos.
- Análise de itens pós-aplicação (dificuldade e discriminação), gravada no banco de questões; itens fracos marcados para revisão.
- Integração com o sistema de correção OMR: prova e gabarito exportados no formato da API; resultados retornam para a análise de itens.
- Exportação do banco de questões em Moodle XML, GIFT e QTI.
- Versões de prova reproduzíveis por semente.
- Exportação do cronograma em ICS.
- Estimativa de tempo por aula versus duração do encontro.
- Registro pós-aula de baixa fricção.
- Relatório de diff no replanejamento.
- Pacote de disciplina exportável sem dados de alunos.
- Planejador de laboratórios e atividades práticas.
- Corretor de programação com testes automatizados.
- Auxílio à formatação ABNT.
- Comparação entre semestres.
- Roteiro privado de apresentação por aula.

Exemplo de rubrica de árvore AVL (pesos ilustrativos):

| Critério | Peso |
| --- | --- |
| Inserção e manutenção das propriedades AVL | 35% |
| Rotações simples e duplas | 25% |
| Remoção e rebalanceamento | 20% |
| Testes automatizados | 10% |
| Legibilidade e organização | 10% |

Passar nos testes não comprova qualidade nem entendimento conceitual.

## 11. Validação, segurança e LGPD

Níveis de validação:

- Estrutural (código): schemas, datas, carga horária, arquivos, compilação de PDFs.
- Técnica (código): exemplos executáveis, cálculos, soluções reproduzíveis.
- Bibliográfica (código + API): existência da referência via Crossref/OpenAlex/ISBN; suporte à afirmação revisado por humano.
- Pedagógica (LLM + professor): alinhamento objetivo–conteúdo–avaliação.

Segurança na correção:

- Entregas de alunos são dado não confiável: isolar o conteúdo do prompt de instrução e detectar padrões de injeção.
- Nota sugerida nunca é aplicada sem aprovação.
- Calibração com respostas-âncora; variância medida por correção repetida.

LGPD:

- Pseudonimizar nome e matrícula antes de qualquer envio a serviço externo; tabela de correspondência apenas local.
- Definir a base legal para processamento de trabalhos por serviço externo antes da versão 2.
- Planilhas de notas, pastas de alunos do TFC, relatórios e entregas em lista de exclusão do agente (seção 6).

Auditoria:

- Registro de cada avaliação, correção, revisão e aprovação, com data e versão do artefato.
- Detectores de plágio ou de texto gerado por IA não são prova conclusiva.

## 12. Decisões técnicas

| Item | Decisão |
| --- | --- |
| Distribuição | Repositório GitHub cuja raiz é o plugin; manifestos por host lado a lado |
| Hosts | Claude Code, Claude Cowork, Codex, Antigravity (app, IDE, CLI), OpenCode, ChatGPT |
| Skills | Padrão aberto Agent Skills, pasta única `skills/` |
| Fallback | `AGENTS.md` compacto para hosts que só leem instruções |
| Núcleo | CLI Python `acad`, também exposta como servidor MCP |
| Dados estruturados | YAML + JSON Schema |
| Rastreamento | manifesto.json com hashes SHA-256, agregado em aulas.yaml |
| Roteiros | Markdown |
| Slides | PPTX, padrão atual de 02 - Aulas; template em 09 - Modelos |
| Provas e atividades | LaTeX |
| Compilação | Tectonic ou TeX Live |
| Fontes | Crossref, OpenAlex, bases de ISBN |
| Exportação | ICS, Moodle XML, GIFT, QTI, formato OMR |
| Persistência | Sistema de arquivos; SQLite apenas como índice derivado |
| Versionamento | Git só no repositório do plugin, fora do Drive; workspace no Google Drive sem Git |
| Versão | Uma versão única, sincronizada em todos os manifestos por script |
| Paralelismo | Opcional, pós-MVP |
| Testes | Amostras reais anonimizadas, cronogramas esperados e matriz de instalação por host |

SQLite, se adotado, é índice reconstruível a partir dos arquivos, nunca fonte primária.

## 13. Roadmap

### MVP — Planejamento, materiais e instalação em todos os hosts

- [ ] Esquemas: disciplina, turma, encontro, aula, calendário, manifesto; regras de nomenclatura do AGENTS.md como validação.
- [ ] CLI `acad` com `validar`.
- [ ] Adotar a estrutura de G:\\Meu Drive\\Fasoft e a lista de exclusão de dados de alunos.
- [ ] Importar os Cronograma - \[Disciplina\].xlsx existentes e o calendário ICS/XLSX; gerar encontros por turma.
- [ ] Distribuir ementa sobre encontros, com aprovação.
- [ ] Gerar uma aula por template, com manifesto.
- [ ] Gerar prova em LaTeX/PDF com gabarito.
- [ ] Skill de entrada e `AGENTS.md` de fallback.
- [ ] Manifestos para Claude, Codex, Antigravity e OpenCode; zip de skills para ChatGPT; script de sincronização de versão.
- [ ] Servidor MCP local (stdio).
- [ ] Matriz de instalação aprovada em cada host local, pelo caminho sem terminal. Configuração guiada e perfil institucional configurável. Teste de uso com ao menos dois professores sem formação técnica, que instalam e preparam uma aula sem ajuda.
- [ ] Testes com amostras reais e cronogramas esperados.

### Versão 2 — Qualidade e correção

- [ ] Importação assistida de calendário em PDF.
- [ ] Verificação bibliográfica via API.
- [ ] Banco de questões com tags e exportação Moodle XML/GIFT/QTI.
- [ ] Integração com o sistema OMR e análise de itens.
- [ ] Correção por rubrica com pseudonimização, defesa contra injeção e calibração.
- [ ] Testes automatizados de trabalhos de programação.
- [ ] Subagentes para produção em lote.

### Versão 3 — Gestão acadêmica e portabilidade

- [ ] Servidor MCP remoto para hosts em nuvem, com acesso ao Google Drive.
- [ ] Integração com calendários, armazenamento e LMS via conectores autorizados.
- [ ] Registro pós-aula e planejado × executado.
- [ ] Comparação entre semestres e reutilização de materiais.
- [ ] Relatórios e alertas.

## 14. Comandos de exemplo

- Organize o semestre 2027-1 em G:\\Meu Drive\\Fasoft\\2027 a partir do calendário acadêmico e dos programas de disciplina.
- Importe o Cronograma - Estrutura de Dados 2.xlsx e valide carga horária e feriados.
- Distribua o programa de Estrutura de Dados 2 entre os encontros da turma TA.
- Prepare a Aula 24 de Estrutura de Dados 2: slides pelo modelo de 09 - Modelos, roteiro, exemplos em 06 - Código e Exemplos e uma lista em 03 - Atividades e Listas.
- Crie a avaliação N3 de Estrutura de Dados 2, turmas TA e TB, com gabarito, em 08 - Avaliações/N3.
- Verifique as referências de 05 - Materiais de Referência de Segurança de Software.
- A aula de quarta-feira foi cancelada: gere o diff do replanejamento.
- Aponte arquivos fora do padrão do AGENTS.md no Segundo Semestre.

## 15. Escopo inicial do MVP

Skill de entrada `usando-agente-academico` mais seis skills, todas em `skills/` e chamando a CLI `acad`:

1. organizador-academico: na primeira execução, conduz a configuração guiada da seção 1A e cria o perfil institucional; depois valida a estrutura contra AGENTS.md e README.md do semestre, cria pastas padrão de disciplina e relata divergências sem corrigir sem confirmação.
2. planejador-semestre: importa calendário e Cronograma - \[Disciplina\].xlsx, gera encontros por turma e responde consultas do tipo "aula de hoje" (absorve a skill cronograma).
3. distribuidor-ementa: distribui o Programa de Disciplina sobre os encontros e grava aulas.yaml.
4. gerador-aulas: gera Aula XX - Tema.pptx, roteiro .md, código em 06 - Código e Exemplos e lista em 03 - Atividades e Listas, com manifesto.
5. gerador-avaliacoes: gera avaliação e gabarito em 08 - Avaliações/NX no padrão de nome do semestre, a partir de 09 - Modelos.
6. validador-academico: carga horária, feriados, cobertura, pré-requisitos, nomenclatura, manifestos desatualizados.

Primeiro caso de uso completo: Estrutura de Dados 2 do semestre 2027-1, partindo do programa de disciplina e do calendário, até as primeiras quatro aulas com material gerado, validado e aprovado.

Critério de pronto do MVP: o `acad validar` roda sem LLM sobre o Segundo Semestre de 2026 atual e reproduz, por código, o que a skill cronograma informa hoje; e o plugin, instalado a partir do repositório, executa o mesmo comando de consulta em Claude Code, Claude Cowork, Codex, Antigravity (app, IDE e CLI) e OpenCode, e as skills carregam no ChatGPT. Um professor sem formação técnica instala o plugin, conclui a configuração guiada e obtém a primeira aula preparada sem usar terminal nem editar arquivo técnico.

## Fontes

Consultadas em 22/10/2026. Reconfirmar antes de implementar cada manifesto.

- [Codex — Agent Skills (OpenAI)](https://developers.openai.com/codex/skills.md)
- [Skills in ChatGPT (OpenAI Help Center)](https://help.openai.com/en/articles/20001066-skills-in-chatgpt)
- [Claude Code — Plugins](https://code.claude.com/docs/en/plugins/overview)
- [Antigravity — Plugins](https://antigravity.google/docs/plugins?tab=cli)
- [Antigravity CLI — Plugins & skills](https://www.antigravity.google/docs/cli/plugins)
- [OpenCode — Skills](https://opencode.ai/v2/docs/skills/)
- [Agent Skills — implementação em clientes](https://agentskills.io/client-implementation/adding-skills-support.md)
- [awesome-codex-plugins (estrutura de plugin Codex)](https://github.com/hashgraph-online/awesome-codex-plugins)
- [obra/superpowers](https://github.com/obra/superpowers)
- [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)
