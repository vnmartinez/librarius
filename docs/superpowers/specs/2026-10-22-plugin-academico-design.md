# Librarius — especificação técnica do MVP

Data: 22/10/2026 · Branch: `vnmartinez/plugin-academico-mvp` · Base: `main` @ `1ff814f`

Fonte de origem: `Plugin de IA para Professores Universitários — Brainstorming Revisado.md` (o "briefing"), na raiz do repositório. Esta spec não reabre o que o briefing resolve; ela fixa os contratos técnicos que o briefing deixa em aberto e registra o que foi verificado nos hosts e no Drive. Onde o briefing diz `agente-academico`, leia-se o repositório `librarius`.

Escopo: MVP completo do briefing (seções 5 a 13), na ordem da seção 0. Fora do escopo: itens marcados v2/v3 no roadmap (seção 13).

---

## 1. Decisões já tomadas (não reabrir)

| # | Decisão | Origem |
|---|---|---|
| T1 | Repositório `librarius` é o plugin; manifestos por host lado a lado na raiz; sem build obrigatório; único artefato gerado é o zip do ChatGPT | briefing §4, §12 |
| T2 | CLI `acad` em Python, também servidor MCP (`acad mcp`) | briefing §4, §12 |
| T3 | Skills no padrão Agent Skills em `skills/`, nomes da seção 15 (inclusive `usando-agente-academico`) | briefing §15; decisão 3 do professor |
| T4 | Dados estruturados em YAML validados por JSON Schema; manifestos com SHA-256 agregados em `aulas.yaml` | briefing §7, §8, §12 |
| T5 | Acesso a `G:\Meu Drive\Fasoft` neste ciclo: **somente leitura** e cópia de amostras para `testes/amostras/`. Nunca criar, mover, renomear ou excluir nada no Drive | decisão 2 do professor |
| T6 | Skill `cronograma` atual é absorvida por `planejador-semestre`; o script dela é o oráculo de comportamento | decisão 4 do professor; briefing §5 |
| T7 | Toda regra verificável é código com teste; o LLM nunca valida datas, carga, nomenclatura ou referências | briefing §0 regra 5 |
| T8 | Todo texto ao professor em português simples, sem exigir terminal nem edição de arquivo técnico | briefing §1A |

## 2. Decisões em aberto (seção 0 do briefing) e o que cada uma bloqueia

Regra: cada decisão bloqueia só a parte que depende dela; o resto segue.

| # | Decisão em aberto | Bloqueia | Não bloqueia | Padrão provisório |
|---|---|---|---|---|
| D1 | Hospedagem de servidor MCP remoto para superfícies em nuvem e como ele acessa o Google Drive | Qualquer acesso a dados do professor a partir de ChatGPT, Claude web e execuções em nuvem do Codex; item "servidor MCP remoto" (já é v3) | Todo o núcleo, MCP local stdio, todos os hosts locais, zip de skills do ChatGPT | Skills, em superfície sem disco local, dizem em português simples que precisam do computador do professor e param |
| D2 | ChatGPT recebe só skills ou também conector MCP remoto | Conector MCP no ChatGPT; teste de leitura do Drive no ChatGPT na matriz | Empacotador `dist/chatgpt/<skill>.zip` e teste "skills carregam no ChatGPT" (critério de pronto §15) | Só skills |
| D3 | Unidade de carga horária da UniRV (hora-aula ou hora-relógio) e duração da hora-aula | Valor padrão de `carga_horaria.unidade` e `minutos_hora_aula` no perfil Fasoft; veredito final da regra `carga-horaria-incompativel` sobre dados reais | Cálculo nas duas unidades, esquema, testes com amostras sintéticas, todas as outras regras | Perfil Fasoft sai com `unidade: null`; o validador emite `carga-unidade-nao-confirmada` (aviso) em vez de julgar |
| D4 | Template de slides de referência em `09 - Modelos` | Gerador de `.pptx` (tarefa marcada BLOQUEADA no plano) e o teste de aceite "primeira aula com slides" | Roteiro `.md`, código em `06 - Código e Exemplos`, lista em `03 - Atividades e Listas`, manifesto, prova LaTeX | Candidato encontrado (ver §2.1). Interface `GeradorSlides` existe desde já com implementação de teste |

### 2.1 Achado relevante para D4

`09 - Modelos/Modelo de Slides UniRV/` contém uma especificação visual completa (`Padrao Visual de Slides - UniRV Fasoft.md`), a biblioteca `unirv-slides.js` (Node + `pptxgenjs`, 16:9, 10 × 5,625 pol., paleta com tokens `green 015537` etc.), decks de aula como scripts `deck-aula-NN.js` e renderizações de referência. A regra do documento é: o deck é gerado por script, nunca editado à mão.

Opções a apresentar ao professor (recomendação primeiro):

1. **Reimplementar o Padrão Visual em Python com `python-pptx`** (recomendado): um só runtime (o mesmo do `acad`), sem Node na máquina do professor, mesmo resultado visual conferido contra `referencia/*.png`.
2. Chamar `node` com `unirv-slides.js`: reaproveita o código, mas exige Node e `npm i pptxgenjs` em cada máquina, o que conflita com §1A.2.

### 2.2 Interpretações registradas (não são decisões novas)

- Plugin e marketplaces se chamam `librarius`; a skill de entrada mantém o nome `usando-agente-academico` (seção 15). Se o professor quiser `usando-librarius`, é troca de nome de pasta + `name`, coberta por teste.
- O README do semestre está desatualizado (lista `06 - TFC 1`, `07 - Avaliações`, `08 - Modelos`). O perfil Fasoft usa as pastas reais detectadas (`08 - Avaliações`, `09 - Modelos`) e o validador relata a divergência (`readme-desatualizado`).
- Python: módulos usam `_` (exigência da linguagem), como os nomes em inglês exigidos pelos hosts (§5 do briefing). Pastas, subcomandos, campos YAML, códigos de achado e nomes de skill usam hífen.
- Calendário acadêmico institucional não está em `00 - Administração Acadêmica` (só horários, ficha de carga, matriz). Testes de calendário usam amostras sintéticas; o calendário real entra pela importação assistida com o professor.

## 3. Estado verificado

### 3.1 Repositório

`README.md` (descreve um escopo anterior: "público que já usa agentes de código" — será reescrito), `LICENSE` (MIT), `.gitignore` (perfil Node), briefing. Repositório **público** no GitHub: nada com dado de aluno, logotipo institucional ou material didático completo entra no Git.

### 3.2 Ambiente desta máquina

Windows 11; `python` 3.14.7 e `py` 3.14; `git`; `uv` **ausente**; agentes `claude`, `codex`, `agy`, `opencode`; `openpyxl` 3.1.5 já instalado no Python global.

### 3.3 Drive (lido em modo somente leitura)

- `AGENTS.md` e `.agents/rules/ordem-numerica.md`: prefixos `Aula XX - ` em `02 - Aulas`, `Lista XX - ` / `Atividade XX - ` em `03 - Atividades e Listas`, pastas `NN - `; proibidos sufixos `(Revisado)`, `_v2`, `- copia`; obsoletos para `99 - Arquivo/`.
- Skill `cronograma` (`.agents/skills/cronograma/SKILL.md` + `scripts/verificar_cronograma.py`, 340 linhas). Comportamento: sobe diretórios até achar `AGENTS.md` contendo "Fasoft"; varre `**/*Cronograma*.xlsx` fora de `99 - Arquivo` e sem `~$`; na planilha ativa, linhas 1–149, colunas 1–6, procura a data alvo (aceita `datetime`, `dd/mm/aaaa`, `aaaa-mm-dd`, `dd/mm`); lê semana (col. 2), aula (col. 4, senão 3), tópico (col. 5); extrai `Aula NN`; classifica feriado/recesso/SETECH/sem aula e avaliação/prova por palavra-chave; procura materiais: slides (`.pptx .ppt .pdf .key .odp`) e roteiros (`.md .docx .doc .txt`) com `Aula NN` no nome, slides "divergentes" por ≥2 palavras-chave do tópico (≥4 letras, sem acento, sem stopwords), atividades com `Aula NN` ou ≥2 palavras-chave, códigos com `aula-NN`; saída texto ou `--json`.
- `Cronograma - Estrutura de Dados 2.xlsx`: aba única; linha 3 é cabeçalho (`Semanas`, `Datas`, `Aulas`, `Tópicos` em B–E); dados a partir da linha 4; uma linha por encontro; `Aula NN` numera encontros (ex.: `Aula 11` = `PRIMEIRA AVALIAÇÃO`).
- Divergências reais em ED2 que o validador deve relatar: `Cronograma - Estrutura de Dados 2.xlsx.bak` em pasta ativa; `Aula 18 - Arvores Rubro-Negras - Propriedades (v2).pptx` (sufixo de versão); arquivos `~$…` (bloqueio do Office: ignorar, nunca relatar como material); números de aula repetidos com temas diferentes (`Aula 05`, `Aula 06`, `Aula 07`, `Aula 15`, `Aula 18`, `Aula 21`); `Lista - BST.pdf`, `Lista de Exercicios - …`, `Atividade Pratica - …`, `Simulado - …` sem número em `03 - Atividades e Listas`; `_ferramentas` sem prefixo; acentuação inconsistente (`Arvores` × `Árvores`).
- `09 - Modelos`: `Modelo LaTeX/` (`modelo-prova.tex`, `unirv-cabecalho.sty`, logo; compila com `pdflatex` duas vezes por causa do `lastpage`), `Modelo de Cabeçalho de Prova.docx`, `Modelo de Slides UniRV/` (§2.1).
- Semestre: pastas `00`…`10`, `11-Relatórios` (fora do padrão), planilhas `2026 - Notas N1.gsheet`, `2026 - NOTAS N2.gsheet` (dado de aluno, não abertas).

## 4. Arquitetura

### 4.1 Visão

```
professor ──fala──▶ host (Claude/Codex/Antigravity/OpenCode/ChatGPT)
                      │ carrega skills/ (SKILL.md finas)
                      ▼
            lançador scripts/acad.py  (stdlib; acha Python, prepara ambiente)
                      │
                      ▼
            núcleo acad (Python)  ◀── também exposto como  acad mcp (stdio)
                      │ lê/grava só via acad.arquivos (lista de exclusão + escrita confirmada)
                      ▼
            workspace do professor (Drive)   +   estado local (~/.librarius ou dados do plugin)
```

Skills decidem **quando** chamar o núcleo e **como** conduzir a aprovação; o núcleo faz toda operação determinística e toda validação.

### 4.2 Abordagens consideradas para executar o núcleo sem instalação manual de Python

1. **Lançador stdlib + ambiente virtual por versão** (escolhida). `scripts/acad.py` usa só a biblioteca padrão: procura `uv`; se houver, roda `uv run --project <raiz> -m acad`; senão procura Python ≥ 3.11 (`py -3`, `python`, `python3`), cria venv em `<dados>/ambiente-<versao>` e instala a raiz do plugin (`pip install <raiz>`), uma vez por versão. Sem Python, sai com código 3 e mensagem em português explicando o que falta e que o assistente pode instalar com a permissão do professor. Prós: sem build, funciona igual em todos os hosts locais. Contra: precisa de rede na primeira execução (dito na explicação de privacidade).
2. Dependências vendorizadas no repositório: evita rede, mas `python-pptx` depende de `lxml` compilado por plataforma; inviável sem build.
3. Executável único por SO (PyInstaller): contraria "sem build obrigatório" e aumenta o repositório.

Diretório de dados: `${CLAUDE_PLUGIN_DATA}` quando definido (Claude; Codex define por compatibilidade); senão `%LOCALAPPDATA%\librarius` (Windows) ou `~/.local/share/librarius`. Variável `ACAD_DADOS` sobrepõe (usada nos testes).

### 4.3 Como a skill encontra o lançador

Cada `SKILL.md` traz uma seção fixa "Como chamar o núcleo" que manda executar `python "<raiz>/scripts/acad.py" <subcomando> --json`, onde `<raiz>` é:

- `${CLAUDE_PLUGIN_ROOT}` — o Claude substitui no corpo da skill;
- senão, a pasta dois níveis acima do `SKILL.md` (`skills/<nome>/SKILL.md` → raiz), que vale em qualquer host que instale o repositório inteiro.

A seção é gerada a partir de um único trecho (`scripts/trechos/chamar-nucleo.md`, fora de `skills/` para nenhum host tratá-lo como skill; inserido por `scripts/sincronizar-skills.py` e checado por teste) para não divergir entre skills.

### 4.4 Estrutura do repositório (MVP)

```
librarius/
├── .claude-plugin/{plugin.json, marketplace.json}
├── .codex-plugin/plugin.json
├── .agents/plugins/marketplace.json
├── plugin.json                      # Antigravity + manifesto portátil Agent Plugins (Codex)
├── .mcp.json                        # MCP stdio (Claude; Codex pelo formato de compatibilidade)
├── mcp_config.json                  # MCP no Antigravity (formato a confirmar na fase 4)
├── hooks/hooks.json                 # SessionStart → skill de entrada (Claude), opcional
├── .opencode/INSTALAR.md
├── opencode.json                    # exemplo
├── AGENTS.md  INSTALAR.md  README.md  LICENSE
├── skills/
│   ├── usando-agente-academico/  organizador-academico/  planejador-semestre/
│   ├── distribuidor-ementa/  gerador-aulas/  gerador-avaliacoes/  validador-academico/
├── acad/
│   ├── __init__.py  __main__.py  cli.py  contexto.py  config.py  mcp.py  saida.py  erros.py  mensagens.py
│   ├── comandos/        # um módulo por grupo de subcomandos (registrados no cli)
│   ├── plataformas/     # validação de skills e manifestos, versão, empacotador ChatGPT
│   ├── arquivos/        # privacidade.py, escrita.py, diario.py (desfazer), caminhos.py
│   ├── esquemas.py      # carga e validação JSON Schema
│   ├── perfil/          # perfil.py, detectar.py, perfis/fasoft.yaml
│   ├── calendario/      # modelo.py, importar_ics.py, importar_xlsx.py
│   ├── cronograma/      # planilha.py, classificar.py, consulta.py (paridade skill cronograma), importar.py, exportar_planilha.py
│   ├── encontros/       # gerar.py, carga.py
│   ├── planejamento/    # arquivos.py (leitura dos YAML), distribuir.py, replanejar.py, status.py
│   ├── manifestos/      # hashes.py, manifesto.py
│   ├── geracao/         # aula.py, slides.py, avaliacao.py, latex.py
│   ├── exportadores/    # ics.py
│   └── validacao/       # nomenclatura.py, estrutura.py, regras.py, achados.py, validar.py
├── esquemas/  *.schema.json (semestre, calendario, disciplina, turma, encontro, aula, questao, avaliacao, manifesto, perfil, conteudo-aula, conteudo-avaliacao)
├── modelos/  roteiro-aula.md, lista.md, prova.tex (genéricos, sem marca institucional)
├── plataformas/<host>/FONTE.md
├── scripts/  acad.py, sincronizar-versao.py, sincronizar-skills.py, validar-manifestos.py, empacotar-chatgpt.py, trechos/
├── testes/
│   ├── unidade/  integracao/  hosts/ (roteiros da matriz)  ferramentas/
│   ├── amostras/   # cópias anonimizadas; árvore espelhada (nomes reais, arquivos vazios) + .xlsx real
│   ├── esperados/  # saídas de referência
│   └── referencia/verificar_cronograma.py   # cópia do oráculo (código do próprio professor)
└── pyproject.toml
```

Sem pasta `bin/` (claude.ai e Cowork recusam plugin com `bin/` na raiz). `comandos/`, `agentes/` e `modelos/{feedback,…}` do briefing ficam para v2: nenhuma função do MVP depende deles.

### 4.5 Dependências Python

`pyyaml`, `jsonschema`, `openpyxl`, `icalendar`, `python-pptx` (só após D4), `mcp` (SDK oficial). Testes: `pytest`. Versões fixadas no `pyproject.toml` na tarefa que introduz cada uma, conferidas com `pip index versions <pacote>` no dia — nada de versão de memória. `requires-python = ">=3.11"`.

## 5. Contratos de dados (seção 7)

Todos os YAML de disciplina ficam em `<disciplina>/01 - Planejamento/`. Datas ISO `AAAA-MM-DD`; horas `"HH:MM"` (string); fuso explícito por turma. Cada arquivo tem um esquema em `esquemas/` com `$id` `https://github.com/vnmartinez/librarius/esquemas/<nome>.schema.json`, `additionalProperties: false` e `"versao_esquema": 1` na raiz do documento.

### 5.1 `calendario.yaml` (em `00 - Administração Acadêmica/`)

```yaml
versao_esquema: 1
calendario:
  semestre: "2026-2"
  inicio: 2026-07-27
  fim: 2026-12-12
  fonte: { tipo: ics | xlsx | manual, arquivo: "…", sha256: "…" }
  status: rascunho | confirmado        # só "confirmado" é usado para gerar encontros
  confirmado_em: null
  dias:                                 # só exceções ao padrão "dia útil seg–sex é letivo"
    - { data: 2026-10-12, tipo: feriado, descricao: "Nossa Senhora Aparecida" }
    - { data: 2026-10-17, tipo: sabado-letivo, equivale_a: 1 }   # ISO: segue horário de segunda
    - { data: 2026-11-20, tipo: recesso }
  eventos:
    - { inicio: 2026-09-21, fim: 2026-09-25, tipo: semana-academica, descricao: "SETECH" }
```

`tipo` ∈ `feriado | recesso | sabado-letivo | troca-de-dia | semana-academica | avaliacao | outro`. `equivale_a` obrigatório em `sabado-letivo` e `troca-de-dia`.

### 5.2 `disciplina.yaml`, `turma-<ID>.yaml`, `encontros-<ID>.yaml`, `aulas.yaml`

Exatamente como na seção 7 do briefing, com as precisões:

- `disciplina.codigo`: `^[A-Z0-9]{2,10}$`; `disciplina.pasta`: nome da pasta real (ex.: `04 - Estrutura de Dados 2 - 5º Período`); `carga_horaria.minutos_hora_aula` obrigatório se e só se `unidade = hora_aula`; `bloom` ∈ `lembrar | entender | aplicar | analisar | avaliar | criar`.
- `turma.id`: `^[A-Z]{1,3}[0-9]?$`; `dia_semana` 1–7 (ISO); `excecoes[].tipo` ∈ `cancelamento | reposicao`; `reposicao` exige `inicio`, `fim`, `repoe`.
- `encontros-<ID>.yaml` é **gerado**: cabeçalho `gerado_por: acad <versao>`, `gerado_em`, `entradas` (hash de `calendario.yaml`, `turma-<ID>.yaml`); `encontros[]` com `id` (`E01`…), `data`, `inicio`, `fim`, `status` (`previsto | realizado | cancelado`), `aulas` (lista de ids de aula, N:M), `funcao` (`conteudo | revisao | avaliacao`), `origem` (`horario | reposicao | sabado-letivo | planilha`), `motivo` (se cancelado). Regenerar preserva `status`, `aulas` e `funcao` por chave (`data`, `inicio`); ids são renumerados por ordem cronológica e o diff é relatado.
- `aulas.yaml`: `versao_esquema`, `disciplina`, `aulas[]`. Cada aula: `id` (`^Aula [0-9]{2}$`), `tema`, `slides`, `roteiro`, `codigo`, `lista` (caminhos relativos à pasta da disciplina, separador `/`, NFC), `objetivos`, `prerequisitos`, `encontros_necessarios` (inteiro ≥ 1, padrão 1), `duracao_estimada_min`, `status` (`planejada | rascunho | revisada | aprovada | ministrada`), `ministrada_em` (ids de encontro), `manifesto` (objeto da §6, opcional).
- `avaliacao.yaml` (MVP, em `01 - Planejamento/avaliacoes/<etapa>-<turma>.yaml`): `etapa` (`N1 | N2 | N3`, configurável por perfil), `turmas`, `data`, `aulas_cobertas`, `objetivos`, `questoes[]` (inline, esquema `questao`), `semente`, `arquivos` (prova, gabarito), `manifesto`.
- `questao`: `id`, `enunciado`, `tipo` (`multipla-escolha | discursiva | verdadeiro-falso`), `alternativas`, `resposta`, `objetivos`, `aulas`, `bloom`, `pontos`.

### 5.3 Perfil institucional (`acad/perfil/perfis/fasoft.yaml` e `<dados>/configuracao.yaml`)

```yaml
versao_esquema: 1
perfil:
  id: fasoft
  instituicao: "UniRV — Fasoft"
  semestre_pasta: "{ano}/{Primeiro|Segundo} Semestre"
  disciplina_pasta: '^(?P<num>\d{2}) - (?P<nome>.+?)(?: - (?P<periodo>.+))?$'
  subpastas_disciplina: ["01 - Planejamento", "02 - Aulas", "03 - Atividades e Listas",
                         "04 - Projetos e Entregáveis", "05 - Materiais de Referência",
                         "06 - Código e Exemplos", "99 - Arquivo"]
  pasta_avaliacoes: '^\d{2} - Avaliações$'
  pasta_modelos: '^\d{2} - Modelos$'
  etapas_avaliacao: [N1, N2, N3]
  nomenclatura: { aula: '^Aula \d{2} - ', lista: '^(Lista|Atividade) \d{2} - ', pasta: '^\d{2} - ',
                  sufixos_proibidos: ['\(Revisado\)', '_v\d+', '\(v\d+\)', ' - [Cc]opia', '\(\d+\)', '\.bak$'] }
  carga_horaria: { unidade: null, minutos_hora_aula: null }   # D3
  exclusao: [ ... §7 ... ]
```

`configuracao.yaml` (estado local, fora do Drive): `perfil`, `raiz_workspace`, `semestre_atual`, `disciplinas` (código → pasta), `turmas`.

## 6. Manifestos e hashes (seção 8)

- Hash: `sha256:` + hex minúsculo. Arquivo: hash dos bytes. Entrada YAML parcial (`aulas.yaml#Aula 03`): hash do JSON canônico do item (`json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))` em UTF-8), excluindo o próprio campo `manifesto`. Pasta (template de slides, código): hash do JSON canônico da lista ordenada `[caminho_relativo_posix_nfc, hash_arquivo]`, ignorando `~$*`, `node_modules/`, `.git/`.
- Chaves de `entradas`: caminho relativo à raiz do **semestre**, separador `/`, NFC, com fragmento `#<id>` para itens.
- Manifesto de aula: guardado em `aulas.yaml` → `aula.manifesto` (`artefatos[]`, `gerado_em` com fuso, `entradas`, `aprovado`, `aprovado_em`, `versao_acad`). Nenhum arquivo extra em `02 - Aulas`. Manifesto de avaliação: dentro do `avaliacao.yaml`.
- `acad validar` recalcula e emite `manifesto-desatualizado` (com a lista de entradas divergentes) e `artefato-ausente`.
- Artefato aprovado nunca é regerado automaticamente: `acad gerar` sobre aula `aprovada` recusa, a menos que `--revisar` (volta a `rascunho`, versão anterior vai para `99 - Arquivo`).
- Ciclo de status: `planejada → rascunho → revisada → aprovada → ministrada`; transições validadas por tabela em código; retrocesso só por `--revisar`.

## 7. Privacidade e escrita segura

### 7.1 Lista de exclusão (dado de aluno)

Padrão do perfil Fasoft (globs relativos à raiz do semestre, comparação sem diferenciar maiúsculas):

- `*Notas*` e `*NOTAS*` (planilhas de notas, inclusive `.gsheet`)
- `*/02 - Alunos/**` dentro de pastas de TFC (`* - TFC*/02 - Alunos/**`)
- `*Relatórios*/**`
- `*/04 - Projetos e Entregáveis/**` (entregas)
- `* - Estágio/**` (acréscimo conservador; o professor pode liberar)

Regras: `acad.arquivos.privacidade` é a única porta de listagem e leitura do workspace. Caminho excluído não é aberto **nem listado** (o nome de pasta de aluno é dado pessoal). O validador só diz "N pastas protegidas não foram lidas". Teste: espiona `open`/`os.scandir` e falha se um caminho excluído for tocado.

### 7.2 Escrita confirmada, arquivo morto e desfazer

- Todo comando que grava produz primeiro uma **proposta** (`<dados>/propostas/<id>.json`: lista de operações `criar | substituir | arquivar`, com caminhos e resumo em português). Nada é gravado até `acad aplicar <id>`.
- `substituir` move a versão anterior para `99 - Arquivo/` da disciplina (ou equivalente do perfil) com o mesmo nome; se já existir, acrescenta ` - anterior AAAA-MM-DD` (o único sufixo admitido em `99 - Arquivo`; o validador não o relata lá dentro).
- Nunca há exclusão. `acad desfazer` reverte a última proposta aplicada a partir de `<dados>/diario.jsonl`.
- Guarda de raiz: escrita só dentro de `raiz_workspace` configurada; nos testes, `ACAD_RAIZ` aponta para cópia temporária, e um teste garante que nenhuma escrita sai de `tmp_path`. Neste ciclo, nenhuma tarefa executa `aplicar` contra o Drive real.

## 8. CLI `acad` (contrato)

Saída: texto em português simples por padrão; `--json` devolve envelope único:

```json
{"ok": true, "mensagem": "…pt simples…", "dados": {}, "avisos": [], "erros": [{"codigo": "…", "mensagem": "…", "detalhe_tecnico": "…"}], "proposta": null}
```

Códigos de saída: 0 ok; 1 validação com achados de nível `erro`; 2 uso incorreto; 3 ambiente (Python, dependência, raiz não encontrada); 4 bloqueado por decisão em aberto. Detalhes técnicos vão para `<dados>/registro.log`, nunca para `mensagem`.

| Subcomando | Função | Grava? |
|---|---|---|
| `acad ambiente verificar` | Python, dependências, raiz, perfil | não |
| `acad perfil detectar --raiz <pasta>` | Detecta semestre, disciplinas e pastas; propõe perfil | não |
| `acad iniciar <semestre> [--confirmar]` | Cria `configuracao.yaml` (estado local, fora do workspace) | só com `--confirmar` |
| `acad disciplina criar` / `acad turma criar` / `acad disciplina estrutura` | `disciplina.yaml`, `turma-<ID>.yaml`, subpastas padrão | proposta |
| `acad calendario importar <arquivo>` / `confirmar` | ICS ou XLSX → `calendario.yaml` rascunho; confirmar muda status | proposta |
| `acad cronograma importar <DISC> --turma <ID>` | `.xlsx` → `encontros-<ID>.yaml` + `aulas.yaml` | proposta |
| `acad cronograma consultar [--data D] [--disciplina X]` | "Aula de hoje" com paridade da skill `cronograma` | não |
| `acad cronograma exportar-planilha <DISC>` | YAML → `Cronograma - <Disciplina>.xlsx` | proposta |
| `acad encontros gerar <DISC> --turma <ID>` | Calendário confirmado × horários | proposta |
| `acad plano distribuir <DISC> --turma <ID>` | Aulas sobre encontros | proposta |
| `acad plano replanejar <DISC> --turma <ID> --cancelar <data>` | Relatório de diff | proposta |
| `acad validar [<DISC>] [--raiz]` | Todas as regras | não |
| `acad gerar aula <DISC> --aula NN` | Roteiro, código, lista, slides (D4), manifesto | proposta |
| `acad gerar avaliacao <DISC> --etapa N1 --turma TA` | `.tex` + gabarito, PDF se houver compilador | proposta |
| `acad aula status <DISC> --aula NN <novo-status>` | Transição de status (aprovar, ministrada) | proposta |
| `acad exportar ics <DISC> --turma <ID>` | Encontros em ICS | proposta |
| `acad aplicar <id>` / `acad desfazer` | Executa / reverte | sim |
| `acad mcp` | Servidor MCP stdio | — |

Subcomandos do briefing (`acad iniciar 2026-2`, `acad calendario importar`, …) são preservados.

### 8.1 Paridade com a skill `cronograma` (critério de pronto §15)

`acad cronograma consultar --data D --json` devolve, por disciplina com aula na data, os mesmos campos do script legado (`disciplina`, `semana`, `aula`, `aula_num`, `topico`, `linha`, `materiais.{slides, slides_divergentes, roteiros_resumos, atividades, atividades_relacionadas, codigos}`) com as mesmas heurísticas da §3.3, mais campos novos (`tipo`: `aula | sem-aula | avaliacao`). Teste de paridade: roda o oráculo (`testes/referencia/verificar_cronograma.py`) e o `acad` sobre a mesma árvore de amostras, para um conjunto de datas, e compara os campos comuns (caminhos absolutos ignorados). Diferença intencional: o `acad` respeita a lista de exclusão; o oráculo não — as amostras não contêm pastas excluídas.

## 9. Regras de validação (código de achado → nível)

| Código | Nível | Regra |
|---|---|---|
| `esquema-invalido` | erro | YAML não segue o esquema |
| `nome-aula-sem-prefixo` | erro | arquivo em `02 - Aulas` sem `Aula NN - ` |
| `nome-lista-sem-prefixo` | erro | arquivo em `03 - Atividades e Listas` sem `Lista NN - `/`Atividade NN - ` (aceita `Aula NN - ` como vínculo à aula — padrão já em uso) |
| `pasta-sem-prefixo` | erro | pasta de disciplina/subpasta sem `NN - ` (inclui `11-Relatórios`, `_ferramentas`) |
| `sufixo-proibido` | erro | `(Revisado)`, `_v2`, `(v2)`, ` - copia`, `(1)`, `.bak` fora de `99 - Arquivo` |
| `numero-aula-repetido` | aviso | mesmo `Aula NN` com temas diferentes em `02 - Aulas` |
| `readme-desatualizado` | aviso | pastas reais ≠ pastas listadas no `README.md` do semestre |
| `subpasta-padrao-ausente` | aviso | disciplina sem uma das subpastas do perfil |
| `carga-unidade-nao-confirmada` | aviso | unidade nula (D3) |
| `carga-horaria-incompativel` | erro | soma dos encontros não cancelados ≠ carga exigida, na unidade declarada |
| `encontro-em-dia-nao-letivo` | erro | encontro em feriado/recesso sem exceção |
| `objetivo-sem-aula` / `objetivo-sem-avaliacao` | aviso | cobertura |
| `avaliacao-sobre-nao-ministrada` | erro | aula coberta sem status `ministrada` nem encontro `previsto` anterior à data da prova |
| `aula-antes-de-prerequisito` | erro | primeiro encontro da aula ≤ primeiro encontro do pré-requisito |
| `manifesto-desatualizado` / `artefato-ausente` | aviso / erro | §6 |
| `slide-numeracao-divergente` | aviso | heurística da skill `cronograma` |

Arquivos `~$*` são ignorados. Comparação de tema × arquivo: NFC + remoção de acentos + minúsculas. Cada achado carrega `mensagem` em português simples e `caminho` relativo.

## 10. Geração

- **Aula** (`geracao/aula.py`): recebe contrato de entrada (item de `aulas.yaml`, objetivos, perfil) e conteúdo fornecido pela skill em arquivo JSON (`--conteudo`) — o LLM redige, o núcleo grava com nome canônico (`Aula NN - <Tema>.pptx`, `Aula NN - Roteiro de Aula - <Tema>.md`, `06 - Código e Exemplos/aula-NN-<tema-slug>/`, `03 - Atividades e Listas/Lista NN - <Tema>.md`), calcula manifesto e põe a aula em `rascunho`. Estimativa de tempo: soma de `minutos` declarados por bloco do roteiro × duração dos encontros; desvio > 15% vira aviso.
- **Slides** (`geracao/slides.py`): interface `GeradorSlides.gerar(conteudo, destino, template) -> Path`. Implementação real BLOQUEADA por D4; `GeradorSlidesFalso` (testes) grava um arquivo marcador.
- **Avaliação** (`geracao/avaliacao.py`, `latex.py`): preenche o modelo do perfil (`\avaliacaoTitulo`, `\avaliacaoDisciplina`, …) com as questões; versões por permutação com `random.Random(semente)`; gabarito em arquivo separado; nome `[Disciplina] - N1 - [descrição] - [turma/versão].tex` e `… - Gabarito.tex` na pasta `NN - Avaliações/N1`. Compila com `tectonic` ou `pdflatex` (2 passes) se existir; senão grava só o `.tex` e avisa. Cobertura validada antes de gerar (`avaliacao-sobre-nao-ministrada` bloqueia).
- Modelos genéricos em `modelos/`; o modelo institucional é lido de `09 - Modelos` em tempo de execução e entra no manifesto por hash (nunca copiado para o repositório).

## 11. Skills (seção 15)

Sete skills em `skills/`, `name` = pasta, `description` ≤ 1024 em português dizendo o que faz e quando usar, corpo < 500 linhas, seção comum "Como chamar o núcleo" (§4.3), regras de conversa da §1A (uma pergunta por vez; resumo antes de gravar; nunca mostrar caminho longo, hash ou YAML; erro explicado). `planejador-semestre` absorve `cronograma` (gatilhos: "aula de hoje", "o que tenho amanhã", "tem slide pronto?"). `usando-agente-academico` lista as demais e responde "o que você sabe fazer?". `AGENTS.md` na raiz: versão compacta das mesmas regras. Validação: teste próprio implementa as regras do Agent Skills (e roda `skills-ref validate` quando instalado).

## 12. Adaptadores por host (seção 4), com fonte e data

Todas as fontes foram consultadas em **22/10/2026** e estão detalhadas em `plataformas/<host>/FONTE.md`.

| Host | Arquivos | Fonte | Validação automática | Pontos a confirmar na matriz |
|---|---|---|---|---|
| Claude Code | `.claude-plugin/plugin.json` (`name: librarius`, `displayName`, `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords`), `.claude-plugin/marketplace.json` (`source: "./"`), `.mcp.json`, `hooks/hooks.json` | https://code.claude.com/docs/en/plugins-reference ; https://code.claude.com/docs/en/plugin-marketplaces | `claude plugin validate . --strict` | — |
| Claude Cowork / app | mesmos; sem `bin/` | idem + https://claude.com/docs/plugins/org-sync | idem | fluxo gráfico de instalação; se MCP stdio e hooks carregam |
| Codex | `plugin.json` raiz (portátil, sem `extensions`) + `.codex-plugin/plugin.json` (camada OpenAI: `skills`, `interface`) + `.agents/plugins/marketplace.json` (`source: {source: local, path: "./"}`, `policy`, `category`) + `.mcp.json` | https://developers.openai.com/codex/plugins/build.md ; https://learn.chatgpt.com/docs/build-skills.md ; https://agent-plugins.org/schemas/1.0.0/plugin.schema.json | validação por esquema (Agent Plugins) em `scripts/validar-manifestos.py`; `codex plugin marketplace add <dir>` em teste de host | `path: "./"`; substituição de `${CLAUDE_PLUGIN_ROOT}` em `.mcp.json` e skills |
| Antigravity app / IDE / CLI | `plugin.json` raiz: **só** `$schema`, `name`, `description`; `mcp_config.json`; `skills/` | https://antigravity.google/docs/plugins?tab=cli | regra do esquema (nome `^[a-zA-Z0-9-_]+$`, sem chaves extras) no validador; `agy plugin install <dir>` + `agy plugin list --json` | aceitação do `$schema` Agent Plugins; formato de `mcp_config.json`; alternativa `.antigravity-plugin/` (superpowers) |
| OpenCode | `opencode.json` de exemplo (`skills: ["<clone>/skills"]` na v2; `mcp.librarius = {type: local, command: [...]}`), `.opencode/INSTALAR.md` | https://opencode.ai/v2/docs/skills/ ; https://opencode.ai/docs/skills/ ; https://opencode.ai/docs/mcp-servers/ | validação de forma do `opencode.json` | versão estável sem opção `skills` (fallback: link em `~/.config/opencode/skills`) |
| ChatGPT | `dist/chatgpt/<skill>.zip` (uma pasta de topo, um `SKILL.md`), gerado por `scripts/empacotar-chatgpt.py` | https://help.openai.com/en/articles/20001066-skills-in-chatgpt (HTTP 403 em 22/10/2026); https://developers.openai.com/api/docs/guides/tools-skills | teste do zip (estrutura, ≤ 50 MB) | formato real de upload no app (reler a página antes de implementar); D1/D2 |
| Agent Skills (todos) | `skills/<nome>/SKILL.md` | https://agentskills.io/specification | teste de frontmatter | — |

Conflito do `plugin.json` na raiz: o Antigravity proíbe chaves além de `name`/`description` (o exemplo mostra `$schema`) e o manifesto portátil Agent Plugins exige `$schema` e `name`. O arquivo terá apenas `$schema`, `name`, `description`, o que satisfaz os dois esquemas no papel; `version` fica fora (por isso o `sincronizar-versao` não o toca). Se a matriz mostrar rejeição em algum host, cai-se para `.antigravity-plugin/plugin.json` (forma do superpowers) e o achado é registrado no `FONTE.md`.

`scripts/sincronizar-versao.py` mantém a mesma versão em: `pyproject.toml`, `acad/__init__.py`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (`plugins[0].version`), `.codex-plugin/plugin.json`. Teste falha se divergirem.

## 13. Servidor MCP local

`acad mcp` via SDK oficial `mcp` (stdio). Ferramentas = subcomandos, nomes com hífen (`validar`, `cronograma-consultar`, `encontros-gerar`, `plano-distribuir`, `gerar-aula`, `gerar-avaliacao`, `aplicar`, `desfazer`, `ambiente-verificar`), mesmo envelope JSON. Ferramentas que gravam só devolvem proposta; `aplicar` exige o id. A API exata do SDK é lida na documentação no dia da tarefa (nada de memória). Teste: cliente MCP do próprio SDK conecta por stdio, lista ferramentas e chama `validar` sobre amostras.

## 14. Testes

- `pytest`; marcadores `drive` (lê `G:\Meu Drive\Fasoft` em modo leitura; pulado se ausente), `hosts` (exige CLI do host), `latex` (exige compilador).
- Amostras: `testes/amostras/fasoft/2026/Segundo Semestre/` gerada por `testes/ferramentas/espelhar-amostras.py` — copia **nomes** (arquivos vazios) de `04 - Estrutura de Dados 2 - 5º Período`, `00 - Administração Acadêmica` e `09 - Modelos`, e o conteúdo real só de `Cronograma - Estrutura de Dados 2.xlsx` e `AGENTS.md`/`README.md`; aplica a lista de exclusão; nunca grava no Drive (abre a origem só para leitura). Logotipos e material didático completo não entram.
- Esperados: `testes/esperados/` com saídas de referência do oráculo e do `acad` por data.
- Critério de pronto do código (sem LLM): `acad validar --raiz "G:\Meu Drive\Fasoft\2026\Segundo Semestre"` roda em modo leitura e relata as divergências da §3.3; `acad cronograma consultar` bate com o oráculo no Drive real para as datas do semestre (teste `drive`).

## 15. Matriz de instalação por host (seção 13)

`testes/hosts/<host>.md`: roteiro com passos sem terminal (caminho do professor) e com terminal (avançado), e checagens: (1) plugin aparece instalado; (2) skill de entrada carrega; (3) `acad ambiente verificar` roda pelo lançador; (4) consulta "qual a aula de hoje de Estrutura de Dados 2?" responde igual ao oráculo; (5) leitura do Drive em modo leitura funciona (hosts locais); (6) MCP lista ferramentas (onde houver). Resultado registrado em `testes/hosts/resultados.md` com data, versão do host e versão do plugin. Teste com dois professores sem formação técnica é etapa humana registrada no mesmo arquivo; não bloqueia o merge do código.

## 16. Erros e mensagens

`acad/erros.py` define `ErroAcad(codigo, mensagem, detalhe_tecnico, saida)`; o `cli` captura qualquer exceção, grava o detalhe no `registro.log` e mostra só a mensagem. Catálogo de mensagens em `acad/mensagens.py` (português simples; teste proíbe termos técnicos como "YAML", "JSON", "hash", "stack", "exception", "path" nas mensagens ao professor).
