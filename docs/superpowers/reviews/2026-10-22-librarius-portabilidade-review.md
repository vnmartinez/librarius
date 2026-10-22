# Relatório de Revisão de Código — Librarius Portabilidade para Outras Instituições

**Data:** 22/10/2026  
**Revisor:** Antigravity (Reviewer / Processo 3 do ciclo orquestrado)  
**Branch:** `vnmartinez/librarius-portabilidade` (HEAD: `f2ba49a`)  
**Base:** `main` (`d944cbe`, 17 commits)  
**Worktree:** `C:\Users\Vinicius\orca\workspaces\librarius\librarius-portabilidade`  
**Documentos de referência:**
- Spec: `docs/superpowers/specs/2026-10-22-librarius-portabilidade-design.md` (achados A1–A7, decisões P1–P11)
- Plano: `docs/superpowers/plans/2026-10-22-librarius-portabilidade.md` (14 tarefas, 78 checkboxes concluídas)

---

## 1. Veredito

**Veredito:** `Ready to merge`

A implementação da portabilidade para outras instituições foi executada com absoluto rigor técnico e fidelidade ao design planejado. O projeto agora é plenamente portável: qualquer professor universitário pode inferir ou criar o perfil da sua própria instituição, organizar pastas com convenções próprias ou neutras, validar o semestre e gerar slides no padrão visual escolhido ou genérico sem qualquer resquício da marca UniRV. Simultaneamente, a compatibilidade estrita com o professor atual (UniRV / Fasoft) foi preservada com 100% de fidelidade byte a byte (comprovado por hashes SHA-256 das partes do `.pptx` gravados antes da refatoração).

Todos os 376 testes automatizados (364 padrão + 3 drive + 7 hosts + 1 rede + 1 latex) passaram sem qualquer erro ou regressão. Não foram identificados defeitos críticos ou importantes.

---

## 2. Evidências dos Comandos (Execução Literal)

Todas as suítes e verificações foram executadas no ambiente virtual local `.venv`:

### 2.1 Suíte Padrão de Testes
```
$ .venv/Scripts/python -m pytest -q
........................................................................ [ 19%]
........................................................................ [ 39%]
........................................................................ [ 59%]
........................................................................ [ 79%]
........................................................................ [ 98%]
....                                                                     [100%]
364 passed, 12 deselected in 119.12s (0:01:59)
```

### 2.2 Marcador `drive` (Leitura real no Google Drive em modo estritamente somente leitura)
```
$ .venv/Scripts/python -m pytest -q -m drive
...                                                                      [100%]
3 passed, 373 deselected in 23.22s
```

### 2.3 Marcador `hosts` (Validação de manifestos e CLIs dos ambientes)
```
$ .venv/Scripts/python -m pytest -q -m hosts
.......                                                                  [100%]
7 passed, 369 deselected in 9.96s
```

### 2.4 Marcador `rede` (Lançador stdlib e criação de ambiente isolado)
```
$ .venv/Scripts/python -m pytest -q -m rede
.                                                                        [100%]
1 passed, 375 deselected in 97.78s (0:01:37)
```

### 2.5 Marcador `latex` (Compilação de avaliações em PDF)
```
$ .venv/Scripts/python -m pytest -q -m latex
.                                                                        [100%]
1 passed, 375 deselected in 9.37s
```

**Total geral:** **376 testes executados e aprovados**, 0 falhas, 0 erros.

### 2.6 Verificação de Ambiente (`acad.py`)
```
$ .venv/Scripts/python scripts/acad.py ambiente verificar --json
{
  "ok": true,
  "mensagem": "O assistente está pronto para trabalhar.",
  "dados": {
    "python": "3.14.7",
    "faltando": []
  },
  "avisos": [],
  "erros": [],
  "proposta": null
}
```

### 2.7 Sincronização de Manifestos e Versão
```
$ .venv/Scripts/python scripts/validar-manifestos.py
claude: ok
codex: ok
antigravity: ok
opencode: ok

$ .venv/Scripts/python scripts/sincronizar-versao.py --verificar
0.1.0

$ .venv/Scripts/python scripts/sincronizar-skills.py --verificar
(exit code 0)
```

---

## 3. Auditoria Detalhada dos Itens

### 3.1 Compatibilidade do Professor Atual (Fasoft)
- **Referência SHA-256 dos slides:** A Tarefa 1 gravou os resumos SHA-256 de todas as partes dos arquivos gerados pelo perfil fasoft a partir do commit base `d944cbe` em `testes/esperados/slides-fasoft.json`. O teste `testes/unidade/test_compat_fasoft.py` regenera a apresentação com o código atual e confirma paridade exata de todos os hashes de partes internas do arquivo compactado `.pptx`.
- **Compatibilidade do Perfil v1:** Perfis com `versao_esquema: 1` continuam sendo carregados normalmente (`testes/esperados/perfil-fasoft-v1.yaml` e teste `test_perfil_v1_continua_valido`), com preenchimento retrocompatível transparente dos padrões em `acad/perfil/padroes.py` (`ESTRUTURA_V1`).
- **Comportamento Inalterado:** Validações, consultas de cronograma e geração de materiais para o perfil `fasoft` no Drive real e em amostras continuam produzindo saídas idênticas.

### 3.2 Eliminação de Marcas Fixas no Código
Executado `git grep -n -e 'UniRV' -e 'RIO VERDE' -e 'Fasoft' -e 'fasoft'` sobre `acad/`, `skills/`, `modelos/` e manifestos:
- Manifestos (`.claude-plugin/`, `.codex-plugin/`, `.agents/`, `plugin.json`, `mcp.json`, `opencode.json`): **0 ocorrências**.
- `skills/`: **0 ocorrências**.
- `modelos/`: **0 ocorrências**.
- `acad/`: Restam apenas 3 ocorrências plenamente justificadas:
  1. `acad/geracao/slides_pptx.py:3-4`: Comentário de docstring histórica explicando a origem das medidas do template;
  2. `acad/perfil/detectar.py:29`: Chave de retrocompatibilidade `raiz_fasoft` mantida no dicionário para evitar quebra de consumidores legados;
  3. `acad/perfil/perfis/fasoft.yaml`: Arquivo de configuração de dados da instituição Fasoft (nome, linhas de cabeçalho, logos).

Nenhum texto, logotipo, curso ("Bacharelado em Engenharia de Software") ou paleta de cores institucional permaneceu hardcoded nos geradores.

### 3.3 Perfil Neutro e Perfis de Outras Instituições
- **Perfil Neutro:** Definido em `acad/perfil/perfis/neutro.yaml` e `acad/geracao/identidade.py` (`IDENTIDADE_NEUTRA`), utilizando paleta neutra ardósia/azul-acinzentado (`2F3E4E`), sem logotipos e sem linhas de cabeçalho institucional na capa.
- **Inspeção Real do `.pptx` Gerado:** Slide widescreen 16:9 (`slide_width: 9144000`, `slide_height: 5143500` emu); zero formas de imagem (Picture); zero menções a UniRV, Rio Verde ou Fasoft; ausência da cor verde UniRV (`015537`) no XML; capa contendo exclusivamente o título, subtítulo/professor e ano.
- **Perfil Customizado e Estruturas Arbitrárias:** Verificado suporte a instituições com estruturas como `Materiais/AAAA-N` e papéis de pastas customizados, com reconhecimento de semestre, detecção de disciplinas e validação completa sem erros.
- **Teste Ponta a Ponta:** `testes/integracao/test_outra_instituicao.py` cobre todo o fluxo: `perfil criar` → `aplicar` → `iniciar` → `perfil detectar` → `disciplina criar` → `validar` → `gerar aula` → inspeção de PPTX → `cronograma consultar`.

### 3.4 Fim do Padrão `fasoft` Implícito
- `acad/contexto.py` define `PERFIL_PADRAO = "neutro"`.
- O comando `iniciar` adota `contexto.PERFIL_PADRAO` ("neutro") quando nenhum perfil é fornecido e emite aviso explicativo convidando o professor a criar o perfil da sua instituição.
- Nenhuma função herda silenciosamente o perfil do dono.

### 3.5 Reconhecimento de Raiz pela Estrutura
- `AGENTS.md` foi totalmente removido do fluxo de resolução de raiz (0 ocorrências em `acad/`).
- A localização da raiz agora é feita exclusivamente pelas regras estruturais do perfil (`semestre_de`, `base_semestre`), funcionando de forma uniforme em árvores profundas, relativas ou sintéticas.

### 3.6 Perfis do Usuário e Ciclo de Propostas
- Perfis do usuário residem em `dir_dados() / "perfis"` e têm prioridade de carregamento sobre os perfis empacotados.
- Comandos `perfil criar` e `perfil importar` operam obrigatoriamente por meio de proposta (`criar_proposta`), exigindo confirmação explícita (`acad aplicar <id>`) e permitindo reversão (`acad desfazer`).
- Mensagens de erro de validação do perfil traduzidas para português simples humanizado via `acad/perfil/validar.py` (ex.: `"Falta o nome da instituição."`, `"A cor “...” não é válida; use seis letras ou números, como 1F3A5F."`).

### 3.7 Esquema `perfil.schema.json` v2
- Suporta `versao_esquema` com enum `[1, 2]`.
- Define `additionalProperties: false` em todos os níveis.
- Torna blocos `estrutura`, `modelos` e `slides` opcionais para garantir retrocompatibilidade integral com o esquema v1.

### 3.8 Invariantes de Segurança e Privacidade
- Dados de alunos permanecem estritamente isolados e nunca lidos (`*Notas*`, `*Alunos*`, `*TFC*`, `*Relatórios*`, etc.).
- Nenhuma operação de escrita foi efetuada em `G:\Meu Drive\Fasoft` (garantido por interceptação nos testes de integração).
- Toda modificação de arquivos depende de proposta aprovada e transacional.
- Vocabulário técnico proibido (`TERMOS_PROIBIDOS`) ausente das mensagens retornadas ao usuário.

---

## 4. Classificação dos Achados

- **Críticos:** 0
- **Importantes:** 0
- **Residuais:** 0

---

## 5. Conclusão

A branch `vnmartinez/librarius-portabilidade` cumpre todos os requisitos do design e do plano de implementação com excelência de engenharia e cobertura de testes exemplar. Está plenamente pronta para integração à branch principal (`main`).
