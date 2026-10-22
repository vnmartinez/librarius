# Librarius — portabilidade para outras instituições (spec)

Data: 22/10/2026 · Base: `main` = `d944cbe` (MVP, 324 testes verdes) · Branch: `vnmartinez/librarius-portabilidade`

## 1. Objetivo

Um professor de **outra instituição** consegue instalar o Librarius, criar o perfil da sua instituição a partir da própria pasta (sem editar arquivo técnico), validar o semestre e gerar slides **sem a marca UniRV**. O perfil `fasoft` do dono continua com o mesmo comportamento: os mesmos slides (byte a byte nas partes do `.pptx`), as mesmas validações e a mesma consulta de cronograma.

Fora do escopo: mudar a geometria dos slides (posições e tamanhos continuam no código), novos tipos de slide, nomes de arquivos gerados (`Aula NN - …`, `Lista NN - …`, `aula-NN-…` continuam fixos), dados de alunos, MCP remoto (D1).

## 2. Achados (auditoria de `d944cbe`)

| # | Onde | Preso à UniRV/Fasoft |
|---|---|---|
| A1 | `acad/geracao/slides_pptx.py:42-70, 209-222` | Paleta (`015537`, `0E7A4E`, `E4EFE9`, `F2F7F4`, `1C2B24`, `2E3B34`, `6A7A72`, `C9D8D0`, `FFFFFF`, `D7E7DF`, `10231B`, `8FB79E`, `D8E8DF`), 9 144 000 × 5 143 500 EMU, Calibri/Courier New, textos "UNIVERSIDADE DE RIO VERDE (UniRV)", "Bacharelado em Engenharia de Software", "RIO VERDE — {ano}", logos `logo-header-unirv.png`, `logo-unirv.png`, `logo-fasoft.png`, limites 6/16/8 |
| A2 | `acad/geracao/aula.py:102-115` | Pasta de modelos achada por `"Modelos" in nome`; modelo de slides precisa se chamar `Modelo de Slides UniRV` |
| A3 | `acad/perfil/perfil.py:29-31` | Perfis só de dentro do pacote; só existe `fasoft.yaml`; não há perfil do usuário nem comando para criar/importar |
| A4 | `acad/contexto.py:50`, `acad/comandos/perfil.py:37`, `acad/perfil/perfil.py:29`, `acad/comandos/perfil.py:70` | Padrão silencioso `fasoft` |
| A5 | `acad/cronograma/consulta.py:22-36`, `acad/perfil/detectar.py:17-25` | Raiz achada pela palavra "Fasoft" no `AGENTS.md` ou pasta `fasoft`; semestre só `AAAA/Primeiro Semestre` ou `AAAA/Segundo Semestre`; chave de saída `raiz_fasoft` |
| A6 | `acad/comandos/gerar.py:93-104` | Modelo de prova fixo em `<Modelos>/Modelo LaTeX/modelo-prova.tex`; sem ele cai no genérico sem avisar |
| A7 | 14 literais em `contexto.py`, `validacao/validar.py`, `validacao/nomenclatura.py`, `geracao/nomes.py`, `geracao/aula.py`, `planejamento/arquivos.py`, `cronograma/consulta.py`, `comandos/{perfil,encontros,cronograma,aula}.py` | Nomes de subpasta fixos (`00 - `, `01 - Planejamento`, `02 - Aulas`, `03 - Atividades e Listas`, `05 - Materiais de Referência`, `06 - Código e Exemplos`, `99 - Arquivo`) e período por `startswith("Primeiro")` |

A7 não estava na auditoria do pedido, mas sem ele um semestre "de estrutura diferente" não valida: o perfil já declara `subpastas_disciplina`, porém o código ignora e usa os nomes da Fasoft.

## 3. Decisões

### P1 — Esquema do perfil versão 2, com a versão 1 ainda válida

`esquemas/perfil.schema.json`: `versao_esquema` passa de `const: 1` para `enum: [1, 2]`. Três blocos novos, **todos opcionais**, em `perfil`: `estrutura`, `modelos`, `slides`. `semestre_pasta` sai de `required` (nunca foi lido pelo código; continua aceito). Nada que um perfil v1 tinha deixa de ser aceito.

O carregador completa o que faltar com valores padrão:

- **`estrutura` ausente (perfis v1)** → os nomes que o MVP usava fixos no código (tabela abaixo). Era isso que um perfil v1 significava.
- **`modelos` ausente** → nenhum modelo institucional (prova simples, slides sem logos).
- **`slides` ausente** → identidade **neutra** (§3 P3). Marca institucional nunca é herdada por padrão.

`acad/perfil/perfis/fasoft.yaml` migra para v2 declarando tudo explicitamente (estrutura, modelos e a identidade UniRV), para que o comportamento do dono não dependa de valor padrão.

```yaml
# bloco estrutura (v2); valores = padrão para perfis v1
estrutura:
  semestre: '^(?P<ano>\d{4})/(?P<periodo>Primeiro|Segundo) Semestre$'   # casado contra "<pai>/<nome>"
  periodos: { Primeiro: 1, Segundo: 2 }       # texto do grupo "periodo" -> 1 ou 2; ausente = int(texto)
  administracao: '^00 - '
  papeis:
    planejamento: "01 - Planejamento"
    aulas: "02 - Aulas"
    atividades: "03 - Atividades e Listas"
    projetos: "04 - Projetos e Entregáveis"
    referencias: "05 - Materiais de Referência"
    codigo: "06 - Código e Exemplos"
    arquivo: "99 - Arquivo"
modelos:
  slides: "Modelo de Slides UniRV"            # pasta dentro da pasta de modelos; null = sem modelo
  prova: "Modelo LaTeX/modelo-prova.tex"      # relativo à pasta de modelos; null = prova simples
```

Regras de `estrutura.semestre`: o padrão é casado contra `"<nome da pasta-pai>/<nome da pasta>"`; se só houver o grupo no nome (padrão sem `/`), casa contra o nome. Grupos obrigatórios: `ano` e `periodo`. A **base** do semestre (onde ficam os anos ou os semestres) é a pasta acima do trecho casado: dois níveis se o padrão tem `/`, um nível se não tem.

`papeis.planejamento` substitui `subpastas_disciplina[0]` como prova de que uma pasta é disciplina (no fasoft são iguais). `pasta_arquivo` continua existindo; se `papeis.arquivo` faltar, vale `pasta_arquivo`.

### P2 — Onde o perfil é lido e qual é usado

- `carregar_perfil(id)` (sem valor padrão) procura `dir_dados()/perfis/<id>.yaml` e, se não existir, o empacotado `acad/perfil/perfis/<id>.yaml`. O perfil do usuário vence o empacotado de mesmo id.
- `id` só aceita `^[a-z0-9][a-z0-9-]{0,39}$` (evita caminho fora da pasta); fora disso: `ErroAcad("perfil-invalido", …)`.
- Perfil inexistente: `ErroAcad("perfil-nao-encontrado", "Não encontrei o perfil “X”. Quer criar um a partir da sua pasta?", saida=4)`.
- Perfil efetivo (`contexto.perfil()`): o `perfil` de `configuracao.yaml` (o último escolhido); sem configuração, **`neutro`**. Nunca `fasoft` por padrão.
- `acad iniciar` sem `--perfil`: mantém o da configuração existente; sem configuração, `neutro`, com aviso: "Usei o perfil neutro, sem marca de instituição. Se quiser, crio o perfil da sua instituição a partir da sua pasta."
- `acad disciplina criar` sem `--unidade` usa `contexto.perfil()` (hoje usa `carregar_perfil()` = fasoft).
- A configuração do dono já tem `perfil: fasoft` (gravada pelo `iniciar` do MVP) e não muda. `esquemas/semestre.schema.json` **não muda**.

### P3 — Identidade visual dos slides é dado do perfil

`acad/geracao/identidade.py` (novo) define `IdentidadeSlides` (dataclass imutável) e `IDENTIDADE_NEUTRA`. `GeradorSlidesPptx(ler_bytes=None, identidade=IDENTIDADE_NEUTRA)`; `avisos_editoriais(slides, limites=LIMITES_PADRAO)`. A geometria fica no código. Bloco `slides` do perfil:

```yaml
slides:
  tamanho: { largura_emu: 9144000, altura_emu: 5143500 }
  fontes: { texto: Calibri, codigo: Courier New }
  paleta:          # 13 cores, 6 dígitos hexadecimais
    principal: "015537"      # era VERDE
    secundaria: "0E7A4E"     # VERDE2
    claro: "E4EFE9"          # VERDE_CLARO
    claro2: "F2F7F4"         # VERDE_CLARO2
    tinta: "1C2B24"
    corpo: "2E3B34"
    apagado: "6A7A72"
    linha: "C9D8D0"
    fundo: "FFFFFF"          # BRANCO
    subtitulo_capa: "D7E7DF"
    codigo_fundo: "10231B"
    codigo_comentario: "8FB79E"
    codigo_texto: "D8E8DF"
  capa:
    linhas: ["UNIVERSIDADE DE RIO VERDE (UniRV)", "Bacharelado em Engenharia de Software"]  # até 2
    local: "RIO VERDE — {ano}"                                                              # "" = sem linha
  logos:                     # nomes dentro de <modelo de slides>/assets/
    cabecalho: logo-header-unirv.png          # null = sem logo no cabeçalho
    capa: [logo-unirv.png, logo-fasoft.png]   # até 2; posições fixas no código
  limites: { topicos: 6, linhas_codigo: 16, linhas_tabela: 8 }
```

Cada chave do bloco é opcional; o que faltar vem de `IDENTIDADE_NEUTRA`. **Identidade neutra:** mesmo tamanho, Calibri/Courier New, paleta cinza-azulada (`principal 2F3E4E`, `secundaria 4A6076`, `claro E8ECF0`, `claro2 F4F6F8`, `tinta 1E2328`, `corpo 2E3338`, `apagado 6B737B`, `linha CDD3D9`, `fundo FFFFFF`, `subtitulo_capa DCE2E8`, `codigo_fundo 1E252C`, `codigo_comentario 9AA8B5`, `codigo_texto E1E6EB`), `capa.linhas: []`, `capa.local: "{ano}"`, sem logos, limites 6/16/8.

Paleta a partir de uma cor (para `perfil criar --cor`): `principal = cor`; `secundaria = mistura(cor, branco, 0.25)`; `claro = mistura(cor, branco, 0.88)`; `claro2 = mistura(cor, branco, 0.94)`; `linha = mistura(cor, branco, 0.75)`; `subtitulo_capa = mistura(cor, branco, 0.82)`; demais = neutra. `mistura(a, b, t) = round(a + (b − a)·t)` por canal.

Com `modelos.slides` definido e a pasta ausente, aviso como hoje ("…os slides saem sem os logotipos"). Com `modelos.slides: null` ou identidade sem logos, nenhum aviso de logo.

### P4 — Comandos de perfil (escrita só por proposta)

Todos devolvem o envelope `ok/mensagem/avisos/erros/proposta` de sempre. A gravação é uma `Operacao("criar"|"substituir", "<id>.yaml")` em `criar_proposta(dir_dados()/"perfis", …)` (a pasta é criada antes, se faltar); vale `acad aplicar <id>` e `acad desfazer`. Um perfil substituído vai para a pasta de arquivo morto dentro de `perfis/`, como qualquer substituição.

- `acad perfil criar --raiz <pasta do semestre> --id <id> --instituicao "<nome>" [--cor RRGGBB] [--rodape "<linha>"]… [--local "<texto com {ano}>"]` — infere o perfil da pasta (P5), valida e propõe. Mensagem: "Reconheci o semestre AAAA-N com K disciplinas e preparei o perfil da <instituição>. Posso guardar?".
- `acad perfil importar --arquivo <perfil.yaml>` — valida o arquivo recebido (de um colega da mesma instituição) e propõe copiá-lo como `<id>.yaml`.
- `acad perfil listar` — só leitura: perfis do usuário e empacotados, indicando qual está em uso.

`acad perfil detectar` passa a usar a estrutura do perfil em uso e devolve `raiz` (nova) e `raiz_fasoft` (mesmo valor, mantida por compatibilidade, marcada como obsoleta na spec).

### P5 — Inferência do perfil a partir da pasta (`acad/perfil/inferir.py`)

Entrada: a pasta do semestre. Só lista **nomes de pastas** até dois níveis, sempre pela `Workspace` com a exclusão neutra; nunca abre arquivo.

1. Semestre — reconhece, nesta ordem: `AAAA/Primeiro|Segundo Semestre` (padrão fasoft); `AAAA/1`, `AAAA/2`, `AAAA/1º Semestre`, `AAAA/2o semestre` (`^(?P<ano>\d{4})/(?P<periodo>[12])(?:º|o)?(?: [Ss]emestre)?$`); `AAAA-N`, `AAAA.N`, `AAAA_N`, `AAAA N` (`^(?P<ano>\d{4})[-._ ](?P<periodo>[12])$`). Outro nome: saída 4, "Não reconheci o ano e o período pelo nome da pasta do semestre. Renomeie para algo como 2027-1 ou me diga qual é."
2. Pastas especiais do semestre — avaliações, modelos e administração pelos padrões neutros (`(?i)^(\d{2} - )?avalia`, `(?i)^(\d{2} - )?modelos?$`, `(?i)^(\d{2} - )?administra`).
3. Disciplinas — as demais pastas com pelo menos duas subpastas. Se todas começam com `NN - `, `disciplina_pasta = '^(?P<num>\d{2}) - (?P<nome>.+?)(?: - (?P<periodo>.+ Período))?$'` e `nomenclatura.pasta = '^\d{2} - '`; senão `'^(?P<nome>[^.~_].*)$'` e `nomenclatura.pasta = '^'`.
4. Subpastas e papéis — `subpastas_disciplina` = subpastas presentes em pelo menos metade das disciplinas, em ordem alfabética. Papel por palavra (sem acento, minúsculas), primeira que casar: `planej` → planejamento; `aula` → aulas; `ativ|lista|exerc` → atividades; `proj|entreg|trabalho` → projetos; `refer|biblio|material` → referencias; `codig|exemplo|fonte` → codigo; `arquivo|antig|morto` → arquivo. Papel sem pasta → nome neutro (`planejamento`, `aulas`, `atividades`, `projetos`, `referencias`, `codigo`, `arquivo`), acrescentado ao fim de `subpastas_disciplina` (o `disciplina estrutura` propõe criá-la).
5. Exclusão — a lista neutra (P6) mais `*/<nome da pasta de projetos>`.
6. Modelos — se a pasta de modelos tem uma subpasta com `slide` no nome, ela vira `modelos.slides`; um `.tex` com `prova` no nome dentro dela (até dois níveis) vira `modelos.prova`. Logos não são adivinhados (identidade neutra, ou `--cor`/`--rodape`/`--local`).
7. Demais campos — copiados do perfil neutro.

### P6 — Perfil neutro empacotado (`acad/perfil/perfis/neutro.yaml`, v2)

`id: neutro`, `instituicao: "Instituição de ensino"`, `estrutura.semestre` = padrão `AAAA-N` de P5, `periodos` ausente, `administracao: '(?i)^(\d{2} - )?administra'`, papéis com os nomes neutros de P5 (minúsculas, sem acento), `subpastas_disciplina` na ordem planejamento, aulas, atividades, projetos, referencias, codigo, arquivo; `pasta_arquivo: arquivo`; `pasta_avaliacoes` e `pasta_modelos` = padrões de P5; `etapas_avaliacao: [AV1, AV2, AV3]`; `disciplina_pasta` e `nomenclatura.pasta` = forma "sem número" de P5; `nomenclatura.aula/lista/sufixos_proibidos` iguais aos do fasoft (são genéricos); `carga_horaria: {unidade: null, minutos_hora_aula: null}`; `modelos` e `slides` ausentes. Exclusão (comparação sensível a maiúsculas, por isso as variantes):

```yaml
exclusao: ["*Notas*", "*notas*", "*NOTAS*", "*Alunos*", "*alunos*", "*Relatórios*", "*relatorios*",
           "*Relatorios*", "*Entregas*", "*entregas*", "*TFC*", "*TCC*", "*tcc*", "*Estágio*", "*estagio*",
           "*/projetos"]
```

### P7 — Raiz pela estrutura, não pela palavra "Fasoft"

`consulta.encontrar_raiz(inicio, perfil)` sobe a partir de `inicio`; em cada pasta `P` verifica se `P` é um semestre do perfil (pelo padrão com seu pai) com ao menos uma disciplina (pasta que casa `disciplina_pasta` e tem a pasta do papel `planejamento`), ou se há um semestre assim até dois níveis abaixo de `P`. A primeira `P` que satisfaz devolve a **base** do semestre (P1). No Drive do dono, de qualquer ponto dentro de `G:\Meu Drive\Fasoft`, a resposta continua `G:\Meu Drive\Fasoft` (base de `2026/Segundo Semestre`). `AGENTS.md` deixa de ser lido.

`detectar.py` usa o mesmo reconhecimento de semestre (e, portanto, períodos do perfil), as pastas especiais do perfil e `papeis.planejamento` para o cronograma.

### P8 — Fim dos nomes de subpasta fixos

`Perfil` ganha `pasta(papel) -> str`, `re_semestre`, `periodos`, `re_administracao`, `modelos`, `slides` e `partes_disciplina(nome) -> {num, nome, periodo}` (grupos ausentes viram `None`). Os 14 literais de A7 passam a usar o perfil; `geracao.nomes.arquivos_da_aula(num, tema, perfil)`; `consulta.consultar(raiz, alvo, perfil)`. Com o perfil fasoft os valores são os mesmos de hoje.

### P9 — Modelo de prova com aviso

`gerar avaliacao` usa `perfil.modelos.prova`. Se o perfil não declara modelo ou o arquivo não existe, usa `modelos/prova.tex` e avisa: "Usei o modelo simples de prova, sem o cabeçalho da instituição." Com o modelo do fasoft presente, nada muda.

### P10 — Mensagens de perfil inválido em português simples

`acad/perfil/validar.py`: `problemas_do_perfil(documento) -> list[str]`, que traduz os erros do esquema e acrescenta as checagens que o esquema não faz (padrões que não compilam; `estrutura.semestre` sem os grupos `ano` e `periodo`; `disciplina_pasta` sem o grupo `nome`). Exemplos: "Falta o nome da instituição.", "A regra que reconhece as pastas das disciplinas não funciona.", "A cor “12GG00” não é válida; use seis letras ou números, como 1F3A5F.", "O perfil tem uma informação que não conheço: “x”." Erro: `ErroAcad("perfil-invalido", "O perfil da instituição tem problemas: <até 3 itens>.", detalhe=<erros técnicos>, saida=1)`. Nenhuma mensagem contém termo de `mensagens.TERMOS_PROIBIDOS`. Mapa campo → nome amigável fica em `acad/perfil/validar.py`.

### P11 — Skills

`skills/organizador-academico/SKILL.md`: no início, perguntar a instituição; se não houver perfil, oferecer `acad perfil criar` (resumo + "sim" + `aplicar`), depois `acad iniciar --perfil <id> --confirmar`. `usando-agente-academico` cita que funciona com qualquer instituição. Sincronizar com `scripts/sincronizar-skills.py`.

## 4. Compatibilidade (fasoft)

- **Slides:** antes de qualquer refatoração, um teste de referência grava os resumos SHA-256 de todas as partes do `.pptx` gerado com o `CONTEUDO` de `testes/unidade/test_slides_pptx.py` e os três logos sintéticos (exceto `docProps/core.xml`, que tem data) em `testes/esperados/slides-fasoft.json`. Depois da refatoração, o mesmo conteúdo gerado com a identidade do perfil fasoft tem os mesmos resumos.
- **Perfil:** um teste carrega uma cópia v1 literal do `fasoft.yaml` de `d944cbe` (`testes/esperados/perfil-fasoft-v1.yaml`) e prova que é válida e produz o mesmo `Perfil` (estrutura igual) que o `fasoft.yaml` v2, exceto `slides` (neutra no v1) e `modelos` (vazio no v1).
- **Validação e cronograma:** os testes existentes (`test_validar`, `test_nomenclatura`, `test_consulta`, `test_paridade_cronograma`, `test_drive_somente_leitura`, `test_slides_drive`) continuam verdes com o perfil fasoft explícito.
- **Testes que dependiam do padrão silencioso:** recebem o perfil fasoft por uma fixture `perfil_fasoft`, que troca `acad.contexto.PERFIL_PADRAO` (valor de produção `"neutro"`) por `"fasoft"` via `monkeypatch`; `semestre_sintetico` (árvore no formato Fasoft) depende dela. Chamadas `carregar_perfil()` sem argumento nos testes passam a `carregar_perfil("fasoft")`. Nenhum teste deixa de ser executado.

## 5. Critérios de aceite

1. `.venv/Scripts/python -m pytest -q` verde, e verdes os marcadores `drive`, `hosts`, `rede`, `latex` onde o ambiente permitir (falta de ferramenta = `skip`, como hoje).
2. Resumos de `testes/esperados/slides-fasoft.json` iguais antes e depois.
3. `grep -rn "UniRV\|Rio Verde\|RIO VERDE\|fasoft\|Fasoft" acad --include=*.py` só encontra comentários/docstrings históricos e a chave obsoleta `raiz_fasoft` (P4), nenhum valor de marca ou de perfil padrão usado em execução; os valores vivem em `acad/perfil/perfis/fasoft.yaml`.
4. Sem configuração, `contexto.perfil().id == "neutro"`; `iniciar` sem `--perfil` não grava `fasoft`.
5. Perfil em `dir_dados()/perfis/x.yaml` vence o empacotado; id inválido e perfil quebrado dão mensagem sem termo técnico.
6. Perfil v1 continua válido (teste).
7. Ponta a ponta "outra instituição" (Tarefa final do plano): pasta `Materiais/2027-1/…` com nomes minúsculos sem número → `perfil criar` → `aplicar` → `iniciar` → `perfil detectar` reconhece o semestre e as disciplinas → `validar` roda sem erro de estrutura → `gerar aula` com slides → `aplicar` → o `.pptx` não contém "UniRV", "RIO VERDE", "Engenharia de Software" nem a cor `015537`, não tem figura, e o título usa a `--cor` escolhida; `cronograma consultar` de dentro de uma disciplina acha a raiz `Materiais`.
8. Nenhum teste lê ou escreve em `G:\` fora dos marcados `drive` (bloqueio `ACAD_BLOQUEAR_ESCRITA` já existente).

## 6. Riscos

- **Referência de slides frágil a versão do python-pptx:** os resumos dependem da versão instalada; o teste grava a versão no JSON e, se ela mudar, falha dizendo para regravar a referência **a partir de `d944cbe`** (não do código novo).
- **Exclusão sensível a maiúsculas:** mitigado pelas variantes no perfil neutro e pelo padrão da pasta de projetos inferido do nome real.
- **Inferência errada de papéis:** o professor vê o resumo antes do "sim"; o perfil pode ser recriado (substituição vai para o arquivo morto) ou importado.
