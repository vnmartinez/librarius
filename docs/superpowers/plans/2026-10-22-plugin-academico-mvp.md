# Librarius — Plano de implementação do MVP

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Entregar o MVP do briefing: núcleo Python `acad` com validação determinística, skills no padrão Agent Skills, manifestos por host, servidor MCP local e matriz de instalação.

**Architecture:** O repositório é o plugin. Skills finas em `skills/` chamam o lançador `scripts/acad.py`, que prepara um ambiente Python e executa o pacote `acad`. Todo acesso ao workspace do professor passa por `acad.arquivos` (lista de exclusão + escrita só por proposta aprovada). O mesmo núcleo é exposto como MCP stdio.

**Tech Stack:** Python ≥ 3.11 (máquina: 3.14.7), `pyyaml`, `jsonschema`, `openpyxl`, `icalendar`, `mcp` (SDK oficial), `python-pptx` (só após D4), `pytest`.

**Spec:** `docs/superpowers/specs/2026-10-22-plugin-academico-design.md` (leia junto com este plano; seções citadas como "spec §N"). Origem: `Plugin de IA para Professores Universitários — Brainstorming Revisado.md` ("briefing").

## Global Constraints

- Trabalhar só no worktree `C:\Users\Vinicius\orca\workspaces\librarius\plugin-academico-mvp`, branch `vnmartinez/plugin-academico-mvp`. Nada de commit/merge na `main`.
- `G:\Meu Drive\Fasoft`: **somente leitura**. Nunca criar, mover, renomear ou excluir nada lá. Única exceção de uso: ler para copiar amostras para `testes/amostras/` (Tarefa 6) e testes marcados `drive` (só leitura).
- Nunca ler dado de aluno: lista de exclusão da spec §7.1. Caminho excluído não é aberto nem listado.
- Repositório público: nada de dado de aluno, logotipo institucional ou material didático completo no Git.
- Nomes de skills, pastas, subcomandos, campos YAML/JSON e códigos de achado: português, minúsculo, sem acento, com hífen. Exceções: nomes exigidos pelos hosts (`SKILL.md`, `plugin.json`, …) e módulos Python (usam `_`).
- Todo texto ao professor em português simples, sem termos técnicos (lista proibida em `acad/mensagens.py`: `yaml`, `json`, `hash`, `sha`, `schema`, `stack`, `exception`, `traceback`, `path`, `stdout`).
- Toda regra verificável é código com teste; o LLM nunca valida datas, carga horária, nomenclatura nem referências.
- Nada é gravado no workspace sem proposta aprovada (`acad aplicar <id>`); substituição arquiva em `99 - Arquivo`; nunca excluir.
- Não inventar APIs, campos de manifesto nem caminhos de host: antes de escrever qualquer manifesto, reler `plataformas/<host>/FONTE.md` e a URL oficial nele, atualizando a data se mudou.
- Versões de dependência: fixar no `pyproject.toml` com o valor de `python -m pip index versions <pacote>` no dia da tarefa (nunca de memória); usar `>=X.Y,<X+1`.
- Interpretador dos testes: `PY=.venv/Scripts/python` (Windows, Git Bash). Rodar testes com `$PY -m pytest`.
- Decisões em aberto (spec §2): D1 MCP remoto, D2 ChatGPT só skills, D3 unidade de carga, D4 template de slides. Tarefa que depende delas está marcada **BLOQUEADA (Dn)**; pule-a e siga.
- Mensagens de commit em português, prefixos `feat:`, `test:`, `docs:`, `chore:`; terminar com `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Mapa de arquivos

| Arquivo | Responsabilidade | Tarefa |
|---|---|---|
| `pyproject.toml`, `acad/__init__.py`, `acad/__main__.py` | pacote, versão, dependências | 1 |
| `acad/saida.py`, `acad/erros.py`, `acad/mensagens.py` | envelope de resultado, erro com mensagem simples | 2 |
| `acad/config.py`, `acad/arquivos/caminhos.py` | diretório de dados, normalização de texto e caminho | 2 |
| `esquemas/*.schema.json`, `acad/esquemas.py` | contratos de dados | 3 |
| `acad/perfil/perfil.py`, `acad/perfil/perfis/fasoft.yaml` | perfil institucional | 4 |
| `acad/arquivos/privacidade.py` | única porta de leitura/listagem; lista de exclusão | 5 |
| `testes/ferramentas/espelhar-amostras.py`, `testes/amostras/`, `testes/referencia/` | amostras e oráculo | 6 |
| `acad/validacao/achados.py`, `nomenclatura.py`, `estrutura.py` | regras de nome e estrutura | 7, 8 |
| `acad/cronograma/planilha.py`, `consulta.py` | leitura de `.xlsx`, "aula de hoje" com paridade | 9, 10 |
| `acad/arquivos/escrita.py`, `diario.py` | propostas, aplicar, desfazer, arquivo morto | 11 |
| `acad/cli.py`, `acad/contexto.py`, `acad/comandos/*` | subcomandos e contexto (raiz, perfil, disciplina) | 12 (base) e seguintes |
| `acad/calendario/*` | calendário canônico, importação ICS/XLSX | 13, 14 |
| `acad/encontros/gerar.py`, `carga.py`, `acad/planejamento/arquivos.py` | encontros por turma, carga horária, leitura dos YAML | 15, 16 |
| `acad/cronograma/importar.py`, `classificar.py`, `exportar_planilha.py` | transição `.xlsx` ↔ YAML | 17, 29 |
| `acad/planejamento/distribuir.py`, `replanejar.py`, `status.py` | distribuição, diff, ciclo de status | 18, 19, 25 |
| `acad/manifestos/*` | hashes e manifestos | 20 |
| `acad/validacao/regras.py`, `validar.py` | regras de planejamento e orquestração | 21, 22 |
| `acad/perfil/detectar.py` | configuração guiada (núcleo) | 23 |
| `acad/geracao/*`, `modelos/*` | aula, slides (BLOQUEADA D4), avaliação, LaTeX | 24, 26, 27 |
| `acad/exportadores/ics.py` | ICS | 28 |
| `scripts/acad.py` | lançador sem dependências | 30 |
| `skills/*/SKILL.md`, `scripts/trechos/`, `scripts/sincronizar-skills.py`, `acad/plataformas/skills.py`, `AGENTS.md` | skills | 31, 32 |
| manifestos dos hosts, `acad/plataformas/manifestos.py`, `scripts/validar-manifestos.py` | adaptadores | 33–36 |
| `scripts/sincronizar-versao.py`, `acad/plataformas/versao.py` | versão única | 37 |
| `scripts/empacotar-chatgpt.py`, `acad/plataformas/chatgpt.py` | zip ChatGPT | 38 |
| `INSTALAR.md`, `README.md` | documentação | 39 |
| `acad/mcp.py`, `.mcp.json`, `mcp_config.json` | servidor MCP | 40 |
| `testes/hosts/*` | matriz | 41, 42 |
---

## Fase 0 — Fundação

### Tarefa 1: Pacote Python e ambiente de teste

**Files:**
- Create: `pyproject.toml`, `acad/__init__.py`, `acad/__main__.py`, `testes/__init__.py`, `testes/unidade/__init__.py`, `testes/unidade/test_pacote.py`, `testes/conftest.py`
- Modify: `.gitignore`

**Interfaces:**
- Produces: `acad.__version__: str = "0.1.0"`; `python -m acad` chama `acad.cli.main()` (criado na Tarefa 12; até lá `__main__` só imprime a versão).

- [x] **Step 1: Criar venv e instalar pytest**

Run: `python -m venv .venv && .venv/Scripts/python -m pip install --upgrade pip pytest`
Expected: termina sem erro.

- [x] **Step 2: Escrever o teste que falha**

```python
# testes/unidade/test_pacote.py
import subprocess, sys
import acad

def test_versao_definida():
    assert acad.__version__ == "0.1.0"

def test_modulo_executavel():
    r = subprocess.run([sys.executable, "-m", "acad", "--versao"], capture_output=True, text=True)
    assert r.returncode == 0
    assert "0.1.0" in r.stdout
```

```python
# testes/conftest.py
import pytest

def pytest_configure(config):
    for nome, desc in [("drive", "lê G:\\Meu Drive\\Fasoft em modo leitura"),
                       ("hosts", "exige a CLI de um host instalada"),
                       ("latex", "exige tectonic ou pdflatex")]:
        config.addinivalue_line("markers", f"{nome}: {desc}")

@pytest.fixture(autouse=True)
def dados_isolados(tmp_path, monkeypatch):
    """Estado local do acad sempre em pasta temporária."""
    monkeypatch.setenv("ACAD_DADOS", str(tmp_path / "_dados"))
```

- [x] **Step 3: Rodar e ver falhar**

Run: `.venv/Scripts/python -m pytest testes/unidade/test_pacote.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'acad'`).

- [x] **Step 4: Implementar**

Consultar versões: `.venv/Scripts/python -m pip index versions pyyaml`, idem `jsonschema`, `openpyxl`, `pytest`. Preencher `X.Y` com a última estável.

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "librarius"
version = "0.1.0"
description = "Núcleo acad do plugin Librarius para professores universitários"
requires-python = ">=3.11"
license = { text = "MIT" }
dependencies = [
  "pyyaml>=X.Y,<X+1",
  "jsonschema>=X.Y,<X+1",
  "openpyxl>=X.Y,<X+1",
]

[project.optional-dependencies]
teste = ["pytest>=X.Y,<X+1"]

[project.scripts]
acad = "acad.cli:main"

[tool.setuptools.packages.find]
include = ["acad*"]

[tool.setuptools.package-data]
acad = ["perfil/perfis/*.yaml"]

[tool.pytest.ini_options]
testpaths = ["testes"]
```

```python
# acad/__init__.py
"""Núcleo acad do plugin Librarius."""
__version__ = "0.1.0"
```

```python
# acad/__main__.py
import sys
from acad import __version__

def _main() -> int:
    if "--versao" in sys.argv[1:]:
        print(__version__)
        return 0
    try:
        from acad.cli import main
    except ImportError:
        print(__version__)
        return 0
    return main()

sys.exit(_main())
```

Acrescentar ao `.gitignore`: `.venv/`, `__pycache__/`, `*.egg-info/`, `.pytest_cache/`.

Run: `.venv/Scripts/python -m pip install -e ".[teste]"`

- [x] **Step 5: Rodar e ver passar**

Run: `.venv/Scripts/python -m pytest testes/unidade/test_pacote.py -v`
Expected: 2 passed.

- [x] **Step 6: Commit**

```bash
git add pyproject.toml acad testes .gitignore
git commit -m "chore: pacote acad e ambiente de teste"
```

### Tarefa 2: Envelope de resultado, erros, mensagens, diretório de dados e normalização

**Files:**
- Create: `acad/saida.py`, `acad/erros.py`, `acad/mensagens.py`, `acad/config.py`, `acad/arquivos/__init__.py`, `acad/arquivos/caminhos.py`
- Test: `testes/unidade/test_saida.py`, `testes/unidade/test_config.py`, `testes/unidade/test_caminhos.py`

**Interfaces:**
- Produces:
  - `Resultado(ok: bool, mensagem: str, dados: dict = {}, avisos: list[str] = [], erros: list[dict] = [], proposta: dict | None = None)` com `.para_json() -> str` e `.para_texto() -> str`.
  - `ErroAcad(codigo: str, mensagem: str, detalhe_tecnico: str = "", saida: int = 2)`; `saida` ∈ {1,2,3,4} (spec §8).
  - `mensagens.msg(codigo: str, **kw) -> str`; `mensagens.TERMOS_PROIBIDOS: tuple[str, ...]`; `mensagens.contem_termo_tecnico(texto) -> bool`.
  - `config.dir_dados() -> Path` (ordem: `ACAD_DADOS`, `CLAUDE_PLUGIN_DATA`, `%LOCALAPPDATA%\librarius`, `~/.local/share/librarius`); `config.registrar_detalhe(texto: str) -> None` (anexa a `dir_dados()/registro.log`).
  - `caminhos.nfc(t: str) -> str`; `caminhos.sem_acento(t: str) -> str` (NFC→NFD, remove marcas, minúsculas); `caminhos.relativo_posix(p: Path, base: Path) -> str` (NFC, `/`).

- [x] **Step 1: Escrever os testes que falham**

```python
# testes/unidade/test_saida.py
import json
from acad.saida import Resultado
from acad.erros import ErroAcad
from acad import mensagens

def test_envelope_json_tem_campos_da_spec():
    r = Resultado(ok=True, mensagem="Tudo certo.")
    d = json.loads(r.para_json())
    assert set(d) == {"ok", "mensagem", "dados", "avisos", "erros", "proposta"}
    assert d["ok"] is True and d["proposta"] is None

def test_json_preserva_acentos():
    assert "Período" in Resultado(ok=True, mensagem="Período").para_json()

def test_texto_mostra_mensagem_e_avisos():
    t = Resultado(ok=True, mensagem="Pronto.", avisos=["Falta o slide."]).para_texto()
    assert "Pronto." in t and "Falta o slide." in t

def test_erro_acad_guarda_codigo_e_saida():
    e = ErroAcad("raiz-nao-encontrada", "Não achei a pasta.", "x", saida=3)
    assert (e.codigo, e.saida, str(e)) == ("raiz-nao-encontrada", 3, "Não achei a pasta.")

def test_mensagens_do_catalogo_sem_termo_tecnico():
    for codigo, texto in mensagens.MENSAGENS.items():
        assert not mensagens.contem_termo_tecnico(texto), codigo

def test_msg_formata_parametros():
    assert "3" in mensagens.msg("propostas-arquivos", n=3)
```

```python
# testes/unidade/test_config.py
from pathlib import Path
from acad import config

def test_acad_dados_tem_prioridade(tmp_path, monkeypatch):
    monkeypatch.setenv("ACAD_DADOS", str(tmp_path / "a"))
    monkeypatch.setenv("CLAUDE_PLUGIN_DATA", str(tmp_path / "b"))
    assert config.dir_dados() == tmp_path / "a"

def test_claude_plugin_data_quando_sem_acad_dados(tmp_path, monkeypatch):
    monkeypatch.delenv("ACAD_DADOS", raising=False)
    monkeypatch.setenv("CLAUDE_PLUGIN_DATA", str(tmp_path / "b"))
    assert config.dir_dados() == tmp_path / "b"

def test_registro_grava_detalhe(tmp_path):
    config.registrar_detalhe("falha X")
    assert "falha X" in (config.dir_dados() / "registro.log").read_text(encoding="utf-8")
```

```python
# testes/unidade/test_caminhos.py
import unicodedata
from pathlib import Path
from acad.arquivos.caminhos import nfc, sem_acento, relativo_posix

def test_sem_acento_iguala_arvores():
    assert sem_acento("Árvores B") == sem_acento("Arvores b") == "arvores b"

def test_nfc_iguala_formas():
    nfd = unicodedata.normalize("NFD", "Período")
    assert nfc(nfd) == "Período"

def test_relativo_posix(tmp_path):
    p = tmp_path / "04 - ED2" / "02 - Aulas" / "Aula 01 - X.pptx"
    assert relativo_posix(p, tmp_path) == "04 - ED2/02 - Aulas/Aula 01 - X.pptx"
```

- [x] **Step 2: Rodar e ver falhar**

Run: `$PY -m pytest testes/unidade/test_saida.py testes/unidade/test_config.py testes/unidade/test_caminhos.py -v`
Expected: FAIL (módulos inexistentes).

- [x] **Step 3: Implementar**

```python
# acad/saida.py
from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict

@dataclass
class Resultado:
    ok: bool
    mensagem: str
    dados: dict = field(default_factory=dict)
    avisos: list[str] = field(default_factory=list)
    erros: list[dict] = field(default_factory=list)
    proposta: dict | None = None

    def para_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2, default=str)

    def para_texto(self) -> str:
        linhas = [self.mensagem]
        linhas += [f"• {a}" for a in self.avisos]
        linhas += [f"✗ {e['mensagem']}" for e in self.erros]
        if self.proposta:
            linhas.append(self.proposta.get("resumo", ""))
        return "\n".join(l for l in linhas if l)
```

```python
# acad/erros.py
class ErroAcad(Exception):
    """Erro com mensagem simples ao professor; o detalhe técnico vai para o registro."""
    def __init__(self, codigo: str, mensagem: str, detalhe_tecnico: str = "", saida: int = 2):
        super().__init__(mensagem)
        self.codigo, self.mensagem, self.detalhe_tecnico, self.saida = codigo, mensagem, detalhe_tecnico, saida
```

```python
# acad/mensagens.py
"""Catálogo de mensagens ao professor, em português simples."""
import re

TERMOS_PROIBIDOS = ("yaml", "json", "hash", "sha", "schema", "stack", "exception", "traceback", "path", "stdout")

MENSAGENS: dict[str, str] = {
    "tudo-certo": "Tudo certo.",
    "raiz-nao-encontrada": "Não encontrei a pasta dos seus materiais. Me diga onde ela fica.",
    "propostas-arquivos": "Vou mexer em {n} arquivo(s). Posso continuar?",
    "proposta-aplicada": "Pronto, as alterações foram feitas.",
    "nada-para-desfazer": "Não há alteração recente para desfazer.",
    "desfeito": "Desfiz a última alteração.",
    "pastas-protegidas": "{n} pasta(s) com dados de alunos foram protegidas e não foram lidas.",
    "decisao-pendente": "Essa parte ainda depende de uma decisão sua: {assunto}.",
    "python-ausente": "Falta um programa (Python) para eu trabalhar com seus arquivos. Posso instalar para você?",
    "erro-inesperado": "Algo deu errado do meu lado. Anotei os detalhes para o suporte.",
}

def msg(codigo: str, **kw) -> str:
    return MENSAGENS[codigo].format(**kw)

def contem_termo_tecnico(texto: str) -> bool:
    baixo = texto.lower()
    return any(re.search(rf"\b{t}\b", baixo) for t in TERMOS_PROIBIDOS)
```

```python
# acad/config.py
import os
from datetime import datetime
from pathlib import Path

def dir_dados() -> Path:
    for var in ("ACAD_DADOS", "CLAUDE_PLUGIN_DATA"):
        if os.environ.get(var):
            return Path(os.environ[var])
    if os.environ.get("LOCALAPPDATA"):
        return Path(os.environ["LOCALAPPDATA"]) / "librarius"
    return Path.home() / ".local" / "share" / "librarius"

def registrar_detalhe(texto: str) -> None:
    d = dir_dados(); d.mkdir(parents=True, exist_ok=True)
    with open(d / "registro.log", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat(timespec='seconds')} {texto}\n")
```

```python
# acad/arquivos/caminhos.py
import unicodedata
from pathlib import Path

def nfc(t: str) -> str:
    return unicodedata.normalize("NFC", t)

def sem_acento(t: str) -> str:
    d = unicodedata.normalize("NFD", t)
    return "".join(c for c in d if unicodedata.category(c) != "Mn").lower()

def relativo_posix(p: Path, base: Path) -> str:
    return nfc(Path(p).relative_to(base).as_posix())
```

`acad/arquivos/__init__.py` vazio.

- [x] **Step 4: Rodar e ver passar**

Run: `$PY -m pytest testes/unidade -v`
Expected: todos PASS.

- [x] **Step 5: Commit**

```bash
git add acad testes
git commit -m "feat: envelope de resultado, erros e mensagens simples"
```

---

## Fase 1 — Esqueleto e esquemas (briefing §5 e §7)

### Tarefa 3: Esquemas JSON e validador

**Files:**
- Create: `esquemas/{calendario,disciplina,turma,encontro,aula,questao,avaliacao,manifesto,perfil,semestre}.schema.json`, `acad/esquemas.py`
- Test: `testes/unidade/test_esquemas.py`, `testes/unidade/dados/` (YAML de exemplo válidos e inválidos)

**Interfaces:**
- Produces: `esquemas.validar(nome: str, documento: dict) -> list[str]` (lista vazia = válido; cada item em português: "campo `turma.horarios[0].inicio`: formato HH:MM"); `esquemas.carregar_yaml(texto: str) -> dict` (`yaml.safe_load`, datas viram `str` ISO antes de validar); `esquemas.validar_ou_falhar(nome, doc) -> None` (levanta `ErroAcad("esquema-invalido", ..., saida=1)`).
- Os esquemas ficam só em `esquemas/` na raiz do repositório (contrato público). O núcleo roda sempre a partir da raiz do plugin (`PYTHONPATH=<raiz>`, Tarefa 29), então `acad/esquemas.py` os encontra em `Path(__file__).resolve().parents[1] / "esquemas"`.

- [x] **Step 1: Escrever testes que falham**

```python
# testes/unidade/test_esquemas.py
import pytest
from acad import esquemas

TURMA_OK = {"versao_esquema": 1, "turma": {"id": "TA", "disciplina": "ED2", "fuso": "America/Sao_Paulo",
    "horarios": [{"dia_semana": 2, "inicio": "19:00", "fim": "20:40", "sala": "B-204"}],
    "excecoes": [{"tipo": "cancelamento", "data": "2026-10-12", "motivo": "feriado"},
                 {"tipo": "reposicao", "data": "2026-10-17", "inicio": "08:00", "fim": "09:40", "repoe": "2026-10-12"}]}}

DISC_OK = {"versao_esquema": 1, "disciplina": {"codigo": "ED2", "nome": "Estrutura de Dados II",
    "pasta": "04 - Estrutura de Dados 2 - 5º Período", "semestre": "2026-2",
    "carga_horaria": {"valor": 60, "unidade": "hora_relogio", "minutos_hora_aula": None},
    "objetivos": [{"id": "OBJ-01", "descricao": "Implementar árvores balanceadas", "bloom": "aplicar"}],
    "configuracao": {"template_slides": "institucional", "template_provas": "latex-padrao", "idioma": "pt-BR"},
    "planejamento": {"status": "rascunho", "aprovado_em": None}}}

def test_turma_valida():
    assert esquemas.validar("turma", TURMA_OK) == []

def test_reposicao_sem_repoe_invalida():
    doc = {**TURMA_OK, "turma": {**TURMA_OK["turma"], "excecoes": [{"tipo": "reposicao", "data": "2026-10-17", "inicio": "08:00", "fim": "09:40"}]}}
    assert esquemas.validar("turma", doc)

def test_hora_mal_formatada():
    t = {**TURMA_OK["turma"], "horarios": [{"dia_semana": 2, "inicio": "7h", "fim": "20:40"}]}
    erros = esquemas.validar("turma", {**TURMA_OK, "turma": t})
    assert any("inicio" in e for e in erros)

def test_hora_aula_exige_minutos():
    d = {**DISC_OK["disciplina"], "carga_horaria": {"valor": 72, "unidade": "hora_aula", "minutos_hora_aula": None}}
    assert esquemas.validar("disciplina", {**DISC_OK, "disciplina": d})

def test_unidade_nula_aceita_ate_d3():
    d = {**DISC_OK["disciplina"], "carga_horaria": {"valor": 60, "unidade": None, "minutos_hora_aula": None}}
    assert esquemas.validar("disciplina", {**DISC_OK, "disciplina": d}) == []

def test_campo_extra_rejeitado():
    d = {**DISC_OK["disciplina"], "inventado": 1}
    assert esquemas.validar("disciplina", {**DISC_OK, "disciplina": d})

def test_aula_id_formato():
    doc = {"versao_esquema": 1, "disciplina": "ED2", "aulas": [{"id": "Aula 3", "tema": "x", "status": "planejada"}]}
    assert esquemas.validar("aula", doc)

def test_calendario_sabado_letivo_exige_equivalencia():
    doc = {"versao_esquema": 1, "calendario": {"semestre": "2026-2", "inicio": "2026-07-27", "fim": "2026-12-12",
           "fonte": {"tipo": "manual"}, "status": "rascunho", "confirmado_em": None,
           "dias": [{"data": "2026-10-17", "tipo": "sabado-letivo"}], "eventos": []}}
    assert esquemas.validar("calendario", doc)

def test_carregar_yaml_converte_datas():
    assert esquemas.carregar_yaml("d: 2026-10-12\n") == {"d": "2026-10-12"}

@pytest.mark.parametrize("nome", ["calendario", "disciplina", "turma", "encontro", "aula",
                                  "questao", "avaliacao", "manifesto", "perfil", "semestre"])
def test_todo_esquema_existe_e_e_estrito(nome):
    s = esquemas.carregar_esquema(nome)
    assert s["$id"].endswith(f"/esquemas/{nome}.schema.json")
```

- [x] **Step 2: Rodar e ver falhar** — `$PY -m pytest testes/unidade/test_esquemas.py -v` → FAIL.

- [x] **Step 3: Implementar**

Adicionar `jsonschema` já está nas dependências. Escrever os esquemas (draft 2020-12) exatamente com os campos e enums da spec §5. Exemplo completo para `turma` (os demais seguem o mesmo padrão: `additionalProperties: false` em todo objeto, `versao_esquema: {"const": 1}` obrigatório na raiz, padrões `HH:MM` = `^([01]\d|2[0-3]):[0-5]\d$`, data = `^\d{4}-\d{2}-\d{2}$`):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/vnmartinez/librarius/esquemas/turma.schema.json",
  "type": "object", "additionalProperties": false,
  "required": ["versao_esquema", "turma"],
  "properties": {
    "versao_esquema": {"const": 1},
    "turma": {
      "type": "object", "additionalProperties": false,
      "required": ["id", "disciplina", "fuso", "horarios"],
      "properties": {
        "id": {"type": "string", "pattern": "^[A-Z]{1,3}[0-9]?$"},
        "disciplina": {"type": "string", "pattern": "^[A-Z0-9]{2,10}$"},
        "fuso": {"type": "string"},
        "horarios": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/horario"}},
        "excecoes": {"type": "array", "items": {"$ref": "#/$defs/excecao"}}
      }
    }
  },
  "$defs": {
    "hora": {"type": "string", "pattern": "^([01]\\d|2[0-3]):[0-5]\\d$"},
    "data": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
    "horario": {"type": "object", "additionalProperties": false, "required": ["dia_semana", "inicio", "fim"],
      "properties": {"dia_semana": {"type": "integer", "minimum": 1, "maximum": 7},
                     "inicio": {"$ref": "#/$defs/hora"}, "fim": {"$ref": "#/$defs/hora"}, "sala": {"type": "string"}}},
    "excecao": {"type": "object", "additionalProperties": false, "required": ["tipo", "data"],
      "properties": {"tipo": {"enum": ["cancelamento", "reposicao"]}, "data": {"$ref": "#/$defs/data"},
                     "motivo": {"type": "string"}, "inicio": {"$ref": "#/$defs/hora"}, "fim": {"$ref": "#/$defs/hora"},
                     "repoe": {"$ref": "#/$defs/data"}},
      "if": {"properties": {"tipo": {"const": "reposicao"}}},
      "then": {"required": ["inicio", "fim", "repoe"]}}
  }
}
```

Regras específicas a codificar nos outros esquemas: `disciplina.carga_horaria.unidade` ∈ `["hora_relogio","hora_aula",null]` com `if unidade==hora_aula then minutos_hora_aula integer ≥ 1`; `bloom` enum da spec §5.2; `aula.id` `^Aula [0-9]{2}$`, `status` enum de 5 valores, `encontros_necessarios` integer ≥ 1; `encontro.status` `previsto|realizado|cancelado`, `funcao` `conteudo|revisao|avaliacao`, `origem` `horario|reposicao|sabado-letivo|planilha`, `id` `^E[0-9]{2,3}$`; `calendario.dias[].tipo` enum da spec §5.1 com `if tipo in (sabado-letivo, troca-de-dia) then required equivale_a (1–7)`; `manifesto` com `artefatos` (array de string), `gerado_em`, `entradas` (objeto `string → ^sha256:[0-9a-f]{64}$`), `aprovado` (bool), `aprovado_em`, `versao_acad`; `avaliacao.etapa` string `^N[0-9]$`, `semente` integer; `questao.tipo` enum da spec §5.2; `perfil` com os campos da spec §5.3; `semestre` = `configuracao.yaml` (`perfil`, `raiz_workspace`, `semestre_atual` `^\d{4}-[12]$`, `disciplinas` objeto código → pasta, `turmas` objeto código → lista de ids). O esquema `encontro` descreve o arquivo `encontros-<ID>.yaml` inteiro (`gerado_por`, `gerado_em`, `entradas`, `encontros[]`); o `aula` descreve `aulas.yaml` inteiro.

```python
# acad/esquemas.py
from __future__ import annotations
import datetime as _dt
import json
from functools import lru_cache
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator
from acad.erros import ErroAcad

def _dir_esquemas() -> Path:
    return Path(__file__).resolve().parents[1] / "esquemas"

@lru_cache
def carregar_esquema(nome: str) -> dict:
    return json.loads((_dir_esquemas() / f"{nome}.schema.json").read_text(encoding="utf-8"))

def _datas_para_texto(o):
    if isinstance(o, dict):
        return {k: _datas_para_texto(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_datas_para_texto(v) for v in o]
    if isinstance(o, (_dt.date, _dt.datetime)):
        return o.isoformat()
    return o

def carregar_yaml(texto: str) -> dict:
    return _datas_para_texto(yaml.safe_load(texto) or {})

def validar(nome: str, documento: dict) -> list[str]:
    v = Draft202012Validator(carregar_esquema(nome))
    erros = []
    for e in sorted(v.iter_errors(documento), key=lambda e: list(e.absolute_path)):
        campo = ".".join(str(p) if not isinstance(p, int) else f"[{p}]" for p in e.absolute_path).replace(".[", "[")
        erros.append(f"campo `{campo or '(raiz)'}`: {e.message}")
    return erros

def validar_ou_falhar(nome: str, documento: dict) -> None:
    erros = validar(nome, documento)
    if erros:
        raise ErroAcad("esquema-invalido", "Um arquivo de planejamento está com informação inválida.",
                       "; ".join(erros), saida=1)
```

- [x] **Step 4: Rodar e ver passar** — `$PY -m pytest testes/unidade/test_esquemas.py -v` → PASS.

- [x] **Step 5: Commit** — `git add esquemas acad testes && git commit -m "feat: esquemas dos contratos de dados"`

### Tarefa 4: Perfil institucional Fasoft

**Files:**
- Create: `acad/perfil/__init__.py`, `acad/perfil/perfil.py`, `acad/perfil/perfis/fasoft.yaml`
- Test: `testes/unidade/test_perfil.py`

**Interfaces:**
- Consumes: `esquemas.validar_ou_falhar("perfil", doc)`.
- Produces: `@dataclass(frozen=True) Perfil` com `id, instituicao, disciplina_pasta: re.Pattern, subpastas_disciplina: tuple[str,...], pasta_avaliacoes: re.Pattern, pasta_modelos: re.Pattern, pasta_arquivo: str ("99 - Arquivo"), etapas_avaliacao: tuple[str,...], re_aula: re.Pattern, re_lista: re.Pattern, re_pasta: re.Pattern, sufixos_proibidos: tuple[re.Pattern,...], unidade_carga: str|None, minutos_hora_aula: int|None, exclusao: tuple[str,...]`; `carregar_perfil(id: str = "fasoft") -> Perfil`.

- [x] **Step 1: Teste que falha**

```python
# testes/unidade/test_perfil.py
from acad.perfil.perfil import carregar_perfil

def test_perfil_fasoft_carrega():
    p = carregar_perfil("fasoft")
    assert p.subpastas_disciplina[0] == "01 - Planejamento"
    assert p.pasta_arquivo == "99 - Arquivo"
    assert p.etapas_avaliacao == ("N1", "N2", "N3")

def test_regex_disciplina_extrai_partes():
    m = carregar_perfil().disciplina_pasta.match("04 - Estrutura de Dados 2 - 5º Período")
    assert m["num"] == "04" and m["nome"] == "Estrutura de Dados 2" and m["periodo"] == "5º Período"

def test_unidade_carga_pendente_d3():
    p = carregar_perfil()
    assert p.unidade_carga is None and p.minutos_hora_aula is None

def test_sufixos_proibidos_pegam_casos_reais():
    p = carregar_perfil()
    for nome in ["Aula 18 - Arvores (v2).pptx", "Recepção dos Calouros (1).xlsx",
                 "Cronograma - ED2.xlsx.bak", "Aula 05 - BST - copia.pptx", "Lista_v2.docx", "X (Revisado).docx"]:
        assert any(r.search(nome) for r in p.sufixos_proibidos), nome
    assert not any(r.search("Aula 05 - Árvores Binárias de Busca (BST).pptx") for r in p.sufixos_proibidos)

def test_exclusao_cobre_dados_de_aluno():
    ex = carregar_perfil().exclusao
    assert "*Notas*" in ex and "* - TFC*/02 - Alunos" in ex
```

- [x] **Step 2: Rodar e ver falhar.**

- [x] **Step 3: Implementar**

```yaml
# acad/perfil/perfis/fasoft.yaml
versao_esquema: 1
perfil:
  id: fasoft
  instituicao: "UniRV — Fasoft"
  semestre_pasta: "{ano}/{Primeiro|Segundo} Semestre"
  disciplina_pasta: '^(?P<num>\d{2}) - (?P<nome>.+?)(?: - (?P<periodo>\d+º Período|Turma Especial))?$'
  subpastas_disciplina: ["01 - Planejamento", "02 - Aulas", "03 - Atividades e Listas",
                         "04 - Projetos e Entregáveis", "05 - Materiais de Referência",
                         "06 - Código e Exemplos", "99 - Arquivo"]
  pasta_arquivo: "99 - Arquivo"
  pasta_avaliacoes: '^\d{2} - Avaliações$'
  pasta_modelos: '^\d{2} - Modelos$'
  etapas_avaliacao: [N1, N2, N3]
  nomenclatura:
    aula: '^Aula \d{2} - '
    lista: '^(Lista|Atividade|Aula) \d{2} - '
    pasta: '^\d{2} - '
    sufixos_proibidos: ['\(Revisado\)', '_v\d+\b', '\(v\d+\)', ' - [Cc][oó]pia\b', ' \(\d+\)\.', '\.bak$']
  carga_horaria: { unidade: null, minutos_hora_aula: null }
  exclusao:
    - "*Notas*"
    - "* - TFC*/02 - Alunos"
    - "*Relatórios*"
    - "*/04 - Projetos e Entregáveis"
    - "* - Estágio"
```

Os padrões de `exclusao` são casados contra o caminho relativo à raiz do semestre, sem diferenciar maiúsculas, por `fnmatch` em cada prefixo do caminho (Tarefa 5). Ajustar o esquema `perfil` da Tarefa 3 se algum campo acima faltar nele (o teste da Tarefa 3 continua passando).

```python
# acad/perfil/perfil.py
from __future__ import annotations
import re
from dataclasses import dataclass
from importlib import resources
from acad import esquemas

@dataclass(frozen=True)
class Perfil:
    id: str
    instituicao: str
    disciplina_pasta: re.Pattern
    subpastas_disciplina: tuple[str, ...]
    pasta_arquivo: str
    pasta_avaliacoes: re.Pattern
    pasta_modelos: re.Pattern
    etapas_avaliacao: tuple[str, ...]
    re_aula: re.Pattern
    re_lista: re.Pattern
    re_pasta: re.Pattern
    sufixos_proibidos: tuple[re.Pattern, ...]
    unidade_carga: str | None
    minutos_hora_aula: int | None
    exclusao: tuple[str, ...]

def carregar_perfil(id: str = "fasoft") -> Perfil:
    texto = (resources.files("acad.perfil") / "perfis" / f"{id}.yaml").read_text(encoding="utf-8")
    doc = esquemas.carregar_yaml(texto)
    esquemas.validar_ou_falhar("perfil", doc)
    p, n = doc["perfil"], doc["perfil"]["nomenclatura"]
    return Perfil(
        id=p["id"], instituicao=p["instituicao"],
        disciplina_pasta=re.compile(p["disciplina_pasta"]),
        subpastas_disciplina=tuple(p["subpastas_disciplina"]), pasta_arquivo=p["pasta_arquivo"],
        pasta_avaliacoes=re.compile(p["pasta_avaliacoes"]), pasta_modelos=re.compile(p["pasta_modelos"]),
        etapas_avaliacao=tuple(p["etapas_avaliacao"]),
        re_aula=re.compile(n["aula"]), re_lista=re.compile(n["lista"]), re_pasta=re.compile(n["pasta"]),
        sufixos_proibidos=tuple(re.compile(s) for s in n["sufixos_proibidos"]),
        unidade_carga=p["carga_horaria"]["unidade"], minutos_hora_aula=p["carga_horaria"]["minutos_hora_aula"],
        exclusao=tuple(p["exclusao"]),
    )
```

`acad/perfil/__init__.py` vazio. Confirmar `package-data` inclui `perfil/perfis/*.yaml` e reinstalar: `$PY -m pip install -e ".[teste]"`.

- [x] **Step 4: Rodar e ver passar.**
- [x] **Step 5: Commit** — `git commit -m "feat: perfil institucional Fasoft"`

### Tarefa 5: Workspace com lista de exclusão (única porta de leitura)

**Files:**
- Create: `acad/arquivos/privacidade.py`
- Test: `testes/unidade/test_privacidade.py`, `testes/conftest.py` (fixture `semestre_sintetico`)

**Interfaces:**
- Consumes: `Perfil.exclusao`, `caminhos.relativo_posix`, `caminhos.nfc`.
- Produces: `class Workspace(raiz: Path, exclusao: Iterable[str])` com `raiz: Path`, `excluido(caminho: Path) -> bool`, `listar(pasta: Path) -> list[Path]` (ordenado por nome NFC, sem itens excluídos, sem `~$*`), `percorrer(pasta: Path) -> Iterator[Path]` (recursivo, não desce em excluídos), `ler_bytes(caminho) -> bytes`, `ler_texto(caminho) -> str`, `existe(caminho) -> bool`, `protegidas: set[str]` (caminhos relativos das **pastas** protegidas encontradas ao listar; arquivos protegidos só são pulados; nunca o conteúdo). Qualquer `ler_*` em caminho excluído levanta `ErroAcad("caminho-protegido", ..., saida=2)`.
- Fixture `semestre_sintetico(tmp_path) -> Path` cria uma árvore mínima (usada em várias tarefas):

```
<tmp>/fasoft/AGENTS.md ("# Fasoft - Diretrizes")
<tmp>/fasoft/2026/Segundo Semestre/
  README.md (lista 00, 01 - Disc A - 3º Período, 08 - Avaliações, 09 - Modelos)
  2026 - Notas N1.gsheet
  00 - Administração Acadêmica/
  01 - Disc A - 3º Período/{01 - Planejamento,02 - Aulas,03 - Atividades e Listas,04 - Projetos e Entregáveis/entrega-aluno.txt,05 - Materiais de Referência,06 - Código e Exemplos,99 - Arquivo}
  07 - TFC 1/02 - Alunos/Fulano/tcc.docx
  08 - Avaliações/{N1,N2,N3}
  09 - Modelos/
  11-Relatórios/rel.docx
```

- [x] **Step 1: Testes que falham**

```python
# testes/conftest.py  (acrescentar)
from pathlib import Path

def _mk(p: Path, conteudo: str = ""):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(conteudo, encoding="utf-8")

@pytest.fixture
def semestre_sintetico(tmp_path) -> Path:
    raiz = tmp_path / "fasoft"
    _mk(raiz / "AGENTS.md", "# Fasoft - Diretrizes do Projeto\n")
    s = raiz / "2026" / "Segundo Semestre"
    _mk(s / "README.md", "```text\nSegundo Semestre/\n├── 00 - Administração Acadêmica/\n├── 01 - Disc A - 3º Período/\n├── 08 - Avaliações/\n└── 09 - Modelos/\n```\n")
    _mk(s / "2026 - Notas N1.gsheet", "{}")
    (s / "00 - Administração Acadêmica").mkdir(parents=True)
    d = s / "01 - Disc A - 3º Período"
    for sub in ["01 - Planejamento", "02 - Aulas", "03 - Atividades e Listas", "05 - Materiais de Referência",
                "06 - Código e Exemplos", "99 - Arquivo"]:
        (d / sub).mkdir(parents=True)
    _mk(d / "04 - Projetos e Entregáveis" / "entrega-aluno.txt", "nome do aluno")
    _mk(s / "07 - TFC 1" / "02 - Alunos" / "Fulano" / "tcc.docx", "x")
    for n in ["N1", "N2", "N3"]:
        (s / "08 - Avaliações" / n).mkdir(parents=True)
    (s / "09 - Modelos").mkdir()
    _mk(s / "11-Relatórios" / "rel.docx", "x")
    return s
```

```python
# testes/unidade/test_privacidade.py
import builtins, os
import pytest
from acad.arquivos.privacidade import Workspace
from acad.perfil.perfil import carregar_perfil
from acad.erros import ErroAcad

@pytest.fixture
def ws(semestre_sintetico):
    return Workspace(semestre_sintetico, carregar_perfil().exclusao)

def test_excluidos_reconhecidos(ws, semestre_sintetico):
    s = semestre_sintetico
    assert ws.excluido(s / "2026 - Notas N1.gsheet")
    assert ws.excluido(s / "07 - TFC 1" / "02 - Alunos" / "Fulano" / "tcc.docx")
    assert ws.excluido(s / "11-Relatórios" / "rel.docx")
    assert ws.excluido(s / "01 - Disc A - 3º Período" / "04 - Projetos e Entregáveis" / "entrega-aluno.txt")
    assert not ws.excluido(s / "01 - Disc A - 3º Período" / "02 - Aulas")

def test_percorrer_nao_entra_em_excluidos(ws, semestre_sintetico, monkeypatch):
    tocados = []
    real_scandir = os.scandir
    def espiao(p="."):
        tocados.append(str(p)); return real_scandir(p)
    monkeypatch.setattr(os, "scandir", espiao)
    nomes = {p.name for p in ws.percorrer(semestre_sintetico)}
    assert "Fulano" not in nomes and "tcc.docx" not in nomes and "rel.docx" not in nomes
    assert not any("02 - Alunos" in t or "Relatórios" in t or "Projetos e Entregáveis" in t for t in tocados)

def test_ler_excluido_falha_sem_abrir(ws, semestre_sintetico, monkeypatch):
    abertos = []
    real_open = builtins.open
    monkeypatch.setattr(builtins, "open", lambda f, *a, **k: (abertos.append(str(f)), real_open(f, *a, **k))[1])
    with pytest.raises(ErroAcad) as e:
        ws.ler_bytes(semestre_sintetico / "2026 - Notas N1.gsheet")
    assert e.value.codigo == "caminho-protegido"
    assert not any("Notas" in a for a in abertos)

def test_protegidas_contabilizadas(ws, semestre_sintetico):
    list(ws.percorrer(semestre_sintetico))
    assert "07 - TFC 1/02 - Alunos" in ws.protegidas
    assert not any("Fulano" in p for p in ws.protegidas)

def test_ignora_bloqueio_do_office(ws, semestre_sintetico):
    (semestre_sintetico / "01 - Disc A - 3º Período" / "02 - Aulas" / "~$Aula 01 - X.pptx").write_text("")
    assert ws.listar(semestre_sintetico / "01 - Disc A - 3º Período" / "02 - Aulas") == []
```

- [x] **Step 2: Rodar e ver falhar.**

- [x] **Step 3: Implementar**

```python
# acad/arquivos/privacidade.py
from __future__ import annotations
import fnmatch, os
from pathlib import Path
from typing import Iterable, Iterator
from acad.arquivos.caminhos import nfc, relativo_posix
from acad.erros import ErroAcad

class Workspace:
    """Única porta de leitura e listagem do workspace do professor."""

    def __init__(self, raiz: Path, exclusao: Iterable[str]):
        self.raiz = Path(raiz)
        self._padroes = tuple(nfc(p).lower() for p in exclusao)
        self.protegidas: set[str] = set()

    def _rel(self, caminho: Path) -> str | None:
        try:
            return relativo_posix(Path(caminho), self.raiz)
        except ValueError:
            return None

    def excluido(self, caminho: Path) -> bool:
        rel = self._rel(caminho)
        if rel is None or rel == ".":
            return False
        partes = rel.lower().split("/")
        for i in range(1, len(partes) + 1):
            prefixo, nome = "/".join(partes[:i]), partes[i - 1]
            for p in self._padroes:
                alvo = prefixo if "/" in p else nome   # padrão com "/" casa o caminho; sem "/" casa o nome
                if fnmatch.fnmatchcase(alvo, p):
                    return True
        return False

    def _primeiro_protegido(self, caminho: Path) -> str:
        partes = self._rel(caminho).split("/")
        for i in range(1, len(partes) + 1):
            if self.excluido(self.raiz.joinpath(*partes[:i])):
                return "/".join(partes[:i])
        return "/".join(partes)

    def listar(self, pasta: Path) -> list[Path]:
        pasta = Path(pasta)
        if self.excluido(pasta):
            raise ErroAcad("caminho-protegido", "Essa pasta guarda dados de alunos e não é lida.", str(pasta))
        itens = []
        with os.scandir(pasta) as it:
            for e in it:
                p = pasta / e.name
                if e.name.startswith("~$"):
                    continue
                if self.excluido(p):
                    if e.is_dir():        # só pastas entram na contagem; o conteúdo nunca é lido
                        self.protegidas.add(self._primeiro_protegido(p))
                    continue
                itens.append(p)
        return sorted(itens, key=lambda p: nfc(p.name))

    def percorrer(self, pasta: Path) -> Iterator[Path]:
        for p in self.listar(pasta):
            yield p
            if p.is_dir():
                yield from self.percorrer(p)

    def _checar(self, caminho: Path) -> Path:
        if self.excluido(caminho):
            raise ErroAcad("caminho-protegido", "Esse arquivo guarda dados de alunos e não é lido.", str(caminho))
        return Path(caminho)

    def ler_bytes(self, caminho: Path) -> bytes:
        with open(self._checar(caminho), "rb") as f:
            return f.read()

    def ler_texto(self, caminho: Path) -> str:
        return self.ler_bytes(caminho).decode("utf-8")

    def existe(self, caminho: Path) -> bool:
        return not self.excluido(caminho) and Path(caminho).exists()
```

Observação: `fnmatch` deixa `*` casar `/`; por isso `*/04 - Projetos e Entregáveis` pega a pasta em qualquer disciplina. Tudo é comparado em minúsculas e NFC.

- [x] **Step 4: Rodar e ver passar** — `$PY -m pytest testes/unidade/test_privacidade.py -v`.
- [x] **Step 5: Commit** — `git commit -m "feat: workspace com lista de exclusão de dados de alunos"`

### Tarefa 6: Amostras reais anonimizadas e oráculo da skill `cronograma`

**Files:**
- Create: `testes/ferramentas/espelhar-amostras.py`, `testes/amostras/fasoft/**` (gerado), `testes/referencia/verificar_cronograma.py` (cópia), `testes/referencia/LEIA-ME.md`, `testes/unidade/test_amostras.py`

**Interfaces:**
- Consumes: `Workspace`, `carregar_perfil`.
- Produces: árvore `testes/amostras/fasoft/` com `AGENTS.md`, `2026/Segundo Semestre/README.md`, e espelho de nomes (arquivos vazios) de `00 - Administração Acadêmica`, `04 - Estrutura de Dados 2 - 5º Período` (exceto `04 - Projetos e Entregáveis` conteúdo, pela exclusão) e `09 - Modelos` (sem descer em `node_modules`, `assets`, `referencia`); conteúdo real só de `Cronograma - Estrutura de Dados 2.xlsx`. Constante de teste `AMOSTRA = Path("testes/amostras/fasoft")`.

- [x] **Step 1: Teste que falha**

```python
# testes/unidade/test_amostras.py
from pathlib import Path
import openpyxl

AMOSTRA = Path(__file__).resolve().parents[1] / "amostras" / "fasoft"
SEM = AMOSTRA / "2026" / "Segundo Semestre"
ED2 = SEM / "04 - Estrutura de Dados 2 - 5º Período"

def test_estrutura_espelhada():
    assert (AMOSTRA / "AGENTS.md").read_text(encoding="utf-8").count("Fasoft") >= 1
    assert (ED2 / "02 - Aulas" / "Aula 01 - Apresentação da Disciplina.pptx").exists()
    assert (ED2 / "01 - Planejamento" / "Cronograma - Estrutura de Dados 2.xlsx.bak").exists()

def test_espelho_sem_conteudo_exceto_cronograma():
    for p in ED2.rglob("*"):
        if p.is_file() and p.name != "Cronograma - Estrutura de Dados 2.xlsx":
            assert p.stat().st_size == 0, p

def test_cronograma_real_legivel():
    wb = openpyxl.load_workbook(ED2 / "01 - Planejamento" / "Cronograma - Estrutura de Dados 2.xlsx", data_only=True)
    ws = wb.active
    assert ws.cell(3, 3).value == "Datas" and ws.cell(4, 4).value == "Aula 01"

def test_nenhum_dado_de_aluno_nem_logo():
    nomes = [p.as_posix() for p in AMOSTRA.rglob("*")]
    assert not any("Notas" in n or "02 - Alunos" in n or "Relatórios" in n for n in nomes)
    assert not any(n.lower().endswith((".png", ".jpg")) for n in nomes)

def test_oraculo_copiado():
    assert (Path(__file__).resolve().parents[1] / "referencia" / "verificar_cronograma.py").exists()
```

- [x] **Step 2: Rodar e ver falhar.**

- [x] **Step 3: Implementar o espelhador (só lê a origem)**

```python
# testes/ferramentas/espelhar-amostras.py
"""Copia NOMES (arquivos vazios) de partes do workspace real para testes/amostras.
Somente leitura na origem. Uso: python testes/ferramentas/espelhar-amostras.py "G:\\Meu Drive\\Fasoft"
"""
import shutil, sys
from pathlib import Path
from acad.arquivos.privacidade import Workspace
from acad.perfil.perfil import carregar_perfil

SEMESTRE = Path("2026") / "Segundo Semestre"
PASTAS = ["00 - Administração Acadêmica", "04 - Estrutura de Dados 2 - 5º Período", "09 - Modelos"]
NAO_DESCER = {"node_modules", "assets", "referencia", ".git"}
COM_CONTEUDO = {"Cronograma - Estrutura de Dados 2.xlsx"}
IGNORAR_EXT = {".png", ".jpg", ".jpeg"}

def espelhar(origem_fasoft: Path, destino_fasoft: Path) -> None:
    if destino_fasoft.resolve().is_relative_to(origem_fasoft.resolve()):
        raise SystemExit("destino dentro da origem: recusado")
    if destino_fasoft.exists():
        shutil.rmtree(destino_fasoft)
    ws = Workspace(origem_fasoft / SEMESTRE, carregar_perfil().exclusao)
    (destino_fasoft / SEMESTRE).mkdir(parents=True)
    (destino_fasoft / "AGENTS.md").write_bytes((origem_fasoft / "AGENTS.md").read_bytes())
    (destino_fasoft / SEMESTRE / "README.md").write_bytes(ws.ler_bytes(origem_fasoft / SEMESTRE / "README.md"))
    def copiar(pasta: Path):
        for p in ws.listar(pasta):
            rel = p.relative_to(origem_fasoft)
            alvo = destino_fasoft / rel
            if p.is_dir():
                alvo.mkdir(parents=True, exist_ok=True)
                if p.name not in NAO_DESCER:
                    copiar(p)
            elif p.suffix.lower() not in IGNORAR_EXT:
                alvo.parent.mkdir(parents=True, exist_ok=True)
                alvo.write_bytes(ws.ler_bytes(p) if p.name in COM_CONTEUDO else b"")
    for nome in PASTAS:
        (destino_fasoft / SEMESTRE / nome).mkdir(parents=True, exist_ok=True)
        copiar(origem_fasoft / SEMESTRE / nome)

if __name__ == "__main__":
    espelhar(Path(sys.argv[1]), Path(__file__).resolve().parents[1] / "amostras" / "fasoft")
```

Run: `$PY testes/ferramentas/espelhar-amostras.py "G:\Meu Drive\Fasoft"`
Depois: `cp "/g/Meu Drive/Fasoft/.agents/skills/cronograma/scripts/verificar_cronograma.py" testes/referencia/verificar_cronograma.py` (leitura da origem; cópia sem alteração).
`testes/referencia/LEIA-ME.md`: "Cópia sem alteração do script da skill `cronograma` do professor (Drive, `.agents/skills/cronograma/scripts/`), copiada em <data>. É o oráculo dos testes de paridade da Tarefa 10. Não editar."
Conferir com `git status` que nada fora de `testes/` mudou e que nenhum `.png` foi copiado.

- [x] **Step 4: Rodar e ver passar** — `$PY -m pytest testes/unidade/test_amostras.py -v`.
- [x] **Step 5: Commit** — `git add testes && git commit -m "test: amostras espelhadas do Drive e oráculo da skill cronograma"`

---

## Fase 2 — Núcleo `acad` com `acad validar` e testes sobre amostras reais

### Tarefa 7: Achados e regras de nomenclatura

**Files:**
- Create: `acad/validacao/__init__.py`, `acad/validacao/achados.py`, `acad/validacao/nomenclatura.py`
- Test: `testes/unidade/test_nomenclatura.py`

**Interfaces:**
- Consumes: `Workspace`, `Perfil`.
- Produces:
  - `@dataclass(frozen=True) Achado(codigo: str, nivel: Literal["erro","aviso","info"], mensagem: str, caminho: str = "")`, `Achado.para_dict() -> dict`.
  - `disciplinas(ws: Workspace, semestre: Path, perfil: Perfil) -> list[Path]` (pastas do semestre que casam `perfil.disciplina_pasta` e não são `pasta_avaliacoes`/`pasta_modelos`/excluídas).
  - `validar_nomes(ws, semestre: Path, perfil) -> list[Achado]` com os códigos `nome-aula-sem-prefixo`, `nome-lista-sem-prefixo`, `pasta-sem-prefixo`, `sufixo-proibido` (spec §9).

Regras exatas:
- `02 - Aulas`: todo arquivo direto (não pasta) que não casa `perfil.re_aula` → `nome-aula-sem-prefixo` (erro). Toda subpasta direta que não casa `re_pasta` → `pasta-sem-prefixo` (erro).
- `03 - Atividades e Listas`: arquivo que não casa `re_lista` → `nome-lista-sem-prefixo` (erro).
- Subpastas de 1º nível de cada disciplina que não casam `re_pasta` → `pasta-sem-prefixo`.
- Pastas de 1º nível do semestre (inclusive nomes em `ws.protegidas`, que são só nomes) que não casam `re_pasta` → `pasta-sem-prefixo`.
- Qualquer arquivo do semestre fora de `<…>/99 - Arquivo/**` cujo nome casa algum `sufixos_proibidos` → `sufixo-proibido` (erro).
- `06 - Código e Exemplos/**` não tem regra de prefixo (convenção `aula-NN-*`).

- [x] **Step 1: Testes que falham**

```python
# testes/unidade/test_nomenclatura.py
from pathlib import Path
import pytest
from acad.arquivos.privacidade import Workspace
from acad.perfil.perfil import carregar_perfil
from acad.validacao.nomenclatura import validar_nomes, disciplinas

AMOSTRA_SEM = Path(__file__).resolve().parents[1] / "amostras" / "fasoft" / "2026" / "Segundo Semestre"

@pytest.fixture
def achados():
    p = carregar_perfil()
    ws = Workspace(AMOSTRA_SEM, p.exclusao)
    return validar_nomes(ws, AMOSTRA_SEM, p)

def _tem(achados, codigo, trecho):
    return any(a.codigo == codigo and trecho in a.caminho for a in achados)

def test_disciplinas_da_amostra():
    p = carregar_perfil()
    nomes = [d.name for d in disciplinas(Workspace(AMOSTRA_SEM, p.exclusao), AMOSTRA_SEM, p)]
    assert nomes == ["04 - Estrutura de Dados 2 - 5º Período"]

def test_divergencias_reais_de_ed2(achados):
    assert _tem(achados, "pasta-sem-prefixo", "02 - Aulas/_ferramentas")
    assert _tem(achados, "sufixo-proibido", "Cronograma - Estrutura de Dados 2.xlsx.bak")
    assert _tem(achados, "sufixo-proibido", "Aula 18 - Arvores Rubro-Negras - Propriedades (v2).pptx")
    assert _tem(achados, "sufixo-proibido", "Recepção dos Calouros (1).xlsx")
    assert _tem(achados, "nome-lista-sem-prefixo", "Lista - BST.pdf")

def test_arquivo_morto_nao_e_cobrado(achados):
    assert not any("99 - Arquivo" in a.caminho for a in achados)

def test_nomes_corretos_nao_geram_achado(achados):
    assert not any("Aula 01 - Apresentação da Disciplina.pptx" in a.caminho for a in achados)
    assert not any("Aula 17 - Atividade 02" in a.caminho for a in achados)

def test_lock_do_office_ignorado(achados):
    assert not any("~$" in a.caminho for a in achados)

def test_mensagens_em_portugues_simples(achados):
    from acad.mensagens import contem_termo_tecnico
    assert achados and all(not contem_termo_tecnico(a.mensagem) for a in achados)

def test_pasta_protegida_avaliada_so_pelo_nome(semestre_sintetico):
    p = carregar_perfil()
    ws = Workspace(semestre_sintetico, p.exclusao)
    list(ws.percorrer(semestre_sintetico))
    a = validar_nomes(ws, semestre_sintetico, p)
    assert any(x.codigo == "pasta-sem-prefixo" and x.caminho == "11-Relatórios" for x in a)
```

- [x] **Step 2: Rodar e ver falhar.**

- [x] **Step 3: Implementar**

```python
# acad/validacao/achados.py
from dataclasses import dataclass, asdict
from typing import Literal

@dataclass(frozen=True)
class Achado:
    codigo: str
    nivel: Literal["erro", "aviso", "info"]
    mensagem: str
    caminho: str = ""

    def para_dict(self) -> dict:
        return asdict(self)
```

```python
# acad/validacao/nomenclatura.py
from __future__ import annotations
from pathlib import Path
from acad.arquivos.caminhos import relativo_posix
from acad.arquivos.privacidade import Workspace
from acad.perfil.perfil import Perfil
from acad.validacao.achados import Achado

def disciplinas(ws: Workspace, semestre: Path, perfil: Perfil) -> list[Path]:
    return [p for p in ws.listar(semestre) if p.is_dir() and perfil.disciplina_pasta.match(p.name)
            and not perfil.pasta_avaliacoes.match(p.name) and not perfil.pasta_modelos.match(p.name)
            and (p / perfil.subpastas_disciplina[0]).is_dir()]

def _no_arquivo_morto(rel: str, perfil: Perfil) -> bool:
    return f"/{perfil.pasta_arquivo}/" in f"/{rel}/"

def validar_nomes(ws: Workspace, semestre: Path, perfil: Perfil) -> list[Achado]:
    achados: list[Achado] = []
    rel = lambda p: relativo_posix(p, semestre)

    topo = ws.listar(semestre)
    for nome in sorted({p.name for p in topo if p.is_dir()} | {r.split("/")[0] for r in ws.protegidas}):
        if not perfil.re_pasta.match(nome):
            achados.append(Achado("pasta-sem-prefixo", "erro",
                f"A pasta “{nome}” não começa com número e traço (ex.: “11 - …”).", nome))

    for disc in disciplinas(ws, semestre, perfil):
        for sub in ws.listar(disc):
            if sub.is_dir() and not perfil.re_pasta.match(sub.name):
                achados.append(Achado("pasta-sem-prefixo", "erro",
                    f"A pasta “{sub.name}” não começa com número e traço.", rel(sub)))
        aulas, listas = disc / "02 - Aulas", disc / "03 - Atividades e Listas"
        if aulas.is_dir():
            for p in ws.listar(aulas):
                if p.is_dir() and not perfil.re_pasta.match(p.name):
                    achados.append(Achado("pasta-sem-prefixo", "erro",
                        f"A pasta “{p.name}” dentro das aulas não começa com número e traço.", rel(p)))
                elif p.is_file() and not perfil.re_aula.match(p.name):
                    achados.append(Achado("nome-aula-sem-prefixo", "erro",
                        f"O arquivo “{p.name}” não começa com “Aula XX - ”.", rel(p)))
        if listas.is_dir():
            for p in ws.listar(listas):
                if p.is_file() and not perfil.re_lista.match(p.name):
                    achados.append(Achado("nome-lista-sem-prefixo", "erro",
                        f"O arquivo “{p.name}” não começa com “Lista XX - ” ou “Atividade XX - ”.", rel(p)))

    for p in ws.percorrer(semestre):
        r = rel(p)
        if p.is_file() and not _no_arquivo_morto(r, perfil) and any(s.search(p.name) for s in perfil.sufixos_proibidos):
            achados.append(Achado("sufixo-proibido", "erro",
                f"“{p.name}” parece uma cópia ou versão antiga. O certo é ficar só o arquivo oficial, "
                f"e a versão antiga ir para “{perfil.pasta_arquivo}”.", r))
    return achados
```

- [x] **Step 4: Rodar e ver passar** — `$PY -m pytest testes/unidade/test_nomenclatura.py -v`.
- [x] **Step 5: Commit** — `git commit -m "feat: regras de nomenclatura do AGENTS.md como validação"`

### Tarefa 8: Regras de estrutura (README do semestre e subpastas padrão)

**Files:**
- Create: `acad/validacao/estrutura.py`
- Test: `testes/unidade/test_estrutura.py`

**Interfaces:**
- Consumes: `disciplinas()`, `Workspace`, `Perfil`, `Achado`.
- Produces: `pastas_do_readme(texto: str) -> list[str]` (nomes do primeiro bloco ```` ```text ```` após "Estrutura principal", ou do primeiro bloco de código se não houver o título; linhas `├── X/` ou `└── X/`, só 1º nível); `validar_estrutura(ws, semestre, perfil) -> list[Achado]` com `readme-desatualizado` (aviso; mensagem cita as pastas que faltam no README e as que o README cita mas não existem) e `subpasta-padrao-ausente` (aviso, por disciplina e subpasta).

- [x] **Step 1: Testes que falham**

```python
# testes/unidade/test_estrutura.py
from acad.arquivos.privacidade import Workspace
from acad.perfil.perfil import carregar_perfil
from acad.validacao.estrutura import pastas_do_readme, validar_estrutura

README = """# Organização
## Estrutura principal
```text
Segundo Semestre/
├── 00 - Administração Acadêmica/
├── 06 - TFC 1/
└── 08 - Modelos/
```
## Estrutura padrão das disciplinas
```text
[Disciplina]/
├── 01 - Planejamento/
```
"""

def test_le_so_estrutura_principal():
    assert pastas_do_readme(README) == ["00 - Administração Acadêmica", "06 - TFC 1", "08 - Modelos"]

def test_readme_desatualizado(semestre_sintetico):
    (semestre_sintetico / "README.md").write_text(README, encoding="utf-8")
    p = carregar_perfil(); ws = Workspace(semestre_sintetico, p.exclusao)
    a = [x for x in validar_estrutura(ws, semestre_sintetico, p) if x.codigo == "readme-desatualizado"]
    assert len(a) == 1
    assert "09 - Modelos" in a[0].mensagem and "08 - Modelos" in a[0].mensagem

def test_subpasta_ausente(semestre_sintetico):
    import shutil
    shutil.rmtree(semestre_sintetico / "01 - Disc A - 3º Período" / "05 - Materiais de Referência")
    p = carregar_perfil(); ws = Workspace(semestre_sintetico, p.exclusao)
    a = validar_estrutura(ws, semestre_sintetico, p)
    assert any(x.codigo == "subpasta-padrao-ausente" and "05 - Materiais de Referência" in x.mensagem for x in a)

def test_pasta_protegida_conta_como_existente(semestre_sintetico):
    p = carregar_perfil(); ws = Workspace(semestre_sintetico, p.exclusao)
    a = validar_estrutura(ws, semestre_sintetico, p)
    msg = next(x.mensagem for x in a if x.codigo == "readme-desatualizado")
    assert "11-Relatórios" in msg        # existe (protegida) e não está no README
```

- [x] **Step 2: Rodar e ver falhar.**

- [x] **Step 3: Implementar**

```python
# acad/validacao/estrutura.py
from __future__ import annotations
import re
from pathlib import Path
from acad.arquivos.caminhos import nfc, relativo_posix
from acad.validacao.achados import Achado
from acad.validacao.nomenclatura import disciplinas

_BLOCO = re.compile(r"```(?:text)?\n(.*?)```", re.S)
_ITEM = re.compile(r"^[├└]── (.+?)/\s*$")

def pastas_do_readme(texto: str) -> list[str]:
    i = texto.find("Estrutura principal")
    m = _BLOCO.search(texto, i if i >= 0 else 0)
    if not m:
        return []
    return [nfc(x[1]) for linha in m.group(1).splitlines() if (x := _ITEM.match(linha.strip()))]

def validar_estrutura(ws, semestre: Path, perfil) -> list[Achado]:
    achados: list[Achado] = []
    readme = semestre / "README.md"
    reais = {p.name for p in ws.listar(semestre) if p.is_dir()} | {r.split("/")[0] for r in ws.protegidas}
    if ws.existe(readme):
        citadas = set(pastas_do_readme(ws.ler_texto(readme)))
        faltam, sobram = sorted(reais - citadas), sorted(citadas - reais)
        if faltam or sobram:
            partes = []
            if faltam: partes.append("existem mas não estão no README: " + ", ".join(faltam))
            if sobram: partes.append("estão no README mas não existem: " + ", ".join(sobram))
            achados.append(Achado("readme-desatualizado", "aviso",
                "O guia de pastas do semestre está desatualizado — " + "; ".join(partes) + ".", "README.md"))
    for disc in disciplinas(ws, semestre, perfil):
        for sub in perfil.subpastas_disciplina:
            if not (disc / sub).is_dir():
                achados.append(Achado("subpasta-padrao-ausente", "aviso",
                    f"A disciplina “{disc.name}” não tem a pasta “{sub}”.", relativo_posix(disc, semestre)))
    return achados
```

- [x] **Step 4: Rodar e ver passar.**
- [x] **Step 5: Commit** — `git commit -m "feat: validação de estrutura do semestre"`

### Tarefa 9: Leitura da planilha de cronograma

**Files:**
- Create: `acad/cronograma/__init__.py`, `acad/cronograma/planilha.py`
- Test: `testes/unidade/test_planilha.py`

**Interfaces:**
- Produces:
  - `@dataclass LinhaCronograma(linha: int, semana: str, data: date | None, aula: str, aula_num: str | None, topico: str)`.
  - `parse_data(valor, ano_padrao: int) -> date | None` — idêntico ao oráculo (`datetime`/`date`, `%d/%m/%Y`, `%Y-%m-%d`, `dd/mm`).
  - `linhas_na_data(conteudo: bytes, alvo: date) -> list[LinhaCronograma]` — **comportamento do oráculo**: aba ativa, linhas 1..min(max_row,149), colunas 1..min(max_col,6), a linha casa se qualquer célula for a data; `aula` = col. 4 ou col. 3; `topico` col. 5; `semana` col. 2 (sem herdar); `aula_num` = `re.search(r"Aula\s*(\d+)", aula, I)` com `zfill(2)`.
  - `ler_cronograma(conteudo: bytes, ano_padrao: int) -> list[LinhaCronograma]` — leitura por cabeçalho (linha com células `Datas` e `Aulas`, sem acento e sem diferenciar maiúsculas; tópicos em `Tópicos`/`Topicos`, semana em `Semanas`), todas as linhas até a primeira sem data e sem aula, **semana herdada** da linha anterior quando vazia. Sem cabeçalho → `ErroAcad("planilha-sem-cabecalho", "Não reconheci as colunas da planilha do cronograma (Datas, Aulas, Tópicos).")`.

- [x] **Step 1: Testes que falham**

```python
# testes/unidade/test_planilha.py
from datetime import date, datetime
from pathlib import Path
import io, openpyxl, pytest
from acad.cronograma.planilha import parse_data, linhas_na_data, ler_cronograma
from acad.erros import ErroAcad

XLSX = (Path(__file__).resolve().parents[1] / "amostras" / "fasoft" / "2026" / "Segundo Semestre"
        / "04 - Estrutura de Dados 2 - 5º Período" / "01 - Planejamento" / "Cronograma - Estrutura de Dados 2.xlsx")

@pytest.mark.parametrize("v,esp", [(datetime(2026, 7, 28), date(2026, 7, 28)), ("28/07/2026", date(2026, 7, 28)),
    ("2026-07-28", date(2026, 7, 28)), ("28/7", date(2026, 7, 28)), ("x", None), (None, None)])
def test_parse_data(v, esp):
    assert parse_data(v, 2026) == esp

def test_linha_do_primeiro_dia():
    [l] = linhas_na_data(XLSX.read_bytes(), date(2026, 7, 28))
    assert (l.linha, l.semana, l.aula, l.aula_num) == (4, "Semana 1", "Aula 01", "01")
    assert l.topico.startswith("Apresenta")

def test_segunda_linha_sem_semana_no_modo_oraculo():
    [l] = linhas_na_data(XLSX.read_bytes(), date(2026, 7, 31))
    assert l.semana == "" and l.aula == "Aula 02"

def test_leitura_por_cabecalho_herda_semana():
    linhas = ler_cronograma(XLSX.read_bytes(), 2026)
    assert linhas[0].data == date(2026, 7, 28)
    assert linhas[1].semana == "Semana 1"
    assert any(l.topico.upper().startswith("PRIMEIRA AVALIA") for l in linhas)

def test_sem_cabecalho():
    wb = openpyxl.Workbook(); wb.active["A1"] = "nada"; b = io.BytesIO(); wb.save(b)
    with pytest.raises(ErroAcad) as e:
        ler_cronograma(b.getvalue(), 2026)
    assert e.value.codigo == "planilha-sem-cabecalho"
```

- [x] **Step 2: Rodar e ver falhar.**

- [x] **Step 3: Implementar**

```python
# acad/cronograma/planilha.py
from __future__ import annotations
import io, re
from dataclasses import dataclass
from datetime import date, datetime
import openpyxl
from acad.arquivos.caminhos import sem_acento
from acad.erros import ErroAcad

@dataclass
class LinhaCronograma:
    linha: int
    semana: str
    data: date | None
    aula: str
    aula_num: str | None
    topico: str

def parse_data(valor, ano_padrao: int) -> date | None:
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if isinstance(valor, str):
        v = valor.strip()
        for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(v, fmt).date()
            except ValueError:
                pass
        m = re.match(r"^(\d{1,2})/(\d{1,2})$", v)
        if m:
            return date(ano_padrao, int(m.group(2)), int(m.group(1)))
    return None

def _num(aula: str) -> str | None:
    m = re.search(r"Aula\s*(\d+)", aula, re.IGNORECASE)
    return m.group(1).zfill(2) if m else None

def _txt(v) -> str:
    return str(v).strip() if v is not None else ""

def _aba(conteudo: bytes):
    return openpyxl.load_workbook(io.BytesIO(conteudo), data_only=True).active

def linhas_na_data(conteudo: bytes, alvo: date) -> list[LinhaCronograma]:
    sh, saida = _aba(conteudo), []
    for r in range(1, min(sh.max_row + 1, 150)):
        if any(parse_data(sh.cell(r, c).value, alvo.year) == alvo for c in range(1, min(sh.max_column + 1, 7))):
            aula = _txt(sh.cell(r, 4).value or sh.cell(r, 3).value or "")
            saida.append(LinhaCronograma(r, _txt(sh.cell(r, 2).value), alvo, aula, _num(aula), _txt(sh.cell(r, 5).value)))
    return saida

def ler_cronograma(conteudo: bytes, ano_padrao: int) -> list[LinhaCronograma]:
    sh = _aba(conteudo)
    cab = None
    for r in range(1, min(sh.max_row, 30) + 1):
        nomes = {sem_acento(_txt(sh.cell(r, c).value)): c for c in range(1, sh.max_column + 1)}
        if "datas" in nomes and "aulas" in nomes:
            cab = (r, nomes); break
    if not cab:
        raise ErroAcad("planilha-sem-cabecalho",
                       "Não reconheci as colunas da planilha do cronograma (Datas, Aulas, Tópicos).")
    r0, n = cab
    cd, ca, ct, cs = n["datas"], n["aulas"], n.get("topicos"), n.get("semanas")
    saida, semana = [], ""
    for r in range(r0 + 1, sh.max_row + 1):
        d = parse_data(sh.cell(r, cd).value, ano_padrao)
        aula = _txt(sh.cell(r, ca).value)
        if d is None and not aula:
            break
        semana = _txt(sh.cell(r, cs).value) if cs and sh.cell(r, cs).value else semana
        saida.append(LinhaCronograma(r, semana, d, aula, _num(aula), _txt(sh.cell(r, ct).value) if ct else ""))
    return saida
```

- [x] **Step 4: Rodar e ver passar.**
- [x] **Step 5: Commit** — `git commit -m "feat: leitura da planilha de cronograma"`

### Tarefa 10: Consulta "aula de hoje" com paridade da skill `cronograma`

**Files:**
- Create: `acad/cronograma/consulta.py`
- Test: `testes/integracao/__init__.py`, `testes/integracao/test_paridade_cronograma.py`, `testes/unidade/test_consulta.py`

**Interfaces:**
- Consumes: `linhas_na_data`, `Workspace`, `sem_acento`.
- Produces:
  - `encontrar_raiz(inicio: Path) -> Path | None` — mesmo algoritmo do oráculo (sobe até achar `AGENTS.md` contendo "Fasoft", ou pasta `fasoft` com `.agents` ou `2026`).
  - `palavras_chave(texto: str) -> list[str]` — `sem_acento`, `\b[a-z]{4,}\b`, stopwords do oráculo.
  - `consultar(raiz: Path, alvo: date, exclusao: Iterable[str]) -> dict` → `{"projeto": str, "data": iso, "quantidade_aulas": int, "aulas": [ {disciplina, disciplina_dir, cronograma_path, semana, aula, aula_num, topico, linha, materiais{slides, slides_divergentes, roteiros_resumos, atividades, atividades_relacionadas, codigos}, tipo} ]}`; `tipo` ∈ `aula | sem-aula | avaliacao` (mesmas palavras-chave do oráculo: `FERIADO RECESSO SETECH SEM AULA`; `AVALIA` em aula/tópico ou `PROVA` no tópico).
  - Varredura: `ws.percorrer(raiz)` pulando pastas cujo nome começa com `.` (o `glob` do oráculo não entra nelas), nomes contendo `Cronograma` e terminando em `.xlsx`, fora de `99 - Arquivo`.
  - `resumo_texto(resultado: dict) -> str` — português simples: "Terça-feira, 28/07/2026 — 1 disciplina com aula." e, por disciplina, "Aula 01 — Apresentação…: slides prontos / slides com outro número / slides faltando; roteiro: …; atividade: …".
- CLI virá na Tarefa 12 (`acad cronograma consultar`).

- [x] **Step 1: Testes que falham**

```python
# testes/integracao/test_paridade_cronograma.py
import json, subprocess, sys
from datetime import date, timedelta
from pathlib import Path
import pytest
from acad.cronograma.consulta import consultar
from acad.cronograma.planilha import ler_cronograma
from acad.perfil.perfil import carregar_perfil

TESTES = Path(__file__).resolve().parents[1]
AMOSTRA = TESTES / "amostras" / "fasoft"
ORACULO = TESTES / "referencia" / "verificar_cronograma.py"
XLSX = AMOSTRA / "2026/Segundo Semestre/04 - Estrutura de Dados 2 - 5º Período/01 - Planejamento/Cronograma - Estrutura de Dados 2.xlsx"
IGNORAR = {"disciplina_dir", "cronograma_path", "tipo"}

def _oraculo(raiz: Path, d: date) -> dict:
    r = subprocess.run([sys.executable, str(ORACULO), "--dir", str(raiz), "--data", d.isoformat(), "--json"],
                       capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(r.stdout)

def _normalizar(res: dict) -> list[dict]:
    saida = []
    for a in res["aulas"]:
        x = {k: v for k, v in a.items() if k not in IGNORAR}
        x["materiais"] = {k: sorted(v) for k, v in a["materiais"].items()}
        saida.append(x)
    return sorted(saida, key=lambda x: (x["disciplina"], x["linha"]))

def _datas():
    ds = {l.data for l in ler_cronograma(XLSX.read_bytes(), 2026) if l.data}
    return sorted(ds | {min(ds) - timedelta(days=1)})          # inclui um dia sem aula

@pytest.mark.parametrize("d", _datas(), ids=str)
def test_paridade_com_oraculo_nas_amostras(d):
    esperado = _oraculo(AMOSTRA, d)
    obtido = consultar(AMOSTRA, d, carregar_perfil().exclusao)
    assert obtido["quantidade_aulas"] == esperado["quantidade_aulas"]
    assert _normalizar(obtido) == _normalizar(esperado)

@pytest.mark.drive
def test_paridade_no_drive_real():
    raiz = Path(r"G:\Meu Drive\Fasoft")
    if not raiz.exists():
        pytest.skip("Drive ausente")
    for d in _datas():
        esperado, obtido = _oraculo(raiz, d), consultar(raiz, d, carregar_perfil().exclusao)
        assert _normalizar(obtido) == _normalizar(esperado), d
```

```python
# testes/unidade/test_consulta.py
from datetime import date
from pathlib import Path
from acad.cronograma.consulta import consultar, encontrar_raiz, palavras_chave, resumo_texto
from acad.perfil.perfil import carregar_perfil

AMOSTRA = Path(__file__).resolve().parents[1] / "amostras" / "fasoft"

def test_encontra_raiz_subindo():
    assert encontrar_raiz(AMOSTRA / "2026" / "Segundo Semestre") == AMOSTRA

def test_palavras_chave_sem_acento_e_stopwords():
    assert palavras_chave("Árvores Binárias de Busca (BST) - Aula") == ["arvores", "binarias", "busca"]

def test_tipo_avaliacao():
    r = consultar(AMOSTRA, date(2026, 9, 1), carregar_perfil().exclusao)
    assert r["aulas"][0]["tipo"] == "avaliacao"

def test_resumo_texto_simples():
    from acad.mensagens import contem_termo_tecnico
    t = resumo_texto(consultar(AMOSTRA, date(2026, 7, 28), carregar_perfil().exclusao))
    assert "28/07/2026" in t and "Estrutura de Dados 2" in t and not contem_termo_tecnico(t)
```

- [x] **Step 2: Rodar e ver falhar** — `$PY -m pytest testes/integracao/test_paridade_cronograma.py testes/unidade/test_consulta.py -v -m "not drive"`.

- [x] **Step 3: Implementar** `acad/cronograma/consulta.py` transcrevendo a lógica do oráculo (`testes/referencia/verificar_cronograma.py`, funções `find_fasoft_root`, `extract_keywords`, `check_materials`, `run_check`) com estas trocas obrigatórias: todo `os.listdir`/`open`/`glob` vira `Workspace.listar`/`ler_bytes`/`percorrer`; `normalize_text` vira `sem_acento`; leitura de planilha usa `linhas_na_data`; resultado inclui `tipo`. Esqueleto:

```python
# acad/cronograma/consulta.py
from __future__ import annotations
import re
from datetime import date
from pathlib import Path
from typing import Iterable
from acad.arquivos.caminhos import sem_acento
from acad.arquivos.privacidade import Workspace
from acad.cronograma.planilha import linhas_na_data

STOPWORDS = {"para", "como", "sobre", "pela", "pelo", "com", "sem", "das", "dos", "uma", "este", "esta",
             "aula", "parte", "secao", "secoes"}
EXT_SLIDE = (".pptx", ".ppt", ".pdf", ".key", ".odp")
EXT_DOC = (".md", ".docx", ".doc", ".txt")
DIAS = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]

def encontrar_raiz(inicio: Path) -> Path | None:
    atual = Path(inicio).resolve()
    while True:
        agents = atual / "AGENTS.md"
        if agents.exists():
            try:
                if "Fasoft" in agents.read_text(encoding="utf-8"):
                    return atual
            except OSError:
                pass
        if atual.name.lower() == "fasoft" and ((atual / ".agents").exists() or (atual / "2026").exists()):
            return atual
        if atual.parent == atual:
            return None
        atual = atual.parent

def palavras_chave(texto: str) -> list[str]:
    return [w for w in re.findall(r"\b[a-z]{4,}\b", sem_acento(texto or "")) if w not in STOPWORDS]

def _materiais(ws: Workspace, disc: Path, num: str | None, topico: str) -> dict:
    m = {k: [] for k in ("slides", "slides_divergentes", "roteiros_resumos", "atividades",
                         "atividades_relacionadas", "codigos")}
    kws = palavras_chave(topico)
    casa = lambda nome: sum(1 for k in kws if k in sem_acento(nome)) >= 2
    aulas = disc / "02 - Aulas"
    if aulas.exists():
        for p in ws.listar(aulas):
            n, baixo = p.name, p.name.lower()
            if num and f"Aula {num}" in n:
                if baixo.endswith(EXT_SLIDE): m["slides"].append(n)
                elif baixo.endswith(EXT_DOC): m["roteiros_resumos"].append(n)
            elif baixo.endswith(EXT_SLIDE) and casa(n):
                m["slides_divergentes"].append(n)
    ativ = disc / "03 - Atividades e Listas"
    if ativ.exists():
        for p in ws.listar(ativ):
            if num and f"Aula {num}" in p.name: m["atividades"].append(p.name)
            elif casa(p.name): m["atividades_relacionadas"].append(p.name)
    cod = disc / "06 - Código e Exemplos"
    if cod.exists():
        m["codigos"] = [p.name for p in ws.listar(cod) if num and f"aula-{num}" in p.name.lower()]
    return m

def _tipo(aula: str, topico: str) -> str:
    a, t = aula.upper(), topico.upper()
    if any(k in a or k in t for k in ("FERIADO", "RECESSO", "SETECH", "SEM AULA")):
        return "sem-aula"
    if "AVALIA" in a or "AVALIA" in t or "PROVA" in t:
        return "avaliacao"
    return "aula"

def _cronogramas(ws: Workspace, pasta: Path):
    for p in ws.listar(pasta):
        if p.is_dir():
            if not p.name.startswith("."):
                yield from _cronogramas(ws, p)
        elif "Cronograma" in p.name and p.name.endswith(".xlsx") and "99 - Arquivo" not in str(p):
            yield p

def consultar(raiz: Path, alvo: date, exclusao: Iterable[str]) -> dict:
    ws = Workspace(raiz, exclusao)
    aulas = []
    for c in _cronogramas(ws, raiz):
        disc = c.parent.parent
        for l in linhas_na_data(ws.ler_bytes(c), alvo):
            aulas.append({"disciplina": disc.name, "disciplina_dir": str(disc), "cronograma_path": str(c),
                          "semana": l.semana, "aula": l.aula, "aula_num": l.aula_num, "topico": l.topico,
                          "linha": l.linha, "materiais": _materiais(ws, disc, l.aula_num, l.topico),
                          "tipo": _tipo(l.aula, l.topico)})
    return {"projeto": str(raiz), "data": alvo.isoformat(), "quantidade_aulas": len(aulas), "aulas": aulas}

def resumo_texto(r: dict) -> str:
    d = date.fromisoformat(r["data"])
    cab = f"{DIAS[d.weekday()]}, {d:%d/%m/%Y} — "
    if not r["aulas"]:
        return cab + "nenhuma aula marcada nos cronogramas."
    linhas = [cab + f"{len(r['aulas'])} disciplina(s) com aula."]
    for a in r["aulas"]:
        nome = re.sub(r"^\d{2} - ", "", a["disciplina"])
        linhas.append(f"\n{nome} — {a['aula']}: {a['topico']}")
        if a["tipo"] == "sem-aula":
            linhas.append("  Sem aula regular (feriado, recesso ou evento)."); continue
        if a["tipo"] == "avaliacao":
            linhas.append("  Dia de avaliação."); continue
        m = a["materiais"]
        if m["slides"]: linhas.append("  Slides: prontos — " + "; ".join(m["slides"]))
        elif m["slides_divergentes"]: linhas.append("  Slides: achei com outro número — " + "; ".join(m["slides_divergentes"]))
        else: linhas.append("  Slides: ainda não existem.")
        if m["roteiros_resumos"]: linhas.append("  Roteiro ou resumo: " + "; ".join(m["roteiros_resumos"]))
        if m["atividades"]: linhas.append("  Atividade: " + "; ".join(m["atividades"]))
        elif m["atividades_relacionadas"]: linhas.append("  Atividades do mesmo tema: " + "; ".join(m["atividades_relacionadas"]))
        if m["codigos"]: linhas.append("  Código de exemplo: " + "; ".join(m["codigos"]))
    return "\n".join(linhas)
```

Se a paridade falhar, a referência é o oráculo: leia a função correspondente nele e ajuste o `acad`, nunca o oráculo.

- [x] **Step 4: Rodar e ver passar** — `$PY -m pytest testes/integracao testes/unidade/test_consulta.py -v -m "not drive"`; depois `$PY -m pytest -m drive -v` (só leitura do Drive).
- [x] **Step 5: Commit** — `git commit -m "feat: consulta de aula do dia com paridade da skill cronograma"`

### Tarefa 11: Escrita por proposta, arquivo morto e desfazer

**Files:**
- Create: `acad/arquivos/escrita.py`, `acad/arquivos/diario.py`
- Modify: `testes/conftest.py` (bloqueio de escrita no Drive)
- Test: `testes/unidade/test_escrita.py`

**Interfaces:**
- Consumes: `config.dir_dados()`, `Perfil.pasta_arquivo`, `ErroAcad`, `mensagens.msg`.
- Produces:
  - `@dataclass Operacao(tipo: Literal["criar","substituir","arquivar","criar-pasta"], destino: str, conteudo: bytes | None = None, resumo: str = "")` — `destino` relativo à raiz, `/`.
  - `criar_proposta(raiz: Path, operacoes: list[Operacao], resumo: str) -> dict` → grava `dir_dados()/propostas/<id>/proposta.json` (`id`, `raiz`, `resumo`, `criada_em`, `itens[{tipo, destino, resumo, sha256}]`) e o conteúdo em `…/<id>/arquivos/<n>`; devolve `{"id", "resumo", "itens": [{tipo, destino, resumo}]}`. Valida: destino dentro da raiz, sem `..`; `criar` exige destino inexistente; `substituir`/`arquivar` exigem existente. `id` = `AAAAMMDD-HHMMSS-<4 hex>`.
  - `aplicar(id: str, perfil) -> list[str]` — grava na ordem; `substituir` e `arquivar` movem o atual para a pasta de arquivo (regra abaixo); registra no diário; recusa se a raiz começar por algum prefixo de `ACAD_BLOQUEAR_ESCRITA` (separados por `;`) → `ErroAcad("escrita-bloqueada", …, saida=2)`; recusa proposta já aplicada.
  - `desfazer(perfil) -> list[str]` — reverte a última proposta aplicada: arquivo criado é removido só se o conteúdo ainda for o gravado (senão é arquivado); arquivo arquivado volta ao lugar; pasta criada vazia é removida.
  - `pasta_arquivo_para(raiz: Path, destino: Path, perfil) -> Path` — ancestral mais próximo (até a raiz) que contém `perfil.pasta_arquivo`; se não houver, `<primeira pasta abaixo da raiz>/<pasta_arquivo>`.
  - Nome no arquivo morto: mesmo nome; se já existir, acrescenta ` - anterior AAAA-MM-DD` antes da extensão (e ` (2)`… se ainda colidir — dentro de `99 - Arquivo` o validador não cobra sufixos).
  - `diario.registrar(entrada: dict)`, `diario.ultima_aplicada() -> dict | None`, `diario.marcar_desfeita(id)` em `dir_dados()/diario.jsonl`.

- [x] **Step 1: Testes que falham**

```python
# testes/conftest.py (acrescentar, autouse)
@pytest.fixture(autouse=True)
def bloquear_drive(monkeypatch):
    monkeypatch.setenv("ACAD_BLOQUEAR_ESCRITA", r"G:\;G:/;/g/")
```

```python
# testes/unidade/test_escrita.py
import pytest
from pathlib import Path
from acad.arquivos.escrita import Operacao, criar_proposta, aplicar, desfazer, pasta_arquivo_para
from acad.perfil.perfil import carregar_perfil
from acad.erros import ErroAcad

P = carregar_perfil()
DISC = "01 - Disc A - 3º Período"

def test_proposta_nao_grava_nada(semestre_sintetico):
    alvo = semestre_sintetico / DISC / "02 - Aulas" / "Aula 01 - Intro.md"
    criar_proposta(semestre_sintetico, [Operacao("criar", f"{DISC}/02 - Aulas/Aula 01 - Intro.md", b"oi", "roteiro")], "1 arquivo")
    assert not alvo.exists()

def test_aplicar_cria(semestre_sintetico):
    pr = criar_proposta(semestre_sintetico, [Operacao("criar", f"{DISC}/02 - Aulas/Aula 01 - Intro.md", b"oi")], "x")
    aplicar(pr["id"], P)
    assert (semestre_sintetico / DISC / "02 - Aulas" / "Aula 01 - Intro.md").read_bytes() == b"oi"

def test_substituir_arquiva_anterior(semestre_sintetico):
    f = semestre_sintetico / DISC / "02 - Aulas" / "Aula 01 - Intro.md"; f.write_bytes(b"v1")
    pr = criar_proposta(semestre_sintetico, [Operacao("substituir", f"{DISC}/02 - Aulas/Aula 01 - Intro.md", b"v2")], "x")
    aplicar(pr["id"], P)
    assert f.read_bytes() == b"v2"
    assert (semestre_sintetico / DISC / "99 - Arquivo" / "Aula 01 - Intro.md").read_bytes() == b"v1"

def test_colisao_no_arquivo_morto(semestre_sintetico):
    f = semestre_sintetico / DISC / "02 - Aulas" / "Aula 01 - Intro.md"; f.write_bytes(b"v1")
    (semestre_sintetico / DISC / "99 - Arquivo" / "Aula 01 - Intro.md").write_bytes(b"v0")
    aplicar(criar_proposta(semestre_sintetico, [Operacao("substituir", f"{DISC}/02 - Aulas/Aula 01 - Intro.md", b"v2")], "x")["id"], P)
    arquivados = sorted(p.name for p in (semestre_sintetico / DISC / "99 - Arquivo").iterdir())
    assert len(arquivados) == 2 and any(" - anterior " in n for n in arquivados)

def test_desfazer_restaura(semestre_sintetico):
    f = semestre_sintetico / DISC / "02 - Aulas" / "Aula 01 - Intro.md"; f.write_bytes(b"v1")
    aplicar(criar_proposta(semestre_sintetico, [Operacao("substituir", f"{DISC}/02 - Aulas/Aula 01 - Intro.md", b"v2"),
                                                Operacao("criar", f"{DISC}/02 - Aulas/Aula 02 - B.md", b"b")], "x")["id"], P)
    desfazer(P)
    assert f.read_bytes() == b"v1"
    assert not (semestre_sintetico / DISC / "02 - Aulas" / "Aula 02 - B.md").exists()
    assert not (semestre_sintetico / DISC / "99 - Arquivo" / "Aula 01 - Intro.md").exists()

def test_desfazer_nao_apaga_arquivo_editado_depois(semestre_sintetico):
    aplicar(criar_proposta(semestre_sintetico, [Operacao("criar", f"{DISC}/02 - Aulas/Aula 02 - B.md", b"b")], "x")["id"], P)
    (semestre_sintetico / DISC / "02 - Aulas" / "Aula 02 - B.md").write_bytes(b"editado pelo professor")
    desfazer(P)
    assert any(p.read_bytes() == b"editado pelo professor" for p in (semestre_sintetico / DISC / "99 - Arquivo").iterdir())

@pytest.mark.parametrize("destino", ["../fora.txt", "C:/fora.txt"])
def test_destino_fora_da_raiz(semestre_sintetico, destino):
    with pytest.raises(ErroAcad):
        criar_proposta(semestre_sintetico, [Operacao("criar", destino, b"x")], "x")

def test_criar_sobre_existente_recusa(semestre_sintetico):
    (semestre_sintetico / "README.md").write_text("x")
    with pytest.raises(ErroAcad):
        criar_proposta(semestre_sintetico, [Operacao("criar", "README.md", b"y")], "x")

def test_escrita_no_drive_bloqueada(monkeypatch, tmp_path):
    monkeypatch.setenv("ACAD_BLOQUEAR_ESCRITA", str(tmp_path))
    (tmp_path / "s").mkdir()
    pr = criar_proposta(tmp_path / "s", [Operacao("criar", "a.txt", b"x")], "x")
    with pytest.raises(ErroAcad) as e:
        aplicar(pr["id"], P)
    assert e.value.codigo == "escrita-bloqueada" and not (tmp_path / "s" / "a.txt").exists()

def test_pasta_arquivo_sem_99_usa_primeiro_nivel(semestre_sintetico):
    p = pasta_arquivo_para(semestre_sintetico, semestre_sintetico / "08 - Avaliações" / "N1" / "x.tex", P)
    assert p == semestre_sintetico / "08 - Avaliações" / "99 - Arquivo"

def test_proposta_aplicada_duas_vezes(semestre_sintetico):
    pr = criar_proposta(semestre_sintetico, [Operacao("criar", "a.txt", b"x")], "x")
    aplicar(pr["id"], P)
    with pytest.raises(ErroAcad):
        aplicar(pr["id"], P)
```

- [x] **Step 2: Rodar e ver falhar.**

- [x] **Step 3: Implementar** `escrita.py` e `diario.py` conforme a interface. Pontos que os testes cobram: normalizar `destino` com `PurePosixPath`, recusar absoluto e `..`; resolver `(raiz / destino).resolve()` e exigir `is_relative_to(raiz.resolve())`; checar `ACAD_BLOQUEAR_ESCRITA` comparando `str(raiz.resolve()).lower()` e a forma com `/` contra cada prefixo em minúsculas; mover com `os.replace` (mesmo volume) e `shutil.move` como alternativa; o diário guarda, por item, `{"acao": "criado"|"arquivado"|"pasta-criada", "destino", "arquivo_morto", "sha256"}`; `desfazer` percorre os itens ao contrário.

```python
# acad/arquivos/diario.py
import json
from acad.config import dir_dados

def _arq():
    d = dir_dados(); d.mkdir(parents=True, exist_ok=True); return d / "diario.jsonl"

def registrar(entrada: dict) -> None:
    with open(_arq(), "a", encoding="utf-8") as f:
        f.write(json.dumps(entrada, ensure_ascii=False) + "\n")

def _todas() -> list[dict]:
    a = _arq()
    return [json.loads(l) for l in a.read_text(encoding="utf-8").splitlines() if l] if a.exists() else []

def ultima_aplicada() -> dict | None:
    desfeitas = {e["id"] for e in _todas() if e.get("tipo") == "desfeita"}
    for e in reversed(_todas()):
        if e.get("tipo") == "aplicada" and e["id"] not in desfeitas:
            return e
    return None

def ja_aplicada(id: str) -> bool:
    return any(e.get("tipo") == "aplicada" and e["id"] == id for e in _todas())

def marcar_desfeita(id: str) -> None:
    registrar({"tipo": "desfeita", "id": id})
```

- [x] **Step 4: Rodar e ver passar** — `$PY -m pytest testes/unidade/test_escrita.py -v`.
- [x] **Step 5: Commit** — `git commit -m "feat: escrita por proposta com arquivo morto e desfazer"`

### Tarefa 12: CLI base (`ambiente verificar`, `cronograma consultar`, `aplicar`, `desfazer`)

**Files:**
- Create: `acad/cli.py`, `acad/contexto.py`
- Test: `testes/unidade/test_cli.py`

**Interfaces:**
- Consumes: `Resultado`, `ErroAcad`, `config`, `consultar`, `resumo_texto`, `encontrar_raiz`, `aplicar`, `desfazer`, `carregar_perfil`.
- Produces:
  - `cli.main(argv: list[str] | None = None) -> int` (argparse com subcomandos aninhados; `--json` global; captura `ErroAcad` → envelope com `erros=[{codigo, mensagem, detalhe_tecnico: ""}]` e `config.registrar_detalhe(detalhe)`; qualquer outra exceção → `erro-inesperado`, saída 2, traceback só no registro).
  - `cli.registrar(nome: str, ajuda: str)` — decorador para tarefas seguintes acrescentarem subcomandos: `@registrar("encontros gerar", "…")` recebe `(sub: argparse.ArgumentParser)` para declarar argumentos e devolve a função `executar(args) -> Resultado`. Comandos de duas palavras viram subparsers aninhados.
  - `contexto.carregar_configuracao() -> dict | None` (`dir_dados()/configuracao.yaml`, validado com esquema `semestre`); `contexto.raiz_semestre(args) -> Path` (`--raiz` ou `raiz_workspace` da configuração; senão `ErroAcad("raiz-nao-encontrada", msg("raiz-nao-encontrada"), saida=3)`); `contexto.workspace(raiz) -> Workspace`; `contexto.perfil() -> Perfil` (da configuração, padrão `fasoft`); `contexto.localizar_disciplina(ws, semestre, ident: str) -> Path` (aceita código do `disciplina.yaml`, número `04` ou trecho do nome sem acento; ambíguo/inexistente → `ErroAcad("disciplina-nao-encontrada", …)`).
- Subcomandos desta tarefa: `ambiente verificar` (versão do Python ≥ 3.11, imports `yaml jsonschema openpyxl`, configuração, raiz acessível; `dados.python`, `dados.faltando`), `cronograma consultar [--data AAAA-MM-DD|DD/MM/AAAA] [--raiz]` (raiz padrão: `encontrar_raiz(cwd)` ou a raiz Fasoft acima de `raiz_workspace`), `aplicar <id>`, `desfazer`.

- [x] **Step 1: Testes que falham**

```python
# testes/unidade/test_cli.py
import json
from pathlib import Path
from acad.cli import main

AMOSTRA = Path(__file__).resolve().parents[1] / "amostras" / "fasoft"

def _json(capsys, argv):
    code = main(argv + ["--json"])
    return code, json.loads(capsys.readouterr().out)

def test_ambiente_verificar(capsys):
    code, d = _json(capsys, ["ambiente", "verificar"])
    assert code == 0 and d["ok"] and d["dados"]["faltando"] == []

def test_consultar_json(capsys):
    code, d = _json(capsys, ["cronograma", "consultar", "--data", "2026-07-28", "--raiz", str(AMOSTRA)])
    assert code == 0 and d["dados"]["quantidade_aulas"] == 1

def test_consultar_aceita_data_brasileira(capsys):
    code, d = _json(capsys, ["cronograma", "consultar", "--data", "28/07/2026", "--raiz", str(AMOSTRA)])
    assert d["dados"]["data"] == "2026-07-28"

def test_consultar_texto(capsys):
    assert main(["cronograma", "consultar", "--data", "2026-07-28", "--raiz", str(AMOSTRA)]) == 0
    assert "Estrutura de Dados 2" in capsys.readouterr().out

def test_data_invalida_explica(capsys):
    code, d = _json(capsys, ["cronograma", "consultar", "--data", "amanhã?", "--raiz", str(AMOSTRA)])
    assert code == 2 and d["erros"][0]["codigo"] == "data-invalida"
    assert "dia/mês/ano" in d["erros"][0]["mensagem"]

def test_desfazer_sem_nada(capsys):
    code, d = _json(capsys, ["desfazer"])
    assert code == 0 and "Não há alteração" in d["mensagem"]

def test_erro_inesperado_vai_para_registro(capsys, monkeypatch):
    import acad.cronograma.consulta as c
    monkeypatch.setattr(c, "consultar", lambda *a, **k: 1 / 0)
    code, d = _json(capsys, ["cronograma", "consultar", "--raiz", str(AMOSTRA)])
    assert code == 2 and d["erros"][0]["codigo"] == "erro-inesperado"
    assert "ZeroDivisionError" not in d["mensagem"]
```

- [x] **Step 2: Rodar e ver falhar.**

- [x] **Step 3: Implementar** `acad/cli.py`:

```python
# acad/cli.py
from __future__ import annotations
import argparse, sys, traceback
from datetime import date, datetime
from typing import Callable
from acad import __version__, config, mensagens
from acad.erros import ErroAcad
from acad.saida import Resultado

_COMANDOS: dict[str, tuple[str, Callable]] = {}

def registrar(nome: str, ajuda: str):
    def deco(declarar: Callable[[argparse.ArgumentParser], Callable]):
        _COMANDOS[nome] = (ajuda, declarar)
        return declarar
    return deco

def ler_data(texto: str | None) -> date:
    if not texto:
        return date.today()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(texto, fmt).date()
        except ValueError:
            pass
    raise ErroAcad("data-invalida", "Não entendi a data. Use dia/mês/ano, por exemplo 28/10/2026.", texto)

def _montar() -> argparse.ArgumentParser:
    raiz = argparse.ArgumentParser(prog="acad", description="Núcleo do Librarius")
    raiz.add_argument("--versao", action="version", version=__version__)
    subs = raiz.add_subparsers(dest="_cmd", required=True)
    grupos: dict[str, argparse._SubParsersAction] = {}
    for nome, (ajuda, declarar) in sorted(_COMANDOS.items()):
        partes = nome.split()
        if len(partes) == 1:
            p = subs.add_parser(partes[0], help=ajuda)
        else:
            if partes[0] not in grupos:
                grupos[partes[0]] = subs.add_parser(partes[0]).add_subparsers(dest="_sub", required=True)
            p = grupos[partes[0]].add_parser(partes[1], help=ajuda)
        p.add_argument("--json", action="store_true")
        p.set_defaults(_executar=declarar(p))
    return raiz

def main(argv: list[str] | None = None) -> int:
    from acad import comandos  # noqa: F401  (importa e registra todos os subcomandos)
    args = _montar().parse_args(argv)
    try:
        r: Resultado = args._executar(args)
        codigo = 0 if r.ok else 1
    except ErroAcad as e:
        config.registrar_detalhe(f"{e.codigo}: {e.detalhe_tecnico}")
        r, codigo = Resultado(ok=False, mensagem=e.mensagem,
                              erros=[{"codigo": e.codigo, "mensagem": e.mensagem, "detalhe_tecnico": ""}]), e.saida
    except Exception:
        config.registrar_detalhe(traceback.format_exc())
        m = mensagens.msg("erro-inesperado")
        r, codigo = Resultado(ok=False, mensagem=m, erros=[{"codigo": "erro-inesperado", "mensagem": m,
                                                            "detalhe_tecnico": ""}]), 2
    sys.stdout.reconfigure(encoding="utf-8")
    print(r.para_json() if getattr(args, "json", False) else r.para_texto())
    return codigo
```

Criar `acad/comandos/__init__.py` que importa `acad.comandos.base` (e, nas tarefas seguintes, cada novo módulo de comando: `calendario`, `encontros`, `plano`, `validar`, `gerar`, `aula`, `exportar`, `perfil`, `mcp`). `acad/comandos/base.py` registra `ambiente verificar`, `cronograma consultar`, `aplicar`, `desfazer` com o decorador. Exemplo de um:

```python
# acad/comandos/base.py
from pathlib import Path
from acad.cli import registrar, ler_data
from acad.saida import Resultado
from acad import contexto, mensagens
import acad.cronograma.consulta as consulta

@registrar("cronograma consultar", "Mostra as aulas de um dia e o que já está pronto")
def _consultar(p):
    p.add_argument("--data"); p.add_argument("--raiz")
    def executar(args) -> Resultado:
        alvo = ler_data(args.data)
        raiz = consulta.encontrar_raiz(Path(args.raiz) if args.raiz else contexto.raiz_padrao_consulta())
        if raiz is None:
            from acad.erros import ErroAcad
            raise ErroAcad("raiz-nao-encontrada", mensagens.msg("raiz-nao-encontrada"), saida=3)
        r = consulta.consultar(raiz, alvo, contexto.perfil().exclusao)
        return Resultado(ok=True, mensagem=consulta.resumo_texto(r), dados=r)
    return executar
```

(`contexto.raiz_padrao_consulta()` devolve `Path.cwd()` ou a `raiz_workspace` configurada.) Atualizar `acad/__main__.py` para `sys.exit(main())` sem o `try/except ImportError`.

- [x] **Step 4: Rodar e ver passar** — `$PY -m pytest testes -v -m "not drive"`.
- [x] **Step 5: Commit** — `git commit -m "feat: CLI acad com consulta, aplicar e desfazer"`

### Tarefa 13: Calendário canônico (modelo, leitura e confirmação)

**Files:**
- Create: `acad/calendario/__init__.py`, `acad/calendario/modelo.py`
- Modify: `acad/esquemas.py` (acrescentar `para_yaml`)
- Test: `testes/unidade/test_calendario.py`

**Interfaces:**
- Produces:
  - `esquemas.para_yaml(doc: dict) -> str` (`yaml.safe_dump(doc, allow_unicode=True, sort_keys=False)`).
  - `@dataclass DiaEspecial(data: date, tipo: str, descricao: str = "", equivale_a: int | None = None)`, `@dataclass Evento(inicio: date, fim: date, tipo: str, descricao: str = "")`, `@dataclass Calendario(semestre: str, inicio: date, fim: date, status: str, dias: list[DiaEspecial], eventos: list[Evento], fonte: dict, confirmado_em: str | None = None)`.
  - `de_documento(doc: dict) -> Calendario` (valida esquema `calendario`), `para_documento(c: Calendario) -> dict`.
  - `dia(c, d: date) -> DiaEspecial | None`; `letivo(c, d) -> bool` (False em `feriado`/`recesso`; dia fora de `inicio..fim` também False); `dia_semana_efetivo(c, d) -> int` (`equivale_a` em `sabado-letivo`/`troca-de-dia`, senão `d.isoweekday()`).
  - `confirmar(c, agora: datetime) -> Calendario` — exige `status == "rascunho"` e todo `sabado-letivo`/`troca-de-dia` com `equivale_a`; senão `ErroAcad("calendario-incompleto", "Falta dizer qual dia da semana o sábado letivo de 17/10 substitui.")`.

- [x] **Step 1: Testes que falham**

```python
# testes/unidade/test_calendario.py
from datetime import date, datetime
import pytest
from acad.calendario.modelo import de_documento, para_documento, dia, letivo, dia_semana_efetivo, confirmar
from acad.erros import ErroAcad

DOC = {"versao_esquema": 1, "calendario": {"semestre": "2026-2", "inicio": "2026-07-27", "fim": "2026-12-12",
       "fonte": {"tipo": "manual"}, "status": "rascunho", "confirmado_em": None,
       "dias": [{"data": "2026-10-12", "tipo": "feriado", "descricao": "Nossa Senhora Aparecida"},
                {"data": "2026-10-17", "tipo": "sabado-letivo", "equivale_a": 1}],
       "eventos": [{"inicio": "2026-09-21", "fim": "2026-09-25", "tipo": "semana-academica", "descricao": "SETECH"}]}}

def test_ida_e_volta():
    assert para_documento(de_documento(DOC)) == DOC

def test_feriado_nao_letivo():
    c = de_documento(DOC)
    assert not letivo(c, date(2026, 10, 12)) and letivo(c, date(2026, 10, 13))

def test_fora_do_semestre():
    assert not letivo(de_documento(DOC), date(2026, 12, 20))

def test_sabado_letivo_equivale_a_segunda():
    assert dia_semana_efetivo(de_documento(DOC), date(2026, 10, 17)) == 1

def test_confirmar_exige_equivalencia():
    d = {**DOC, "calendario": {**DOC["calendario"], "dias": [{"data": "2026-10-17", "tipo": "sabado-letivo", "equivale_a": None}]}}
    with pytest.raises(ErroAcad) as e:
        confirmar(de_documento(d, validar=False), datetime(2026, 7, 1))
    assert "17/10" in e.value.mensagem

def test_confirmar_muda_status():
    c = confirmar(de_documento(DOC), datetime(2026, 7, 1, 10, 0))
    assert c.status == "confirmado" and c.confirmado_em.startswith("2026-07-01")
```

(`de_documento(doc, validar=True)` — `validar=False` só para montar o caso inválido do teste; o esquema da Tarefa 3 já recusa `equivale_a` nulo.)

- [x] **Step 2: Rodar e ver falhar.**
- [x] **Step 3: Implementar** `modelo.py` conforme a interface (conversões `date.fromisoformat`; `para_documento` reproduz a ordem de chaves do documento de entrada: `semestre, inicio, fim, fonte, status, confirmado_em, dias, eventos`; omite `descricao` vazia e `equivale_a` nulo).
- [x] **Step 4: Rodar e ver passar.**
- [x] **Step 5: Commit** — `git commit -m "feat: calendário acadêmico canônico"`

### Tarefa 14: Importar calendário de ICS e XLSX (`acad calendario importar|confirmar`)

**Files:**
- Create: `acad/calendario/importar_ics.py`, `acad/calendario/importar_xlsx.py`, `acad/comandos/calendario.py`, `modelos/calendario.xlsx` (gerado pelo teste-ferramenta abaixo), `testes/amostras/sinteticos/calendario-2026-2.ics`, `testes/amostras/sinteticos/calendario-2026-2.xlsx`
- Modify: `pyproject.toml` (+ `icalendar`, versão via `pip index versions icalendar`)
- Test: `testes/unidade/test_importar_calendario.py`

**Interfaces:**
- Consumes: `Calendario`, `DiaEspecial`, `Evento`, `criar_proposta`, `Operacao`, `contexto`.
- Produces:
  - `importar_ics(conteudo: bytes, semestre: str, inicio: date, fim: date) -> Calendario` — só `VEVENT`; `DTSTART`/`DTEND` (all-day: `DTEND` exclusivo); classificação por `sem_acento(SUMMARY)`: contém `feriado` → `feriado`; `recesso` → `recesso`; `sabado letivo` → `sabado-letivo` com `equivale_a=None`; evento de mais de um dia que não seja feriado/recesso → `Evento(tipo="semana-academica" se contém "semana" senão "outro")`; um dia sem palavra-chave → `DiaEspecial(tipo="outro")`. Feriado/recesso de vários dias vira um `DiaEspecial` por dia. Sempre `status="rascunho"`, `fonte={"tipo": "ics", "arquivo": <nome>, "sha256": …}`.
  - `importar_xlsx(conteudo: bytes, semestre, inicio, fim) -> Calendario` — formato canônico do Librarius (`modelos/calendario.xlsx`): aba 1, cabeçalho na linha 1 `Data | Tipo | Descrição | Equivale a`; `Tipo` em português simples (`Feriado`, `Recesso`, `Sábado letivo`, `Troca de dia`, `Semana acadêmica`, `Avaliação`, `Outro`) mapeado para o enum; `Equivale a` aceita `segunda`…`domingo`; `Data` aceita data ou intervalo `dd/mm/aaaa a dd/mm/aaaa`.
  - `acad calendario importar <arquivo> --inicio D --fim D [--semestre 2026-2] [--raiz]` → proposta criando/substituindo `00 - Administração Acadêmica/calendario.yaml` (a pasta é a que casa `^00 - ` no semestre); mensagem lista quantos feriados/recessos/sábados letivos e pede conferência.
  - `acad calendario confirmar [--raiz]` → proposta substituindo o arquivo com `status: confirmado`.

- [x] **Step 1: Criar amostras sintéticas** (datas fictícias, nada institucional): `calendario-2026-2.ics` com 4 eventos — `Feriado - Nossa Senhora Aparecida` (12/10, all-day), `Recesso` (19/11–21/11, DTEND 22/11), `Sábado letivo` (17/10), `SETECH - Semana Acadêmica` (21/09–26/09); e o `.xlsx` equivalente no formato canônico (gerar com openpyxl num script `testes/ferramentas/gerar-sinteticos.py`, commitado).

- [x] **Step 2: Testes que falham**

```python
# testes/unidade/test_importar_calendario.py
import json
from datetime import date
from pathlib import Path
from acad.calendario.importar_ics import importar_ics
from acad.calendario.importar_xlsx import importar_xlsx
from acad.cli import main

SINT = Path(__file__).resolve().parents[1] / "amostras" / "sinteticos"
ARGS = ("2026-2", date(2026, 7, 27), date(2026, 12, 12))

def _tipos(c):
    return {(d.data, d.tipo) for d in c.dias}

def test_ics():
    c = importar_ics((SINT / "calendario-2026-2.ics").read_bytes(), *ARGS)
    assert (date(2026, 10, 12), "feriado") in _tipos(c)
    assert {(date(2026, 11, d), "recesso") for d in (19, 20, 21)} <= _tipos(c)
    assert (date(2026, 11, 22), "recesso") not in _tipos(c)          # DTEND exclusivo
    assert any(e.tipo == "semana-academica" for e in c.eventos)
    assert c.status == "rascunho" and c.fonte["tipo"] == "ics"

def test_sabado_letivo_fica_pendente():
    c = importar_ics((SINT / "calendario-2026-2.ics").read_bytes(), *ARGS)
    [s] = [d for d in c.dias if d.tipo == "sabado-letivo"]
    assert s.equivale_a is None

def test_xlsx_equivale_ao_ics():
    a = importar_ics((SINT / "calendario-2026-2.ics").read_bytes(), *ARGS)
    b = importar_xlsx((SINT / "calendario-2026-2.xlsx").read_bytes(), *ARGS)
    assert _tipos(a) == _tipos(b)

def test_cli_importar_gera_proposta(capsys, semestre_sintetico):
    code = main(["calendario", "importar", str(SINT / "calendario-2026-2.ics"), "--inicio", "2026-07-27",
                 "--fim", "2026-12-12", "--semestre", "2026-2", "--raiz", str(semestre_sintetico), "--json"])
    d = json.loads(capsys.readouterr().out)
    assert code == 0 and d["proposta"]["itens"][0]["destino"] == "00 - Administração Acadêmica/calendario.yaml"
    assert not (semestre_sintetico / "00 - Administração Acadêmica" / "calendario.yaml").exists()
    assert "feriado" in d["mensagem"].lower()
```

- [x] **Step 3: Rodar e ver falhar.**
- [x] **Step 4: Implementar** com `icalendar.Calendar.from_ical(conteudo)` e `walk("VEVENT")` (conferir a API na documentação do pacote instalado: `$PY -c "import icalendar, inspect; print(icalendar.__version__)"` e https://icalendar.readthedocs.io — usar só o que lá estiver). Comando:

```python
# acad/comandos/calendario.py (trecho)
@registrar("calendario importar", "Lê o calendário da instituição (arquivo de agenda ou planilha)")
def _importar(p):
    p.add_argument("arquivo"); p.add_argument("--inicio", required=True); p.add_argument("--fim", required=True)
    p.add_argument("--semestre", required=True); p.add_argument("--raiz")
    def executar(args):
        semestre = contexto.raiz_semestre(args)
        caminho = Path(args.arquivo)
        imp = importar_ics if caminho.suffix.lower() == ".ics" else importar_xlsx
        cal = imp(caminho.read_bytes(), args.semestre, ler_data(args.inicio), ler_data(args.fim))
        cal.fonte["arquivo"] = caminho.name
        destino = f"{contexto.pasta_administracao(semestre).name}/calendario.yaml"
        tipo = "substituir" if (semestre / destino).exists() else "criar"
        doc = esquemas.para_yaml(para_documento(cal)).encode("utf-8")
        pr = criar_proposta(semestre, [Operacao(tipo, destino, doc, "calendário do semestre")],
                            "Vou guardar o calendário do semestre na pasta de administração.")
        n = Counter(d.tipo for d in cal.dias)
        msg = (f"Li o calendário: {n['feriado']} feriado(s), {n['recesso']} dia(s) de recesso, "
               f"{n['sabado-letivo']} sábado(s) letivo(s). Confira antes de eu usar.")
        return Resultado(ok=True, mensagem=msg, dados=para_documento(cal), proposta=pr)
    return executar
```

(`contexto.pasta_administracao(semestre) -> Path`: primeira pasta do semestre que casa `^00 - `; criar em `contexto.py`.)
- [x] **Step 5: Rodar e ver passar.**
- [x] **Step 6: Commit** — `git commit -m "feat: importação de calendário ICS e planilha"`

### Tarefa 15: Gerar encontros por turma (`acad encontros gerar`)

**Files:**
- Create: `acad/encontros/__init__.py`, `acad/encontros/gerar.py`, `acad/comandos/encontros.py`, `acad/planejamento/__init__.py`, `acad/planejamento/arquivos.py`
- Test: `testes/unidade/test_encontros.py`

**Interfaces:**
- Consumes: `Calendario`, `letivo`, `dia`, `dia_semana_efetivo`, esquemas `turma`/`encontro`.
- Produces:
  - `@dataclass Encontro(id: str, data: date, inicio: str, fim: str, status: str, aulas: list[str], funcao: str, origem: str, motivo: str | None = None)`; `Encontro.minutos -> int`.
  - `gerar_encontros(cal: Calendario, turma: dict, anteriores: list[Encontro] | None = None) -> list[Encontro]` — algoritmo: para cada data de `cal.inicio` a `cal.fim`, dia da semana efetivo; para cada horário da turma nesse dia: feriado/recesso → `cancelado` (motivo = descrição ou tipo, origem `horario`); exceção `cancelamento` da turma → `cancelado` (motivo da exceção); senão `previsto` (origem `sabado-letivo` se o dia for sábado letivo/troca, senão `horario`). Fora do calendário (inicio/fim) nada. Reposições da turma viram `previsto` com origem `reposicao`. Ordena por (`data`, `inicio`) e numera `E01`… (`E001` se > 99). Com `anteriores`: para a mesma chave (`data`, `inicio`), preserva `status`, `aulas`, `funcao` do anterior, exceto quando o novo é `cancelado` por calendário (o calendário vence).
  - `planejamento.arquivos`: `ler_turma(ws, disc, id) -> dict`, `ler_encontros(ws, disc, id) -> list[Encontro]` (vazio se não existe), `documento_encontros(encontros, entradas: dict[str,str], versao: str, agora: datetime) -> dict`, `ler_aulas(ws, disc) -> dict` (documento `aulas.yaml` ou `{"versao_esquema":1,"disciplina":..., "aulas": []}`), `ler_disciplina(ws, disc) -> dict`, `ler_avaliacoes(ws, disc) -> list[dict]` (vazio se não há pasta), `caminho(disc, nome) -> str` (relativo ao semestre: `<disc>/01 - Planejamento/<nome>`).
  - `acad encontros gerar <DISC> --turma TA [--raiz]` — exige calendário `confirmado` (senão `ErroAcad("calendario-nao-confirmado", "O calendário ainda não foi conferido por você.", saida=1)`); gera proposta criando/substituindo `encontros-TA.yaml`; mensagem: "N encontros previstos, M cancelados por feriado ou recesso" + diff de ids quando já existia.

- [x] **Step 1: Testes que falham**

```python
# testes/unidade/test_encontros.py
from datetime import date
from acad.calendario.modelo import de_documento
from acad.encontros.gerar import gerar_encontros, Encontro

CAL = de_documento({"versao_esquema": 1, "calendario": {"semestre": "2026-2", "inicio": "2026-10-05", "fim": "2026-10-23",
    "fonte": {"tipo": "manual"}, "status": "confirmado", "confirmado_em": "2026-07-01T10:00:00-03:00",
    "dias": [{"data": "2026-10-12", "tipo": "feriado", "descricao": "Nossa Senhora Aparecida"},
             {"data": "2026-10-17", "tipo": "sabado-letivo", "equivale_a": 1}], "eventos": []}})
TURMA = {"id": "TA", "disciplina": "ED2", "fuso": "America/Sao_Paulo",
         "horarios": [{"dia_semana": 1, "inicio": "19:00", "fim": "20:40"}, {"dia_semana": 3, "inicio": "19:00", "fim": "20:40"}],
         "excecoes": [{"tipo": "cancelamento", "data": "2026-10-21", "motivo": "evento do curso"},
                      {"tipo": "reposicao", "data": "2026-10-24", "inicio": "08:00", "fim": "09:40", "repoe": "2026-10-21"}]}

def _por_data(es):
    return {(e.data, e.inicio): e for e in es}

def test_segundas_e_quartas():
    es = gerar_encontros(CAL, TURMA)
    previstos = [e.data for e in es if e.status == "previsto"]
    assert date(2026, 10, 5) in previstos and date(2026, 10, 7) in previstos
    assert date(2026, 10, 6) not in [e.data for e in es]

def test_feriado_cancela():
    e = _por_data(gerar_encontros(CAL, TURMA))[(date(2026, 10, 12), "19:00")]
    assert e.status == "cancelado" and "Aparecida" in e.motivo

def test_sabado_letivo_segue_segunda():
    e = _por_data(gerar_encontros(CAL, TURMA))[(date(2026, 10, 17), "19:00")]
    assert e.status == "previsto" and e.origem == "sabado-letivo"

def test_excecao_e_reposicao_da_turma():
    es = _por_data(gerar_encontros(CAL, TURMA))
    assert es[(date(2026, 10, 21), "19:00")].status == "cancelado"
    r = es[(date(2026, 10, 24), "08:00")]
    assert r.status == "previsto" and r.origem == "reposicao"

def test_reposicao_fora_do_periodo_ainda_entra():
    # 24/10 é após o fim (23/10): reposição explícita vale mesmo assim
    assert (date(2026, 10, 24), "08:00") in _por_data(gerar_encontros(CAL, TURMA))

def test_ids_cronologicos():
    es = gerar_encontros(CAL, TURMA)
    assert [e.id for e in es] == [f"E{i:02d}" for i in range(1, len(es) + 1)]
    assert es == sorted(es, key=lambda e: (e.data, e.inicio))

def test_regerar_preserva_status_e_aulas():
    es = gerar_encontros(CAL, TURMA)
    es[0].status, es[0].aulas = "realizado", ["Aula 01"]
    novos = gerar_encontros(CAL, TURMA, anteriores=es)
    assert novos[0].status == "realizado" and novos[0].aulas == ["Aula 01"]

def test_calendario_vence_anterior():
    es = gerar_encontros(CAL, TURMA)
    alvo = next(e for e in es if e.data == date(2026, 10, 12)); alvo.status = "previsto"
    novos = _por_data(gerar_encontros(CAL, TURMA, anteriores=es))
    assert novos[(date(2026, 10, 12), "19:00")].status == "cancelado"

def test_minutos():
    assert Encontro("E01", date(2026, 10, 5), "19:00", "20:40", "previsto", [], "conteudo", "horario").minutos == 100
```

E um teste de CLI que monta `turma-TA.yaml`, `calendario.yaml` confirmado e `disciplina.yaml` no `semestre_sintetico` e confere a proposta (`destino` termina em `01 - Planejamento/encontros-TA.yaml`) e a recusa com calendário em rascunho (`codigo == "calendario-nao-confirmado"`).

- [x] **Step 2: Rodar e ver falhar.**
- [x] **Step 3: Implementar** conforme o algoritmo da interface. Reposição explícita entra mesmo fora de `inicio..fim` (o professor a declarou); `funcao` padrão `conteudo`.
- [x] **Step 4: Rodar e ver passar.**
- [x] **Step 5: Commit** — `git commit -m "feat: geração de encontros por turma"`

### Tarefa 16: Carga horária

**Files:**
- Create: `acad/encontros/carga.py`
- Test: `testes/unidade/test_carga.py`

**Interfaces:**
- Produces: `minutos_validos(encontros) -> int` (soma de `minutos` com status ≠ `cancelado`); `em_unidade(minutos: int, unidade: str, minutos_hora_aula: int | None) -> float` (`hora_relogio`: /60; `hora_aula`: /`minutos_hora_aula`); `verificar_carga(encontros, carga_horaria: dict) -> list[Achado]` — `unidade` nula → `carga-unidade-nao-confirmada` (aviso, mensagem cita D3 em linguagem simples: "Ainda falta você me dizer se a carga da disciplina é contada em hora-aula ou em hora cheia."); senão compara com `valor` (tolerância 0,01) → `carga-horaria-incompativel` (erro) com "faltam X h" ou "sobram X h" na unidade declarada.

- [x] **Step 1: Testes que falham**

```python
# testes/unidade/test_carga.py
from datetime import date, timedelta
from acad.encontros.gerar import Encontro
from acad.encontros.carga import minutos_validos, em_unidade, verificar_carga

def _enc(n, status="previsto"):
    return [Encontro(f"E{i:02d}", date(2026, 8, 3) + timedelta(days=i), "19:00", "20:40", status, [], "conteudo", "horario")
            for i in range(1, n + 1)]

def test_cancelados_nao_contam():
    assert minutos_validos(_enc(3) + _enc(2, "cancelado")) == 300

def test_unidades():
    assert em_unidade(3600, "hora_relogio", None) == 60
    assert em_unidade(3600, "hora_aula", 50) == 72

def test_36_encontros_de_100_min_fecham_60h():
    assert verificar_carga(_enc(36), {"valor": 60, "unidade": "hora_relogio", "minutos_hora_aula": None}) == []

def test_falta_carga():
    [a] = verificar_carga(_enc(30), {"valor": 60, "unidade": "hora_relogio", "minutos_hora_aula": None})
    assert a.codigo == "carga-horaria-incompativel" and "faltam 10" in a.mensagem

def test_hora_aula_50():
    assert verificar_carga(_enc(36), {"valor": 72, "unidade": "hora_aula", "minutos_hora_aula": 50}) == []

def test_unidade_pendente_d3():
    [a] = verificar_carga(_enc(36), {"valor": 60, "unidade": None, "minutos_hora_aula": None})
    assert a.codigo == "carga-unidade-nao-confirmada" and a.nivel == "aviso"
```

- [x] **Step 2–4:** falhar, implementar, passar (formatar horas com vírgula decimal: `f"{x:.1f}".replace(".", ",").removesuffix(",0")`).
- [x] **Step 5: Commit** — `git commit -m "feat: verificação de carga horária nas duas unidades"`

### Tarefa 17: Importar cronograma `.xlsx` para YAML (`acad cronograma importar`)

**Files:**
- Create: `acad/cronograma/importar.py`, `acad/comandos/cronograma.py`
- Test: `testes/unidade/test_importar_cronograma.py`, `testes/esperados/ed2-aulas.yaml`, `testes/esperados/ed2-encontros-TA.yaml`

**Interfaces:**
- Consumes: `ler_cronograma`, `consulta._tipo` (mover para `acad/cronograma/classificar.py` como `tipo_linha(aula, topico) -> str` e reusar nos dois), `Encontro`, `ler_turma`.
- Produces: `importar_cronograma(linhas: list[LinhaCronograma], turma: dict, disciplina: str) -> tuple[list[Encontro], dict]` — um encontro por linha com data; `inicio`/`fim` do horário da turma cujo `dia_semana` = dia da data (senão o primeiro horário, e aviso); `origem="planilha"`; `tipo_linha` `sem-aula` → `status="cancelado"`, `motivo=topico`, `aulas=[]`; `avaliacao` → `funcao="avaliacao"`, `aulas=[]`; `aula` → `funcao="conteudo"`, `aulas=["Aula NN"]`, e entra em `aulas.yaml` (`id`, `tema`=tópico, `status="planejada"`, `objetivos=[]`, `prerequisitos=[]`, `encontros_necessarios=1`; se o mesmo `Aula NN` aparecer em mais de uma linha, a aula ganha os vários encontros e `encontros_necessarios` = quantidade). Retorna `(encontros, documento_aulas)`.
- CLI: `acad cronograma importar <DISC> --turma TA [--raiz]` → proposta com `encontros-TA.yaml` e `aulas.yaml` (substituir se existem). Mensagem: "Li N linhas: X aulas, Y avaliações, Z dias sem aula."

- [x] **Step 1: Testes que falham**

```python
# testes/unidade/test_importar_cronograma.py
from pathlib import Path
import yaml
from acad.cronograma.planilha import ler_cronograma
from acad.cronograma.importar import importar_cronograma

T = Path(__file__).resolve().parents[1]
XLSX = T / "amostras/fasoft/2026/Segundo Semestre/04 - Estrutura de Dados 2 - 5º Período/01 - Planejamento/Cronograma - Estrutura de Dados 2.xlsx"
TURMA = {"id": "TA", "disciplina": "ED2", "fuso": "America/Sao_Paulo",
         "horarios": [{"dia_semana": 2, "inicio": "19:00", "fim": "20:40"}, {"dia_semana": 5, "inicio": "19:00", "fim": "20:40"}]}

def test_importa_amostra_real():
    es, aulas = importar_cronograma(ler_cronograma(XLSX.read_bytes(), 2026), TURMA, "ED2")
    assert es[0].aulas == ["Aula 01"] and es[0].inicio == "19:00"
    aval = [e for e in es if e.funcao == "avaliacao"]
    assert aval and all(e.aulas == [] for e in aval)
    ids = [a["id"] for a in aulas["aulas"]]
    assert "Aula 01" in ids and "Aula 11" not in ids          # Aula 11 = PRIMEIRA AVALIAÇÃO

def test_saida_bate_com_esperado():
    es, aulas = importar_cronograma(ler_cronograma(XLSX.read_bytes(), 2026), TURMA, "ED2")
    esperado = yaml.safe_load((T / "esperados" / "ed2-aulas.yaml").read_text(encoding="utf-8"))
    assert aulas == esperado
```

Para criar `testes/esperados/ed2-aulas.yaml`: rodar a função uma vez, **conferir à mão** contra a planilha (abrir no Excel/LibreOffice ou imprimir as linhas com `ler_cronograma`) que cada aula, tema e avaliação está certa, e só então salvar. Registrar no commit que o esperado foi conferido linha a linha.

- [x] **Step 2–4:** falhar, implementar, passar. Conferir também com `acad cronograma importar 04 --turma TA --raiz testes/amostras/fasoft/2026/Segundo\ Semestre --json` (gera proposta; não aplicar).
- [x] **Step 5: Commit** — `git commit -m "feat: importação do cronograma em planilha para o modelo de dados"`

### Tarefa 18: Distribuir aulas sobre encontros (`acad plano distribuir`)

**Files:**
- Create: `acad/planejamento/distribuir.py`, `acad/comandos/plano.py`
- Test: `testes/unidade/test_distribuir.py`

**Interfaces:**
- Consumes: `Encontro`, documento de aulas.
- Produces: `ordenar_por_prerequisitos(aulas: list[dict]) -> list[dict]` (Kahn estável: respeita a ordem original quando não há dependência; ciclo → `ErroAcad("prerequisitos-em-ciclo", "Duas aulas dependem uma da outra: …")`); `distribuir(aulas: list[dict], encontros: list[Encontro]) -> tuple[list[Encontro], list[str]]` — encontros `realizado` mantêm suas aulas; aulas `ministrada` não se movem; as demais aulas (ordenadas) ocupam, em sequência, os encontros `previsto` com `funcao == "conteudo"` (limpando o mapeamento antigo desses encontros), `encontros_necessarios` encontros consecutivos cada; devolve `(encontros, aulas_sem_encontro)`.
- CLI: `acad plano distribuir <DISC> --turma TA` → proposta substituindo `encontros-TA.yaml`; mensagem com a lista "Aula 01 → 03/08; Aula 05 → 17/08 e 19/08…" e aviso se sobrar aula.

- [x] **Step 1: Testes que falham**

```python
# testes/unidade/test_distribuir.py
from datetime import date, timedelta
import pytest
from acad.encontros.gerar import Encontro
from acad.planejamento.distribuir import distribuir, ordenar_por_prerequisitos
from acad.erros import ErroAcad

def _es(n, **kw):
    return [Encontro(f"E{i:02d}", date(2026, 8, 3) + timedelta(days=2 * i), "19:00", "20:40",
                     kw.get("status", "previsto"), [], kw.get("funcao", "conteudo"), "horario") for i in range(1, n + 1)]

def _a(id, nec=1, pre=(), status="planejada"):
    return {"id": id, "tema": id, "status": status, "encontros_necessarios": nec, "prerequisitos": list(pre)}

def test_sequencial_com_dois_encontros():
    es, sobra = distribuir([_a("Aula 01"), _a("Aula 02", 2), _a("Aula 03")], _es(4))
    assert [e.aulas for e in es] == [["Aula 01"], ["Aula 02"], ["Aula 02"], ["Aula 03"]] and sobra == []

def test_pula_avaliacao_e_cancelado():
    es = _es(4); es[1].funcao = "avaliacao"; es[2].status = "cancelado"
    es, _ = distribuir([_a("Aula 01"), _a("Aula 02")], es)
    assert es[1].aulas == [] and es[2].aulas == [] and es[3].aulas == ["Aula 02"]

def test_realizado_preservado():
    es = _es(3); es[0].status, es[0].aulas = "realizado", ["Aula 01"]
    es, _ = distribuir([_a("Aula 01", status="ministrada"), _a("Aula 02")], es)
    assert es[0].aulas == ["Aula 01"] and es[1].aulas == ["Aula 02"]

def test_sobra_aula():
    _, sobra = distribuir([_a("Aula 01"), _a("Aula 02")], _es(1))
    assert sobra == ["Aula 02"]

def test_prerequisito_reordena():
    ordem = ordenar_por_prerequisitos([_a("Aula 02", pre=["Aula 01"]), _a("Aula 01"), _a("Aula 03")])
    assert [a["id"] for a in ordem] == ["Aula 01", "Aula 02", "Aula 03"]

def test_ciclo():
    with pytest.raises(ErroAcad):
        ordenar_por_prerequisitos([_a("Aula 01", pre=["Aula 02"]), _a("Aula 02", pre=["Aula 01"])])
```

- [x] **Step 2–4:** falhar, implementar, passar.
- [x] **Step 5: Commit** — `git commit -m "feat: distribuição das aulas sobre os encontros"`

### Tarefa 19: Replanejamento com relatório de diff (`acad plano replanejar`)

**Files:**
- Create: `acad/planejamento/replanejar.py`
- Modify: `acad/comandos/plano.py`
- Test: `testes/unidade/test_replanejar.py`

**Interfaces:**
- Consumes: `distribuir`, `Encontro`, avaliações (`data`, `aulas_cobertas`, `etapa`).
- Produces: `cancelar(encontros, d: date, motivo: str) -> list[Encontro]` (cópias; encontros da data viram `cancelado`; data sem encontro → `ErroAcad("sem-encontro-na-data", "Não há aula dessa turma em 21/10.")`); `diff(antes: list[Encontro], depois: list[Encontro], avaliacoes: list[dict]) -> dict` → `{"deslocadas": [{"aula", "de": [iso], "para": [iso]}], "comprimidas": [aula cujo nº de encontros diminuiu], "sem_encontro": [aula], "avaliacoes_afetadas": [{"etapa", "data", "aulas": [aula coberta cujo último encontro agora é depois da prova ou ficou sem encontro]}]}`; `resumo_diff(d: dict) -> str` em português ("3 aulas mudam de dia: Aula 06 sai de 21/10 para 26/10; … A avaliação N2 de 18/11 passaria a cobrir a Aula 12, que ainda não teria sido dada.").
- CLI: `acad plano replanejar <DISC> --turma TA --cancelar <data> [--motivo "..."]` → proposta substituindo `encontros-TA.yaml`; `dados` traz o diff; o professor aprova o diff, não o cronograma inteiro.

- [x] **Step 1: Testes que falham**

```python
# testes/unidade/test_replanejar.py
from datetime import date, timedelta
from acad.encontros.gerar import Encontro
from acad.planejamento.distribuir import distribuir
from acad.planejamento.replanejar import cancelar, diff, resumo_diff

def _es(n):
    return [Encontro(f"E{i:02d}", date(2026, 10, 5) + timedelta(days=2 * (i - 1)), "19:00", "20:40", "previsto", [], "conteudo", "horario")
            for i in range(1, n + 1)]

AULAS = [{"id": f"Aula {i:02d}", "tema": "x", "status": "planejada", "encontros_necessarios": 1, "prerequisitos": []} for i in range(1, 5)]

def test_cancelar_desloca_e_afeta_avaliacao():
    antes, _ = distribuir(AULAS, _es(5))
    depois, sobra = distribuir(AULAS, cancelar(antes, date(2026, 10, 7), "chuva"))
    aval = [{"etapa": "N2", "data": "2026-10-12", "aulas_cobertas": ["Aula 03"]}]
    d = diff(antes, depois, aval)
    assert {"aula": "Aula 02", "de": ["2026-10-07"], "para": ["2026-10-09"]} in d["deslocadas"]
    assert d["avaliacoes_afetadas"] == [{"etapa": "N2", "data": "2026-10-12", "aulas": ["Aula 03"]}]

def test_resumo_em_portugues():
    antes, _ = distribuir(AULAS, _es(5))
    depois, _ = distribuir(AULAS, cancelar(antes, date(2026, 10, 7), "chuva"))
    t = resumo_diff(diff(antes, depois, []))
    assert "Aula 02" in t and "07/10" in t and "09/10" in t
```

- [x] **Step 2–4:** falhar, implementar, passar.
- [x] **Step 5: Commit** — `git commit -m "feat: replanejamento com relatório do que muda"`

### Tarefa 20: Hashes e manifestos

**Files:**
- Create: `acad/manifestos/__init__.py`, `acad/manifestos/hashes.py`, `acad/manifestos/manifesto.py`
- Test: `testes/unidade/test_manifestos.py`

**Interfaces:**
- Consumes: `Workspace`, `relativo_posix`, `nfc`.
- Produces (spec §6): `hash_bytes(b: bytes) -> str` (`"sha256:" + hex`); `hash_item(obj: dict, ignorar=("manifesto",)) -> str` (JSON canônico `sort_keys=True, ensure_ascii=False, separators=(",", ":")`, UTF-8); `hash_pasta(ws, pasta: Path) -> str` (lista ordenada `[rel_posix_nfc, hash_bytes]`, ignora `~$*`, `node_modules`, `.git`); `hash_entrada(ws, semestre: Path, chave: str, itens: dict[str, dict] | None = None) -> str | None` (chave `"<rel>#<id>"` → item de `aulas.yaml`; pasta → `hash_pasta`; arquivo → `hash_bytes`; inexistente → `None`); `montar_manifesto(artefatos: list[str], entradas: dict[str, str], versao: str, agora: datetime) -> dict` (`aprovado: False`, `aprovado_em: None`); `divergencias(manifesto: dict, calcular: Callable[[str], str | None]) -> list[str]` (chaves cujo hash atual ≠ registrado, inclusive `None`).

- [x] **Step 1: Testes que falham**

```python
# testes/unidade/test_manifestos.py
from datetime import datetime
from acad.arquivos.privacidade import Workspace
from acad.manifestos.hashes import hash_bytes, hash_item, hash_pasta
from acad.manifestos.manifesto import montar_manifesto, divergencias

def test_hash_bytes_formato():
    h = hash_bytes(b"abc")
    assert h == "sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"

def test_hash_item_ignora_ordem_e_manifesto():
    a = {"id": "Aula 03", "tema": "Rotações AVL", "manifesto": {"x": 1}}
    b = {"tema": "Rotações AVL", "id": "Aula 03"}
    assert hash_item(a) == hash_item(b)

def test_hash_item_muda_com_tema():
    assert hash_item({"id": "Aula 03", "tema": "A"}) != hash_item({"id": "Aula 03", "tema": "B"})

def test_hash_pasta_ignora_lock(tmp_path):
    (tmp_path / "m").mkdir(); (tmp_path / "m" / "a.js").write_text("1")
    ws = Workspace(tmp_path, [])
    h1 = hash_pasta(ws, tmp_path / "m")
    (tmp_path / "m" / "~$a.pptx").write_text("lixo")
    assert hash_pasta(ws, tmp_path / "m") == h1

def test_divergencias():
    m = montar_manifesto(["x.pptx"], {"a": "sha256:1", "b": "sha256:2"}, "0.1.0", datetime(2026, 10, 20, 14, 2))
    assert divergencias(m, {"a": "sha256:1", "b": "sha256:3"}.get) == ["b"]
    assert divergencias(m, {"a": "sha256:1"}.get) == ["b"]
```

- [x] **Step 2–4:** falhar, implementar, passar. `gerado_em` com fuso: `agora.astimezone().isoformat(timespec="seconds")`.
- [x] **Step 5: Commit** — `git commit -m "feat: hashes e manifestos de artefatos"`

### Tarefa 21: Regras de planejamento

**Files:**
- Create: `acad/validacao/regras.py`
- Test: `testes/unidade/test_regras.py`

**Interfaces:**
- Consumes: `Encontro`, `Calendario`, `letivo`, `Achado`, `divergencias`, `hash_entrada`, `sem_acento`.
- Produces (cada uma devolve `list[Achado]`, códigos da spec §9):
  - `regra_dia_nao_letivo(encontros, cal)` — encontro `previsto`/`realizado` em data não letiva e que não seja `origem == "reposicao"` → `encontro-em-dia-nao-letivo` (erro).
  - `regra_prerequisitos(aulas, encontros)` — primeiro encontro da aula ≤ primeiro encontro do pré-requisito (ou pré-requisito sem encontro) → `aula-antes-de-prerequisito` (erro).
  - `regra_cobertura(disciplina: dict, aulas, avaliacoes)` — objetivo sem aula → `objetivo-sem-aula`; objetivo sem avaliação → `objetivo-sem-avaliacao` (avisos). Sem avaliações cadastradas → só a primeira regra.
  - `regra_avaliacao_nao_ministrada(avaliacao, aulas, encontros)` — aula coberta que não está `ministrada` e não tem encontro `previsto`/`realizado` com data < data da prova → erro.
  - `regra_numero_repetido(ws, pasta_aulas)` — `.pptx` com o mesmo `Aula NN` e temas diferentes (tema = nome sem `Aula NN - `, sem extensão, `sem_acento`, sem os prefixos `slides - `, `roteiro de aula - `, `resumo de aula - `, `guia de estudo - `, `atividades complementares - `) → `numero-aula-repetido` (aviso, um por número).
  - `regra_manifestos(ws, semestre, disc, aulas)` — para aulas com `manifesto`: artefato inexistente → `artefato-ausente` (erro); `divergencias` não vazias → `manifesto-desatualizado` (aviso, cita quais entradas mudaram em linguagem simples: "o plano da aula", "o modelo de slides", "o programa da disciplina"; mapear por padrão do caminho).
  - `regra_slide_divergente(ws, disc, aulas)` — reaproveita `consulta._materiais` para cada aula de `aulas.yaml`: sem `slides` e com `slides_divergentes` → `slide-numeracao-divergente` (aviso).

- [x] **Step 1: Testes que falham**

```python
# testes/unidade/test_regras.py
from datetime import date
from pathlib import Path
from acad.arquivos.privacidade import Workspace
from acad.calendario.modelo import de_documento
from acad.encontros.gerar import Encontro
from acad.validacao import regras

def E(id, d, aulas=(), status="previsto", origem="horario"):
    return Encontro(id, d, "19:00", "20:40", status, list(aulas), "conteudo", origem)

CAL = de_documento({"versao_esquema": 1, "calendario": {"semestre": "2026-2", "inicio": "2026-08-01", "fim": "2026-12-12",
    "fonte": {"tipo": "manual"}, "status": "confirmado", "confirmado_em": "2026-07-01T10:00:00-03:00",
    "dias": [{"data": "2026-10-12", "tipo": "feriado"}], "eventos": []}})

def test_encontro_em_feriado():
    [a] = regras.regra_dia_nao_letivo([E("E01", date(2026, 10, 12))], CAL)
    assert a.codigo == "encontro-em-dia-nao-letivo"
    assert regras.regra_dia_nao_letivo([E("E01", date(2026, 10, 12), status="cancelado")], CAL) == []

def test_prerequisito():
    aulas = [{"id": "Aula 01", "prerequisitos": []}, {"id": "Aula 02", "prerequisitos": ["Aula 01"]}]
    es = [E("E01", date(2026, 8, 3), ["Aula 02"]), E("E02", date(2026, 8, 5), ["Aula 01"])]
    [a] = regras.regra_prerequisitos(aulas, es)
    assert a.codigo == "aula-antes-de-prerequisito" and "Aula 02" in a.mensagem

def test_cobertura():
    disc = {"objetivos": [{"id": "OBJ-01"}, {"id": "OBJ-02"}]}
    aulas = [{"id": "Aula 01", "objetivos": ["OBJ-01"]}]
    avs = [{"etapa": "N1", "objetivos": ["OBJ-01"]}]
    cods = {a.codigo for a in regras.regra_cobertura(disc, aulas, avs)}
    assert cods == {"objetivo-sem-aula", "objetivo-sem-avaliacao"}

def test_avaliacao_sobre_aula_futura():
    av = {"etapa": "N1", "data": "2026-09-01", "aulas_cobertas": ["Aula 01", "Aula 09"]}
    aulas = [{"id": "Aula 01", "status": "planejada"}, {"id": "Aula 09", "status": "planejada"}]
    es = [E("E01", date(2026, 8, 3), ["Aula 01"]), E("E09", date(2026, 9, 8), ["Aula 09"])]
    [a] = regras.regra_avaliacao_nao_ministrada(av, aulas, es)
    assert "Aula 09" in a.mensagem

def test_numero_repetido_na_amostra():
    aulas = (Path(__file__).resolve().parents[1] / "amostras/fasoft/2026/Segundo Semestre"
             / "04 - Estrutura de Dados 2 - 5º Período/02 - Aulas")
    nums = {a.mensagem.split("“")[1].split("”")[0] for a in regras.regra_numero_repetido(Workspace(aulas.parent, []), aulas)}
    assert {"Aula 05", "Aula 06", "Aula 07", "Aula 15", "Aula 18"} <= nums
```

(Mensagem de `numero-aula-repetido`: `“Aula NN” aparece em slides de temas diferentes: …`.) Incluir testes de `regra_manifestos` com um `aulas.yaml` sintético: artefato ausente e entrada alterada.

- [x] **Step 2–4:** falhar, implementar, passar.
- [x] **Step 5: Commit** — `git commit -m "feat: regras de calendário, pré-requisitos, cobertura e manifestos"`

### Tarefa 22: `acad validar` e critério de pronto sobre o Drive real

**Files:**
- Create: `acad/validacao/validar.py`, `acad/comandos/validar.py`
- Test: `testes/unidade/test_validar.py`, `testes/integracao/test_drive_somente_leitura.py`

**Interfaces:**
- Consumes: todas as regras das Tarefas 7, 8, 16, 21; `planejamento.arquivos.*`; `carregar_calendario` (opcional: sem `calendario.yaml`, regras de calendário são puladas com `info` "calendário ainda não cadastrado").
- Produces: `validar_semestre(ws, semestre: Path, perfil, disciplina: Path | None = None) -> list[Achado]` (YAML inválido → `esquema-invalido`, sem derrubar o resto); `resumo_validacao(achados, protegidas: int) -> str` ("Encontrei 3 problemas e 5 avisos." + até 10 itens + `mensagens.msg("pastas-protegidas", n=…)`); CLI `acad validar [<DISC>] [--raiz]` → saída 1 se houver `erro`, `dados.achados` = lista de dicts.

- [x] **Step 1: Testes que falham**

```python
# testes/unidade/test_validar.py
import json
from pathlib import Path
from acad.cli import main

SEM = Path(__file__).resolve().parents[1] / "amostras/fasoft/2026/Segundo Semestre"

def test_validar_amostra(capsys):
    code = main(["validar", "--raiz", str(SEM), "--json"])
    d = json.loads(capsys.readouterr().out)
    cods = {a["codigo"] for a in d["dados"]["achados"]}
    assert code == 1
    assert {"sufixo-proibido", "pasta-sem-prefixo", "nome-lista-sem-prefixo", "readme-desatualizado",
            "numero-aula-repetido"} <= cods

def test_validar_uma_disciplina(capsys):
    main(["validar", "04", "--raiz", str(SEM), "--json"])
    d = json.loads(capsys.readouterr().out)
    assert all("Recepção" not in a["caminho"] for a in d["dados"]["achados"])

def test_yaml_invalido_nao_derruba(capsys, semestre_sintetico):
    (semestre_sintetico / "01 - Disc A - 3º Período" / "01 - Planejamento" / "aulas.yaml").write_text("aulas: 3\n", encoding="utf-8")
    main(["validar", "--raiz", str(semestre_sintetico), "--json"])
    d = json.loads(capsys.readouterr().out)
    assert any(a["codigo"] == "esquema-invalido" for a in d["dados"]["achados"])
    assert any(a["codigo"] == "pasta-sem-prefixo" for a in d["dados"]["achados"])
```

```python
# testes/integracao/test_drive_somente_leitura.py
import builtins, json, os
from pathlib import Path
import pytest
from acad.cli import main

DRIVE = Path(r"G:\Meu Drive\Fasoft\2026\Segundo Semestre")

@pytest.mark.drive
def test_validar_drive_real_sem_escrever(capsys, monkeypatch):
    if not DRIVE.exists():
        pytest.skip("Drive ausente")
    real_open = builtins.open
    def open_so_leitura(f, mode="r", *a, **k):
        if str(f).lower().startswith("g:") and any(c in mode for c in "wax+"):
            raise AssertionError(f"tentativa de escrita no Drive: {f}")
        return real_open(f, mode, *a, **k)
    monkeypatch.setattr(builtins, "open", open_so_leitura)
    for nome in ("replace", "rename", "remove", "unlink", "mkdir", "makedirs", "rmdir"):
        monkeypatch.setattr(os, nome, lambda *a, **k: (_ for _ in ()).throw(AssertionError(nome)))
    main(["validar", "--raiz", str(DRIVE), "--json"])
    d = json.loads(capsys.readouterr().out)
    cods = {(a["codigo"], a["caminho"].split("/")[-1]) for a in d["dados"]["achados"]}
    assert ("sufixo-proibido", "Cronograma - Estrutura de Dados 2.xlsx.bak") in cods
    assert ("pasta-sem-prefixo", "11-Relatórios") in cods
    assert ("pasta-sem-prefixo", "_ferramentas") in cods
    assert any(c == "readme-desatualizado" for c, _ in cods)
    assert "02 - Alunos" not in json.dumps(d, ensure_ascii=False).replace("07 - TFC 1/02 - Alunos", "")
```

(O `registro.log` e o estado ficam em `ACAD_DADOS`, que aponta para `tmp_path` — fora do Drive.)

- [x] **Step 2: Rodar e ver falhar.**
- [x] **Step 3: Implementar** `validar_semestre` chamando, por disciplina: nomenclatura/estrutura (uma vez por semestre), leitura tolerante dos YAML (`try`/`ErroAcad` → achado `esquema-invalido` com o nome do arquivo), carga (para cada turma com encontros), dia não letivo, pré-requisitos, cobertura, avaliações, manifestos, número repetido, slide divergente. Ordenar achados por (`nivel` erro→aviso→info, `caminho`, `codigo`).
- [x] **Step 4: Rodar e ver passar** — `$PY -m pytest -m "not drive" -v` e depois `$PY -m pytest -m drive -v`.
- [x] **Step 5: Registrar o resultado no Drive real** (somente leitura): `$PY -m acad validar --raiz "G:\Meu Drive\Fasoft\2026\Segundo Semestre" > "$SCRATCH/validar-drive.txt"` e colar o resumo (sem nomes de aluno — não deve haver) na descrição do commit.
- [x] **Step 6: Commit** — `git commit -m "feat: acad validar sobre o semestre inteiro"`

### Tarefa 23: Núcleo da configuração guiada (`perfil detectar`, `iniciar`, `disciplina criar`, `turma criar`, `disciplina estrutura`)

**Files:**
- Create: `acad/perfil/detectar.py`, `acad/comandos/perfil.py`
- Modify: `acad/contexto.py` (gravar configuração)
- Test: `testes/unidade/test_configuracao_guiada.py`

**Interfaces:**
- Produces:
  - `detectar(raiz: Path, perfil) -> dict` → `{"raiz_fasoft": str|None, "semestres": [{"pasta": rel, "ano": 2026, "periodo": 2}], "disciplinas": [{"pasta", "numero", "nome", "periodo", "tem_cronograma": bool, "subpastas_faltando": [...]}], "pasta_avaliacoes", "pasta_modelos"}`; aceita a raiz Fasoft ou a pasta do semestre; semestre = `^\d{4}/(Primeiro|Segundo) Semestre$`.
  - `acad perfil detectar --raiz <pasta>` (não grava; `mensagem` em português: "Encontrei o 2º semestre de 2026 com 6 disciplinas: …. Quer que eu use essa organização?").
  - `acad iniciar <semestre AAAA-N> --raiz <pasta do semestre> [--perfil fasoft] [--confirmar]` — sem `--confirmar` só descreve; com `--confirmar` grava `dir_dados()/configuracao.yaml` (estado local, fora do workspace; validado pelo esquema `semestre`). (Ajuste em relação à tabela da spec §8: estado local usa `--confirmar`, não proposta — a proposta é para o workspace.)
  - `acad disciplina criar <CODIGO> --pasta "<nome da pasta>" --nome "<nome>" --carga <n> [--unidade hora_relogio|hora_aula] [--minutos-hora-aula 50]` → proposta `01 - Planejamento/disciplina.yaml` (`planejamento.status: rascunho`).
  - `acad turma criar <DISC> --turma TA --horario "2 19:00 20:40 [sala]" [--horario …] [--fuso America/Sao_Paulo]` → proposta `turma-TA.yaml`.
  - `acad disciplina estrutura <DISC>` → proposta com `criar-pasta` para cada subpasta padrão faltando.

- [x] **Step 1: Testes que falham** (no `semestre_sintetico`): `detectar` acha 1 disciplina e `subpastas_faltando == ["04 - Projetos e Entregáveis"]`? — não: essa pasta existe mas é protegida; garantir que pasta protegida **existente** não conte como faltando (`subpastas_faltando == []`); `iniciar` sem `--confirmar` não cria `configuracao.yaml`, com `--confirmar` cria e o `contexto.raiz_semestre` passa a funcionar sem `--raiz`; `turma criar` com `--horario "8 19:00 20:40"` falha com mensagem "dia da semana vai de 1 (segunda) a 7 (domingo)"; `disciplina criar --unidade hora_aula` sem `--minutos-hora-aula` falha explicando; `disciplina estrutura` após apagar `05 - Materiais de Referência` propõe `criar-pasta` só para ela.
- [x] **Step 2–4:** falhar, implementar, passar.
- [x] **Step 5: Commit** — `git commit -m "feat: núcleo da configuração guiada"`

### Tarefa 24: Gerar aula — roteiro, código, lista e manifesto (`acad gerar aula`)

**Files:**
- Create: `acad/geracao/__init__.py`, `acad/geracao/nomes.py`, `acad/geracao/slides.py`, `acad/geracao/aula.py`, `acad/comandos/gerar.py`, `modelos/roteiro-aula.md`, `modelos/lista.md`, `esquemas/conteudo-aula.schema.json`
- Test: `testes/unidade/test_gerar_aula.py`

**Interfaces:**
- Consumes: `ler_aulas`, `ler_encontros`, `Operacao`, `criar_proposta`, `montar_manifesto`, `hash_item`, `hash_bytes`, `hash_pasta`.
- Produces:
  - `nomes.limpar_tema(t) -> str` (remove `<>:"/\|?*`, espaços duplos, ponto final); `nomes.slug(t) -> str` (`sem_acento`, não alfanumérico → `-`, sem `-` repetido); `nomes.arquivos_da_aula(num: str, tema: str) -> dict` → `{"slides": "02 - Aulas/Aula NN - T.pptx", "roteiro": "02 - Aulas/Aula NN - Roteiro de Aula - T.md", "codigo": "06 - Código e Exemplos/aula-NN-slug", "lista": "03 - Atividades e Listas/Lista NN - T.md"}`.
  - `slides.GeradorSlides` (Protocol: `gerar(conteudo: dict, template: Path | None) -> bytes`), `slides.GeradorSlidesFalso` (devolve `b"PPTX-FALSO:" + titulo`), `slides.GeradorSlidesBloqueado` (levanta `ErroAcad("decisao-pendente-d4", mensagens.msg("decisao-pendente", assunto="qual modelo de slides usar"), saida=4)`), `slides.obter_gerador() -> GeradorSlides` (bloqueado até a Tarefa 26).
  - Contrato de conteúdo (`--conteudo arquivo.json`, esquema `conteudo-aula`): `{"tema": str, "roteiro": {"objetivo": str, "blocos": [{"titulo": str, "minutos": int, "texto": str}]}, "codigo": {"arquivos": {"<nome>": "<texto>"}}?, "lista": {"questoes": [{"enunciado": str, "resposta": str?}]}?, "slides": {"slides": [{"tipo": "capa"|"topicos"|"codigo"|"tabela"|"nota", ...}]}?}`. O LLM escreve esse arquivo; o núcleo valida e grava.
  - `planejar_aula(ws, semestre, disc: Path, num: str, conteudo: dict, gerador: GeradorSlides, agora: datetime, revisar: bool = False) -> tuple[list[Operacao], list[str]]` — devolve operações e avisos. Regras: aula `aprovada`/`ministrada` sem `revisar` → `ErroAcad("aula-aprovada", "Essa aula já foi aprovada por você. Para mudar, peça para revisar a aula.", saida=1)`; arquivo existente → `substituir` (arquivamento automático); slides bloqueados → aviso "Os slides ficam para depois: ainda falta escolher o modelo." e o resto segue; estimativa: soma de `minutos` × soma da duração dos encontros da aula (de `encontros-*.yaml`), desvio > 15% → aviso "O roteiro tem 140 min, mas a aula tem 100 min."; atualiza a aula em `aulas.yaml` (`slides`/`roteiro`/`codigo`/`lista` com os caminhos, `status: rascunho`, `manifesto` com `entradas` = `{"<disc>/01 - Planejamento/aulas.yaml#Aula NN": hash_item(aula sem manifesto), "<pasta de modelos de slides>": hash_pasta(...) quando usada, "<programa da disciplina>.pdf": hash_bytes(...) quando existir}`) e inclui `substituir aulas.yaml`.
  - CLI: `acad gerar aula <DISC> --aula NN --conteudo <arquivo.json> [--revisar]` → proposta; mensagem: "Vou criar 3 arquivos na pasta de aulas e atualizar o plano da disciplina."

- [x] **Step 1: Testes que falham**

```python
# testes/unidade/test_gerar_aula.py
from datetime import datetime
import pytest, yaml
from acad.arquivos.privacidade import Workspace
from acad.geracao.aula import planejar_aula
from acad.geracao.slides import GeradorSlidesFalso, GeradorSlidesBloqueado
from acad.geracao.nomes import arquivos_da_aula, slug
from acad.erros import ErroAcad

DISC = "01 - Disc A - 3º Período"
CONTEUDO = {"tema": "Rotações AVL",
            "roteiro": {"objetivo": "Aplicar rotações", "blocos": [{"titulo": "Revisão", "minutos": 20, "texto": "…"},
                                                                    {"titulo": "Rotações", "minutos": 80, "texto": "…"}]},
            "codigo": {"arquivos": {"main.go": "package main\n"}},
            "lista": {"questoes": [{"enunciado": "Insira 3, 2, 1 numa AVL."}]},
            "slides": {"slides": [{"tipo": "capa", "titulo": "Rotações AVL"}]}}

@pytest.fixture
def disc(semestre_sintetico):
    d = semestre_sintetico / DISC
    (d / "01 - Planejamento" / "aulas.yaml").write_text(yaml.safe_dump({"versao_esquema": 1, "disciplina": "DA",
        "aulas": [{"id": "Aula 03", "tema": "Rotações AVL", "status": "planejada", "objetivos": [], "prerequisitos": [],
                   "encontros_necessarios": 1}]}, allow_unicode=True), encoding="utf-8")
    return d

def test_nomes_canonicos():
    a = arquivos_da_aula("03", "Rotações AVL: casos?")
    assert a["roteiro"] == "02 - Aulas/Aula 03 - Roteiro de Aula - Rotações AVL casos.md"
    assert a["codigo"] == "06 - Código e Exemplos/aula-03-rotacoes-avl-casos"
    assert slug("Árvore B+") == "arvore-b"

def test_planeja_arquivos_e_manifesto(semestre_sintetico, disc):
    ws = Workspace(semestre_sintetico, [])
    ops, avisos = planejar_aula(ws, semestre_sintetico, disc, "03", CONTEUDO, GeradorSlidesFalso(), datetime(2026, 10, 20, 14, 2))
    destinos = {o.destino for o in ops}
    assert f"{DISC}/02 - Aulas/Aula 03 - Rotações AVL.pptx" in destinos
    assert f"{DISC}/06 - Código e Exemplos/aula-03-rotacoes-avl/main.go" in destinos
    aulas = yaml.safe_load(next(o for o in ops if o.destino.endswith("aulas.yaml")).conteudo)
    a = aulas["aulas"][0]
    assert a["status"] == "rascunho" and a["manifesto"]["aprovado"] is False
    assert f"{DISC}/01 - Planejamento/aulas.yaml#Aula 03" in a["manifesto"]["entradas"]

def test_slides_bloqueados_nao_impedem_resto(semestre_sintetico, disc):
    ops, avisos = planejar_aula(Workspace(semestre_sintetico, []), semestre_sintetico, disc, "03", CONTEUDO,
                                GeradorSlidesBloqueado(), datetime(2026, 10, 20))
    assert not any(o.destino.endswith(".pptx") for o in ops)
    assert any("slides ficam para depois" in a.lower() for a in avisos)

def test_aula_aprovada_recusa(semestre_sintetico, disc):
    p = disc / "01 - Planejamento" / "aulas.yaml"
    d = yaml.safe_load(p.read_text(encoding="utf-8")); d["aulas"][0]["status"] = "aprovada"
    p.write_text(yaml.safe_dump(d, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ErroAcad) as e:
        planejar_aula(Workspace(semestre_sintetico, []), semestre_sintetico, disc, "03", CONTEUDO, GeradorSlidesFalso(), datetime(2026, 10, 20))
    assert e.value.codigo == "aula-aprovada"

def test_estimativa_de_tempo(semestre_sintetico, disc):
    longo = {**CONTEUDO, "roteiro": {"objetivo": "x", "blocos": [{"titulo": "a", "minutos": 140, "texto": "…"}]}}
    (disc / "01 - Planejamento" / "encontros-TA.yaml").write_text(yaml.safe_dump({"versao_esquema": 1, "gerado_por": "acad 0.1.0",
        "gerado_em": "2026-10-01T10:00:00-03:00", "entradas": {}, "encontros": [{"id": "E03", "data": "2026-08-10",
        "inicio": "19:00", "fim": "20:40", "status": "previsto", "aulas": ["Aula 03"], "funcao": "conteudo", "origem": "horario"}]}), encoding="utf-8")
    _, avisos = planejar_aula(Workspace(semestre_sintetico, []), semestre_sintetico, disc, "03", longo, GeradorSlidesFalso(), datetime(2026, 10, 20))
    assert any("140 min" in a and "100 min" in a for a in avisos)

def test_conteudo_invalido(semestre_sintetico, disc):
    with pytest.raises(ErroAcad) as e:
        planejar_aula(Workspace(semestre_sintetico, []), semestre_sintetico, disc, "03", {"tema": 1}, GeradorSlidesFalso(), datetime(2026, 10, 20))
    assert e.value.codigo == "esquema-invalido"
```

- [x] **Step 2–4:** falhar, implementar, passar. Roteiro renderizado de `modelos/roteiro-aula.md` com `string.Template` (`${tema}`, `${objetivo}`, `${blocos}`, `${duracao_total}`); lista de `modelos/lista.md`.
- [x] **Step 5: Commit** — `git commit -m "feat: geração de aula com roteiro, código, lista e manifesto"`

### Tarefa 25: Ciclo de status da aula (`acad aula status`)

**Files:**
- Create: `acad/planejamento/status.py`, `acad/comandos/aula.py`
- Test: `testes/unidade/test_status_aula.py`

**Interfaces:**
- Produces: `TRANSICOES = {"planejada": {"rascunho"}, "rascunho": {"revisada", "planejada"}, "revisada": {"aprovada", "rascunho"}, "aprovada": {"ministrada"}, "ministrada": set()}`; `mudar_status(aula: dict, novo: str, agora: datetime, encontro: str | None = None) -> dict` — transição fora da tabela → `ErroAcad("transicao-invalida", "Uma aula em rascunho precisa ser revisada antes de ser aprovada.")` (mensagem por caso); `aprovada` grava `manifesto.aprovado = True`, `aprovado_em`; `ministrada` exige `encontro` e acrescenta em `ministrada_em`. CLI `acad aula status <DISC> --aula NN <novo> [--encontro E05]` → proposta substituindo `aulas.yaml` (e `encontros-*.yaml` marcando o encontro `realizado` quando `ministrada`).
- [x] **Step 1: Testes que falham** — tabela completa de transições válidas e inválidas (parametrize), aprovação grava `aprovado_em`, `ministrada` sem encontro falha, `ministrada` marca o encontro `realizado`.
- [x] **Step 2–4:** falhar, implementar, passar.
- [x] **Step 5: Commit** — `git commit -m "feat: ciclo de status da aula com aprovação do professor"`

### Tarefa 26: Gerador de slides `.pptx` — **BLOQUEADA (D4)**

Só começar depois que o professor confirmar o modelo de referência (spec §2.1) e a abordagem. O executor **não** decide sozinho: se a decisão não estiver registrada no `ANDAMENTO.md`/spec, pule esta tarefa.

**Files (abordagem 1, recomendada):**
- Create: `acad/geracao/slides_pptx.py`
- Modify: `acad/geracao/slides.py` (`obter_gerador()` devolve `GeradorSlidesPptx`), `pyproject.toml` (+ `python-pptx`, versão via `pip index versions python-pptx`)
- Test: `testes/unidade/test_slides_pptx.py`

**Interfaces:**
- Consumes: contrato `slides` da Tarefa 24; especificação `09 - Modelos/Modelo de Slides UniRV/Padrao Visual de Slides - UniRV Fasoft.md` (lida do workspace em tempo de execução; tokens e medidas transcritos para constantes no código, com comentário citando a seção do documento).
- Produces: `GeradorSlidesPptx(pasta_modelo: Path).gerar(conteudo, template) -> bytes`.

- [ ] **Step 1: Ler** `Padrao Visual de Slides - UniRV Fasoft.md` inteiro (somente leitura) e listar em `acad/geracao/slides_pptx.py` (docstring) as medidas, a paleta e os componentes que o MVP cobre: capa, tópicos, bloco de código, tabela, nota.
- [ ] **Step 2: Testes que falham**

```python
# testes/unidade/test_slides_pptx.py
import io
from pptx import Presentation
from pptx.util import Emu
from acad.geracao.slides_pptx import GeradorSlidesPptx

CONTEUDO = {"slides": [{"tipo": "capa", "titulo": "Rotações AVL"},
                       {"tipo": "topicos", "titulo": "Casos", "itens": ["LL", "RR", "LR", "RL"]},
                       {"tipo": "codigo", "titulo": "Rotação à direita", "codigo": "func rotDir() {}"}]}

def _pres():
    return Presentation(io.BytesIO(GeradorSlidesPptx(None).gerar(CONTEUDO, None)))

def test_tamanho_16x9_do_padrao():
    p = _pres()
    assert (p.slide_width, p.slide_height) == (Emu(9144000), Emu(5143500))

def test_um_slide_por_item():
    assert len(_pres().slides) == 3

def test_titulo_presente():
    textos = [sh.text_frame.text for sh in _pres().slides[1].shapes if sh.has_text_frame]
    assert "Casos" in textos
```

- [ ] **Step 3–4:** implementar e passar.
- [ ] **Step 5: Conferência visual (humana):** gerar um deck de exemplo, abrir no PowerPoint e comparar com `referencia/*.png` do modelo; registrar o resultado no commit.
- [ ] **Step 6: Commit** — `git commit -m "feat: slides no padrão visual UniRV"`

### Tarefa 27: Gerar avaliação em LaTeX com gabarito (`acad gerar avaliacao`)

**Files:**
- Create: `acad/geracao/avaliacao.py`, `acad/geracao/latex.py`, `modelos/prova.tex`, `esquemas/conteudo-avaliacao.schema.json`
- Modify: `acad/comandos/gerar.py`
- Test: `testes/unidade/test_avaliacao.py`, `testes/integracao/test_latex.py`

**Interfaces:**
- Consumes: `regra_avaliacao_nao_ministrada`, `ler_aulas`, `ler_encontros`, `Operacao`, `montar_manifesto`, `Perfil.pasta_avaliacoes`.
- Produces:
  - `escapar_latex(t: str) -> str` (`\ & % $ # _ { } ~ ^`).
  - `versoes(questoes: list[dict], semente: int, n: int) -> list[list[dict]]` — versão A = ordem original; demais = `random.Random(f"{semente}-{i}")` embaralhando questões e alternativas (com a resposta acompanhando a alternativa); reprodutível.
  - `nome_arquivo(disciplina_nome: str, etapa: str, descricao: str, turma: str, versao: str | None, gabarito: bool, ext: str) -> str` → `"Estrutura de Dados 2 - N1 - Avaliação - TA.tex"`, `"… - TA - Versão B.tex"`, `"… - TA - Gabarito.tex"` (padrão do README do semestre).
  - `renderizar(modelo: str, dados: dict, questoes: list[dict], gabarito: bool) -> str` — preenche `\avaliacaoTitulo{}`, `\avaliacaoDisciplina{}`, `\avaliacaoProfessor{}`, `\avaliacaoData{}` (formato dd/mm/aaaa) por substituição do argumento entre chaves; insere o corpo após a linha que contém `A partir daqui entra o corpo da prova` (modelo institucional) ou no marcador `%% CORPO %%` (modelo genérico `modelos/prova.tex`); questões numeradas com `enumerate`; gabarito acrescenta a resposta em negrito.
  - `latex.compilador() -> list[str] | None` (`tectonic` → `["tectonic", "-X", "compile"]` se existir; senão `pdflatex` → 2 passes; checar com `shutil.which`, sintaxe conferida em `tectonic --help` no dia); `latex.compilar(tex: Path) -> Path | None` (compila numa pasta temporária com os arquivos de apoio do modelo copiados ao lado — `.sty`, logo — e devolve o PDF; falha → `None` + detalhe no registro).
  - CLI: `acad gerar avaliacao <DISC> --etapa N1 --turma TA --data D --conteudo q.json [--descricao Avaliação] [--versoes 1] [--semente 1234]` → valida cobertura antes (erro bloqueia: "A prova cobre a Aula 09, que só acontece em 08/09 — depois da prova."); proposta com `.tex` (+ `.pdf` se compilou) de cada versão e do gabarito em `<NN - Avaliações>/<etapa>/`, e `01 - Planejamento/avaliacoes/<etapa>-<turma>.yaml` (esquema `avaliacao`, com `semente`, `arquivos`, `manifesto`). Modelo: `<NN - Modelos>/Modelo LaTeX/modelo-prova.tex` do workspace se existir (lido, nunca copiado para o repositório), senão `modelos/prova.tex`.
- [ ] **Step 1: Testes que falham** (unidade): `escapar_latex("50% de R$ 10_000")`; `versoes` reprodutível com a mesma semente e diferente com outra; resposta acompanha a alternativa embaralhada; `nome_arquivo` nos três formatos; `renderizar` com o modelo genérico contém `\avaliacaoDisciplina{Estrutura de Dados 2}` e as questões; gabarito contém as respostas e a prova não; CLI recusa avaliação sobre aula futura (saída 1, `codigo == "avaliacao-sobre-nao-ministrada"`); proposta cai em `08 - Avaliações/N1/`.
- [ ] **Step 2: Teste `latex`** (marcador `latex`): compila o `modelos/prova.tex` renderizado e confere que o PDF começa com `%PDF`.
- [ ] **Step 3–4:** falhar, implementar, passar (`$PY -m pytest -m "not drive" -v`; `-m latex` se houver compilador — registrar no commit se não houver).
- [ ] **Step 5: Commit** — `git commit -m "feat: avaliação em LaTeX com gabarito e versões por semente"`

### Tarefa 28: Exportar encontros em ICS (`acad exportar ics`)

**Files:**
- Create: `acad/exportadores/__init__.py`, `acad/exportadores/ics.py`, `acad/comandos/exportar.py`
- Test: `testes/unidade/test_exportar_ics.py`

**Interfaces:**
- Produces: `exportar_ics(encontros: list[Encontro], disciplina_nome: str, turma: str, fuso: str, aulas: dict[str, str]) -> bytes` — um `VEVENT` por encontro não cancelado; `UID` estável `<disciplina-slug>-<turma>-<data>-<inicio>@librarius`; `SUMMARY` "Estrutura de Dados 2 (TA) — Aula 03: Rotações AVL" (ou "Avaliação"); `DTSTART`/`DTEND` com `TZID` do fuso; `PRODID:-//Librarius//acad//PT`. CLI `acad exportar ics <DISC> --turma TA` → proposta criando/substituindo `01 - Planejamento/Cronograma - <Disciplina> - TA.ics`.
- [ ] **Step 1: Testes que falham** — reabrir com `icalendar` e conferir número de eventos (cancelados fora), UID estável entre duas exportações, horário 19:00 em `America/Sao_Paulo`.
- [ ] **Step 2–4:** falhar, implementar, passar.
- [ ] **Step 5: Commit** — `git commit -m "feat: exportação do cronograma para agenda"`

### Tarefa 29: Regenerar a planilha do cronograma a partir do modelo (`acad cronograma exportar-planilha`)

**Files:**
- Create: `acad/cronograma/exportar_planilha.py`
- Modify: `acad/comandos/cronograma.py`
- Test: `testes/unidade/test_exportar_planilha.py`

**Interfaces:**
- Produces: `exportar_planilha(titulo: str, encontros: list[Encontro], aulas: dict[str, dict]) -> bytes` — mesmo leiaute da planilha real (título em B1, cabeçalho na linha 3 `Semanas | Datas | Aulas | Tópicos` em B–E, dados a partir da linha 4, uma linha por encontro, "Semana N" só na primeira linha de cada semana ISO, encontro cancelado com o motivo em Tópicos, avaliação com "AVALIAÇÃO"). CLI `acad cronograma exportar-planilha <DISC> --turma TA` → proposta **substituindo** `Cronograma - <Disciplina>.xlsx` (a versão anterior vai para `99 - Arquivo` pela regra da Tarefa 11).
- [ ] **Step 1: Teste que falha (ida e volta):** `importar_cronograma(ler_cronograma(exportar_planilha(...)))` reproduz os mesmos encontros (data, aulas, função, status) e as mesmas aulas da importação da amostra real.
- [ ] **Step 2–4:** falhar, implementar, passar.
- [ ] **Step 5: Commit** — `git commit -m "feat: planilha do cronograma regenerada a partir do plano"`

---

## Fase 3 — Skills no padrão Agent Skills (briefing §15)

### Tarefa 30: Lançador `scripts/acad.py` (sem dependências)

**Files:**
- Create: `scripts/acad.py`
- Test: `testes/unidade/test_lancador.py`, `testes/integracao/test_lancador_real.py`

**Interfaces:**
- Produces (spec §4.2): `python <raiz>/scripts/acad.py <args do acad>` em qualquer host local. Funções testáveis: `raiz() -> Path` (`Path(__file__).resolve().parents[1]`), `versao() -> str` (de `pyproject.toml` via `tomllib`), `dependencias() -> list[str]` (`[project].dependencies`), `dir_dados() -> Path` (`ACAD_DADOS`, `CLAUDE_PLUGIN_DATA`, `PLUGIN_DATA`, `%LOCALAPPDATA%\librarius`, `~/.local/share/librarius`), `python_do_ambiente(amb: Path) -> Path` (`Scripts/python.exe` no Windows, `bin/python` fora), `preparar(amb: Path, executar=subprocess.run) -> Path` (cria venv com `uv venv` se `shutil.which("uv")`, senão `sys.executable -m venv`; instala dependências com `uv pip install --python …` ou `pip install`; grava `amb/.pronto` com a lista de dependências; se `.pronto` igual, não faz nada), `main(argv) -> int` (Python < 3.11 → mensagem e saída 3; falha de instalação → "Não consegui baixar os componentes de que preciso. Confira a internet e tente de novo." e saída 3; senão executa `[python_do_ambiente, "-m", "acad", *argv]` com `PYTHONPATH=<raiz>` e `PYTHONUTF8=1`, repassando a saída e o código).
- O núcleo roda **a partir da raiz do plugin** (não é instalado como pacote no ambiente): assim `esquemas/`, `modelos/` e `acad/` são sempre os da versão instalada do plugin.

- [ ] **Step 1: Testes que falham**

```python
# testes/unidade/test_lancador.py
import importlib.util, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("lancador", RAIZ / "scripts" / "acad.py")
L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)

def test_versao_e_dependencias():
    assert L.versao() == "0.1.0"
    assert any(d.startswith("pyyaml") for d in L.dependencias())

def test_dir_dados_prioridade(monkeypatch, tmp_path):
    monkeypatch.setenv("ACAD_DADOS", str(tmp_path))
    assert L.dir_dados() == tmp_path

def test_preparar_nao_reinstala(tmp_path, monkeypatch):
    chamadas = []
    monkeypatch.setattr(L.shutil, "which", lambda n: None)
    fake = lambda cmd, **k: chamadas.append(cmd) or type("R", (), {"returncode": 0})()
    L.preparar(tmp_path / "amb", executar=fake)
    n = len(chamadas)
    L.preparar(tmp_path / "amb", executar=fake)
    assert n >= 2 and len(chamadas) == n

def test_python_antigo(monkeypatch, capsys):
    monkeypatch.setattr(L.sys, "version_info", (3, 9, 0))
    assert L.main(["ambiente", "verificar"]) == 3
    assert "Python" in capsys.readouterr().out

def test_falha_de_instalacao_explica(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("ACAD_DADOS", str(tmp_path))
    monkeypatch.setattr(L, "preparar", lambda amb, **k: (_ for _ in ()).throw(L.FalhaInstalacao("x")))
    assert L.main(["ambiente", "verificar"]) == 3
    assert "internet" in capsys.readouterr().out
```

```python
# testes/integracao/test_lancador_real.py
import json, subprocess, sys
from pathlib import Path
import pytest

RAIZ = Path(__file__).resolve().parents[2]

@pytest.mark.rede
def test_lancador_cria_ambiente_e_roda(tmp_path):
    env = {**__import__("os").environ, "ACAD_DADOS": str(tmp_path)}
    r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "acad.py"), "ambiente", "verificar", "--json"],
                       capture_output=True, text=True, encoding="utf-8", env=env, timeout=900)
    assert r.returncode == 0, r.stdout + r.stderr
    assert json.loads(r.stdout)["ok"] is True
```

Registrar o marcador `rede` no `conftest.py` (`"rede": "baixa dependências da internet"`).

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar** `scripts/acad.py` só com biblioteca padrão (`os, sys, shutil, subprocess, tomllib, pathlib, venv`), mensagens em português simples, sem `print` de caminhos longos. `class FalhaInstalacao(Exception)`.
- [ ] **Step 4: Rodar e ver passar** — `$PY -m pytest testes/unidade/test_lancador.py -v` e `$PY -m pytest -m rede -v` (rede real; leva minutos na primeira vez).
- [ ] **Step 5: Commit** — `git commit -m "feat: lançador que prepara o ambiente sem instalação manual"`

### Tarefa 31: Infraestrutura das skills (trecho comum, sincronização e testes de conformidade)

**Files:**
- Create: `scripts/trechos/chamar-nucleo.md`, `scripts/sincronizar-skills.py`, `acad/plataformas/__init__.py`, `acad/plataformas/skills.py`
- Test: `testes/unidade/test_skills.py`

**Interfaces:**
- Consumes: spec §11; `plataformas/agent-skills/FONTE.md` (reler antes; atualizar a data se a especificação mudou).
- Produces:
  - `skills.SKILLS = ("usando-agente-academico", "organizador-academico", "planejador-semestre", "distribuidor-ementa", "gerador-aulas", "gerador-avaliacoes", "validador-academico")`.
  - `skills.ler_skill(pasta: Path) -> tuple[dict, str]` (frontmatter, corpo); `skills.problemas(pasta: Path) -> list[str]` — regras Agent Skills: `name` 1–64, `^[a-z0-9]+(-[a-z0-9]+)*$`, igual à pasta; `description` 1–1024; `compatibility` ≤ 500 se houver; só chaves `name, description, license, compatibility, metadata, allowed-tools`; corpo < 500 linhas; seções obrigatórias `## Quando usar`, `## Como conversar com o professor`, `## Passo a passo`, `## Exemplos de pedidos`; trecho entre `<!-- inicio:chamar-nucleo -->` e `<!-- fim:chamar-nucleo -->` idêntico a `scripts/trechos/chamar-nucleo.md`.
  - `skills.comandos_citados(corpo: str) -> set[str]` (padrão `` `acad ([a-z-]+(?: [a-z-]+)?)`` ``) e teste de que cada um está registrado em `acad.cli._COMANDOS`.
  - `scripts/sincronizar-skills.py [--verificar]` — reescreve o trecho em todas as skills (ou só verifica; saída 1 se divergir).

Conteúdo de `scripts/trechos/chamar-nucleo.md`:

```markdown
## Como chamar o núcleo

1. Raiz do plugin: `${CLAUDE_PLUGIN_ROOT}`. Se o texto anterior não virou um caminho de pasta, a raiz é a pasta dois níveis acima deste `SKILL.md`.
2. Antes do primeiro uso na conversa, rode `python "<raiz>/scripts/acad.py" ambiente verificar --json` (no Windows, se `python` não existir, tente `py -3`). Se nenhum dos dois existir, explique ao professor que falta um programa gratuito chamado Python, ofereça instalar e só instale com o "sim" dele.
3. Rode sempre `python "<raiz>/scripts/acad.py" <comando> --json` e leia a resposta: mostre ao professor apenas o campo `mensagem` e os `avisos`, com suas palavras, em português simples. Nunca mostre caminhos longos, códigos, nomes de arquivo técnicos nem o conteúdo bruto da resposta.
4. Se a resposta trouxer `proposta`, mostre o `resumo` em uma ou duas frases e pergunte se pode continuar. Só depois de um "sim" claro, rode `acad aplicar <id>`. Para voltar atrás: `acad desfazer`.
5. Saída 3: falta algo no computador — explique e ofereça ajuda. Saída 4: falta uma decisão do professor — diga qual e siga com o resto.
6. Sem acesso ao computador do professor (ChatGPT ou versão web): diga que essa parte precisa do assistente instalado no computador e pare.
7. Arquivos de alunos (notas, pastas de TFC, relatórios, entregas) nunca são abertos, nem se pedirem de passagem; se o professor pedir de forma explícita, explique que esta versão não trabalha com dados de alunos.
```

- [ ] **Step 1: Testes que falham**

```python
# testes/unidade/test_skills.py
from pathlib import Path
import subprocess, sys
import pytest
from acad.plataformas import skills
from acad import cli
import acad.comandos  # noqa: F401  (registra os comandos)

RAIZ = Path(__file__).resolve().parents[2]

def test_existem_as_sete_skills():
    assert sorted(p.name for p in (RAIZ / "skills").iterdir() if p.is_dir()) == sorted(skills.SKILLS)

@pytest.mark.parametrize("nome", skills.SKILLS)
def test_conformidade(nome):
    assert skills.problemas(RAIZ / "skills" / nome) == []

@pytest.mark.parametrize("nome", skills.SKILLS)
def test_comandos_citados_existem(nome):
    _, corpo = skills.ler_skill(RAIZ / "skills" / nome)
    assert skills.comandos_citados(corpo) <= set(cli._COMANDOS) | {"aplicar", "desfazer"}

def test_trecho_sincronizado():
    r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "sincronizar-skills.py"), "--verificar"])
    assert r.returncode == 0

def test_regra_de_nome_pega_erros(tmp_path):
    d = tmp_path / "Errada"; d.mkdir()
    (d / "SKILL.md").write_text("---\nname: errada\ndescription: x\n---\ncorpo\n", encoding="utf-8")
    probs = skills.problemas(d)
    assert any("pasta" in p for p in probs) and any("Quando usar" in p for p in probs)
```

- [ ] **Step 2: Rodar e ver falhar** (pasta `skills/` ainda não existe).
- [ ] **Step 3: Implementar** `acad/plataformas/skills.py` e `scripts/sincronizar-skills.py`. Os testes por skill passam na Tarefa 32; nesta tarefa, `test_regra_de_nome_pega_erros` deve passar.
- [ ] **Step 4: Rodar** — `$PY -m pytest testes/unidade/test_skills.py::test_regra_de_nome_pega_erros -v` → PASS.
- [ ] **Step 5: Commit** — `git commit -m "feat: conformidade das skills com o padrão Agent Skills"`

### Tarefa 32: As sete skills e o `AGENTS.md` de fallback

**Files:**
- Create: `skills/<nome>/SKILL.md` (7), `AGENTS.md`
- Test: `testes/unidade/test_skills.py` (já existe), `testes/unidade/test_agents_md.py`

**Interfaces:**
- Consumes: subcomandos das Tarefas 12–29; trecho comum; spec §1A do briefing.
- Produces: skills com frontmatter abaixo (descrições exatas; `compatibility` igual em todas: `Precisa do assistente instalado no computador do professor e de Python 3.11 ou mais novo (o assistente ajuda a instalar).`; `metadata: {autor: "Vinicius Martinez", projeto: "librarius"}`).

| Pasta / `name` | `description` |
|---|---|
| `usando-agente-academico` | `Ponto de entrada do assistente acadêmico Librarius. Use no início da conversa com um professor e sempre que ele perguntar o que você sabe fazer, como fazer algo, ou pedir ajuda com aulas, cronograma, provas ou organização de pastas. Explica as demais skills e quando usar cada uma.` |
| `organizador-academico` | `Configura o assistente na primeira vez (instituição, pasta dos materiais, disciplinas, turmas e horários) e confere a organização das pastas do semestre contra as regras de nomes. Use quando o professor começar a usar o assistente, pedir para organizar ou conferir pastas, ou perguntar quais arquivos estão fora do padrão.` |
| `planejador-semestre` | `Importa o calendário da instituição e a planilha de cronograma de cada disciplina, gera os encontros de cada turma e responde consultas como "aula de hoje", "o que tenho amanhã" e "tem slide pronto?". Use para planejar o semestre, consultar o cronograma ou registrar que uma aula foi cancelada.` |
| `distribuidor-ementa` | `Distribui o conteúdo do programa da disciplina pelos encontros do semestre, respeitando pré-requisitos, avaliações e revisões, e mostra o que muda quando uma aula é cancelada. Use quando o professor pedir para montar ou refazer o plano de aulas a partir da ementa.` |
| `gerador-aulas` | `Prepara o material de uma aula: slides no modelo da instituição, roteiro do professor, código de exemplo e lista de exercícios, sempre com aprovação do professor antes de gravar. Use quando o professor pedir para preparar, revisar ou aprovar uma aula.` |
| `gerador-avaliacoes` | `Monta provas e atividades com gabarito no modelo da instituição, só com conteúdo já dado até a data da prova, e gera versões diferentes de forma reproduzível. Use quando o professor pedir uma prova, avaliação N1/N2/N3, simulado ou gabarito.` |
| `validador-academico` | `Confere, sem depender de opinião da IA, carga horária, feriados, cobertura dos objetivos, pré-requisitos, nomes de arquivos e materiais desatualizados, e explica cada problema em linguagem simples. Use quando o professor pedir para conferir, revisar ou validar o semestre ou uma disciplina.` |

Corpo de cada skill (todas com as quatro seções obrigatórias e o trecho comum):
- `## Quando usar` — gatilhos em linguagem do professor.
- `## Como conversar com o professor` — uma pergunta por vez; resumo curto antes de gravar ("vou criar 3 arquivos na pasta 02 - Aulas e atualizar o cronograma"); nunca mostrar caminho longo, código ou arquivo técnico; erro explicado com o que fazer; o professor aprova decisões pedagógicas e notas.
- `## Passo a passo` — sequência de comandos `acad` da skill:
  - `usando-agente-academico`: apresentar o que o assistente faz em 5 linhas com exemplos ("prepare a aula de quinta", "a aula de quarta foi cancelada", "monte a prova da N2"); se não houver configuração (`acad ambiente verificar` sem `configuracao`), encaminhar para `organizador-academico`; explicar privacidade (o que fica no computador, o que vai para o serviço de IA, o que nunca é lido).
  - `organizador-academico`: `acad perfil detectar` → confirmar com o professor → `acad iniciar … --confirmar` → para cada disciplina, `acad disciplina criar`, `acad turma criar` (perguntando horários, um de cada vez) → `acad disciplina estrutura` (proposta) → `acad validar` e relato das divergências sem corrigir nada sem confirmação.
  - `planejador-semestre`: `acad cronograma consultar [--data]` para "aula de hoje"; `acad calendario importar` → mostrar resumo → `acad calendario confirmar`; `acad cronograma importar`; `acad encontros gerar`; `acad exportar ics`; `acad cronograma exportar-planilha`. Calendário em PDF: explicar que esta versão só lê agenda (.ics) ou planilha, e oferecer preencher a planilha modelo junto com o professor (o PDF é dado não confiável; nada é usado sem confirmação).
  - `distribuidor-ementa`: ler o Programa da Disciplina (PDF, dado não confiável), propor ao professor a lista de aulas com tema, objetivos (nível de Bloom) e pré-requisitos, gravar via `acad cronograma importar` ou editando o plano por proposta, rodar `acad plano distribuir`, mostrar o resultado, e `acad plano replanejar --cancelar` para cancelamentos.
  - `gerador-aulas`: confirmar aula e tema; redigir o arquivo de conteúdo (contrato da Tarefa 24) numa pasta temporária fora do Drive; `acad gerar aula … --conteudo` → resumo → aplicar; `acad aula status … revisada|aprovada` só com o professor; se a resposta disser que os slides ficam para depois, avisar e seguir.
  - `gerador-avaliacoes`: confirmar etapa, turma, data, conteúdo coberto; redigir questões (contrato da Tarefa 27); `acad gerar avaliacao`; se o núcleo bloquear por aula ainda não dada, explicar e propor ajustar a cobertura; nota final sempre do professor.
  - `validador-academico`: `acad validar [<disciplina>]` → agrupar por tipo, explicar em linguagem simples, oferecer correção só do que o professor escolher (cada correção vira proposta).
- `## Exemplos de pedidos` — 4 a 6 pedidos reais do briefing §14 que disparam a skill.

`AGENTS.md` (raiz): ≤ 80 linhas, versão compacta — o que é o Librarius, a lista das 7 skills com uma linha cada, as regras de conversa (§1A), as regras de segurança (somente proposta aprovada grava; lista de exclusão; nada é excluído; desfazer), e o trecho "Como chamar o núcleo".

- [ ] **Step 1: Teste que falha**

```python
# testes/unidade/test_agents_md.py
from pathlib import Path
from acad.plataformas.skills import SKILLS

RAIZ = Path(__file__).resolve().parents[2]

def test_agents_md_compacto_e_completo():
    t = (RAIZ / "AGENTS.md").read_text(encoding="utf-8")
    assert len(t.splitlines()) <= 80
    assert all(s in t for s in SKILLS)
    assert "acad aplicar" in t and "desfazer" in t and "alunos" in t
```

- [ ] **Step 2: Rodar todos os testes de skills e ver falhar.**
- [ ] **Step 3: Escrever as 7 skills e o `AGENTS.md`**; rodar `$PY scripts/sincronizar-skills.py` para inserir o trecho.
- [ ] **Step 4: Rodar e ver passar** — `$PY -m pytest testes/unidade/test_skills.py testes/unidade/test_agents_md.py -v`; se `skills-ref` estiver disponível (`pip index versions skills-ref`), rodar `skills-ref validate skills/<nome>` em cada uma e registrar.
- [ ] **Step 5: Teste de leitura com o professor (humano, rápido):** ler a `description` e a seção "Como conversar" em voz alta procurando jargão; trocar o que soar técnico.
- [ ] **Step 6: Commit** — `git commit -m "feat: sete skills do MVP e AGENTS.md de fallback"`

---

## Fase 4 — Adaptadores por plataforma com validação estrutural (briefing §4)

Regra de todas as tarefas desta fase: **Step 0 = reler `plataformas/<host>/FONTE.md` e as URLs oficiais nele; se algo mudou, atualizar o `FONTE.md` (fatos + data) antes de escrever o manifesto.** Campos usados devem estar no `FONTE.md`.

### Tarefa 33: Validador de manifestos e adaptador Claude Code / Cowork

**Files:**
- Create: `acad/plataformas/manifestos.py`, `scripts/validar-manifestos.py`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`
- Test: `testes/unidade/test_manifestos_hosts.py`

**Interfaces:**
- Produces: `manifestos.validar_claude(raiz: Path) -> list[str]`, depois (tarefas seguintes) `validar_codex`, `validar_antigravity`, `validar_opencode`; `manifestos.validar_todos(raiz) -> dict[str, list[str]]`; `scripts/validar-manifestos.py` imprime por host "ok" ou os problemas e sai 1 se houver algum. Checagens Claude: `.claude-plugin/plugin.json` com `name == "librarius"`, kebab-case, não reservado; `version`, `description`, `author.name` presentes; nenhuma chave fora da lista do `FONTE.md`; caminhos de componente começam com `./` e existem; não existe pasta `bin/` na raiz; nada além de `plugin.json`/`marketplace.json` em `.claude-plugin/`; `marketplace.json` com `name`, `owner.name`, `plugins[0].name == "librarius"`, `plugins[0].source == "./"`.

```json
// .claude-plugin/plugin.json
{
  "name": "librarius",
  "displayName": "Librarius",
  "version": "0.1.0",
  "description": "Assistente para professores universitários: cronograma, aulas, provas e organização de pastas, com conferência automática de datas, carga horária e nomes.",
  "author": { "name": "Vinicius Martinez" },
  "homepage": "https://github.com/vnmartinez/librarius",
  "repository": "https://github.com/vnmartinez/librarius",
  "license": "MIT",
  "keywords": ["professor", "universidade", "cronograma", "aulas", "provas"]
}
```

```json
// .claude-plugin/marketplace.json
{
  "name": "librarius",
  "description": "Plugins do projeto Librarius",
  "owner": { "name": "Vinicius Martinez" },
  "plugins": [
    { "name": "librarius", "source": "./", "version": "0.1.0",
      "description": "Assistente para professores universitários" }
  ]
}
```

- [ ] **Step 0:** reler `plataformas/claude/FONTE.md` e https://code.claude.com/docs/en/plugins-reference, https://code.claude.com/docs/en/plugin-marketplaces; atualizar se preciso.
- [ ] **Step 1: Testes que falham**

```python
# testes/unidade/test_manifestos_hosts.py
import json, shutil
from pathlib import Path
import pytest
from acad.plataformas import manifestos

RAIZ = Path(__file__).resolve().parents[2]

def _copia(tmp_path):
    destino = tmp_path / "plugin"
    shutil.copytree(RAIZ, destino, ignore=shutil.ignore_patterns(".git", ".venv", "testes", "__pycache__"))
    return destino

def test_claude_ok():
    assert manifestos.validar_claude(RAIZ) == []

def test_claude_recusa_bin(tmp_path):
    d = _copia(tmp_path); (d / "bin").mkdir()
    assert any("bin" in p for p in manifestos.validar_claude(d))

def test_claude_recusa_caminho_sem_ponto_barra(tmp_path):
    d = _copia(tmp_path); m = d / ".claude-plugin" / "plugin.json"
    j = json.loads(m.read_text(encoding="utf-8")); j["skills"] = "skills/"
    m.write_text(json.dumps(j), encoding="utf-8")
    assert manifestos.validar_claude(d)

@pytest.mark.hosts
def test_claude_validate_oficial():
    import subprocess
    if not shutil.which("claude"):
        pytest.skip("claude ausente")
    r = subprocess.run(["claude", "plugin", "validate", str(RAIZ), "--strict"], capture_output=True, text=True)
    assert r.returncode == 0 and "Validation passed" in r.stdout, r.stdout + r.stderr
```

- [ ] **Step 2–4:** falhar, escrever manifestos e validador, passar (`$PY -m pytest testes/unidade/test_manifestos_hosts.py -v` e `-m hosts`). `claude plugin validate` só lê arquivos: não instala nada.
- [ ] **Step 5 (opcional, hook de sessão):** consultar https://code.claude.com/docs/en/hooks (evento `SessionStart` e formato de saída que injeta contexto), registrar em `plataformas/claude/FONTE.md`, e só então criar `hooks/hooks.json` que injeta um lembrete para carregar `usando-agente-academico`. Se a documentação não for clara, não criar (nenhuma função depende do hook).
- [ ] **Step 6: Commit** — `git commit -m "feat: manifestos do Claude Code e validador de manifestos"`

### Tarefa 34: Adaptador Codex e `plugin.json` da raiz (portátil)

**Files:**
- Create: `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `plugin.json`, `plataformas/codex/plugin.schema.json` (cópia do esquema Agent Plugins baixado no dia, com a URL e a data no `FONTE.md`)
- Modify: `acad/plataformas/manifestos.py`, `testes/unidade/test_manifestos_hosts.py`

**Interfaces:**
- Produces: `validar_codex(raiz) -> list[str]` — `plugin.json` da raiz valida contra `plataformas/codex/plugin.schema.json` (com `jsonschema`) **e** tem só `$schema`, `name`, `description` (restrição do Antigravity, spec §12); `.codex-plugin/plugin.json` com `name`, `version`, `description`, `skills == "./skills/"`, `interface.displayName`, `interface.category`; `.agents/plugins/marketplace.json` com `name`, `plugins[0].name == "librarius"`, `plugins[0].source == {"source": "local", "path": "./"}`, `policy.installation` ∈ {`AVAILABLE`, `INSTALLED_BY_DEFAULT`, `NOT_AVAILABLE`}, `category` presente.

```json
// plugin.json  (raiz — compartilhado com o Antigravity)
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "librarius",
  "description": "Assistente para professores universitários: cronograma, aulas, provas e organização de pastas."
}
```

```json
// .codex-plugin/plugin.json
{
  "name": "librarius",
  "version": "0.1.0",
  "description": "Assistente para professores universitários: cronograma, aulas, provas e organização de pastas.",
  "author": { "name": "Vinicius Martinez", "url": "https://github.com/vnmartinez" },
  "homepage": "https://github.com/vnmartinez/librarius",
  "repository": "https://github.com/vnmartinez/librarius",
  "license": "MIT",
  "keywords": ["professor", "universidade", "cronograma", "aulas", "provas"],
  "skills": "./skills/",
  "interface": {
    "displayName": "Librarius",
    "shortDescription": "Cronograma, aulas e provas para professores",
    "longDescription": "Planeja o semestre, prepara aulas e provas no modelo da instituição e confere datas, carga horária e nomes de arquivo, sempre pedindo aprovação antes de gravar.",
    "developerName": "Vinicius Martinez",
    "category": "Productivity",
    "capabilities": ["Interactive", "Read", "Write"],
    "defaultPrompt": ["Qual é a minha aula de hoje?", "Prepare a aula de quinta."],
    "websiteURL": "https://github.com/vnmartinez/librarius"
  }
}
```

```json
// .agents/plugins/marketplace.json
{
  "name": "librarius",
  "interface": { "displayName": "Librarius" },
  "plugins": [
    { "name": "librarius", "source": { "source": "local", "path": "./" },
      "policy": { "installation": "AVAILABLE", "authentication": "ON_INSTALL" },
      "category": "Productivity" }
  ]
}
```

- [ ] **Step 0:** reler `plataformas/codex/FONTE.md`, https://developers.openai.com/codex/plugins/build.md e https://developers.openai.com/plugins/deploy/submission (campos de `interface` e valores de `category`/`capabilities`); baixar `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json` para `plataformas/codex/plugin.schema.json`.
- [ ] **Step 1: Testes que falham:** `validar_codex(RAIZ) == []`; cópia com `"version"` no `plugin.json` da raiz falha (regra do Antigravity); cópia com `policy.installation = "SEMPRE"` falha; cópia sem `category` falha.
- [ ] **Step 2–4:** falhar, implementar, passar.
- [ ] **Step 5: Commit** — `git commit -m "feat: manifestos do Codex e manifesto portátil na raiz"`

### Tarefa 35: Adaptador Antigravity (app, IDE, CLI)

**Files:**
- Modify: `acad/plataformas/manifestos.py`, `testes/unidade/test_manifestos_hosts.py`, `plataformas/antigravity/FONTE.md`

**Interfaces:**
- Produces: `validar_antigravity(raiz) -> list[str]` — `plugin.json` na raiz existe; chaves ⊆ {`$schema`, `name`, `description`}; `name` casa `^[a-zA-Z0-9-_]+$`; `skills/<nome>/SKILL.md` existem. (MCP do Antigravity entra na Tarefa 40.)
- [ ] **Step 0:** reler https://antigravity.google/docs/plugins?tab=cli; tentar de novo o esquema https://antigravity.google/schemas/v1/plugin.json; registrar resultado.
- [ ] **Step 1: Testes que falham:** `validar_antigravity(RAIZ) == []`; cópia com `"displayName"` na raiz falha; cópia com nome `"libra rius"` falha.
- [ ] **Step 2–4:** falhar, implementar, passar.
- [ ] **Step 5 (`hosts`, sem instalar):** `agy plugin --help` e `agy plugin list --json` para confirmar que a CLI existe e o formato de listagem; registrar no `FONTE.md`. **Não** rodar `agy plugin install` aqui — instalação é na matriz (Tarefa 42), com o professor.
- [ ] **Step 6: Commit** — `git commit -m "feat: adaptador Antigravity"`

### Tarefa 36: Adaptador OpenCode

**Files:**
- Create: `opencode.json`, `.opencode/INSTALAR.md`
- Modify: `acad/plataformas/manifestos.py`, `testes/unidade/test_manifestos_hosts.py`

**Interfaces:**
- Produces: `opencode.json` de exemplo (`$schema: "https://opencode.ai/config.json"`, `skills: ["<pasta do clone>/skills"]` — no arquivo do repositório, `"./skills"`, que resolve a partir do diretório de trabalho quando o OpenCode é aberto na raiz do clone); `.opencode/INSTALAR.md` — roteiro que o próprio agente segue: (1) clonar `https://github.com/vnmartinez/librarius` numa pasta fora do Drive (perguntar ao professor; padrão `%USERPROFILE%\librarius`), (2) se o OpenCode aceitar a opção `skills` (v2), acrescentar o caminho das skills ao `opencode.json` global; senão, criar links (junction no Windows: `mklink /J`) de cada skill em `~/.config/opencode/skills/<nome>`, (3) rodar `python <clone>/scripts/acad.py ambiente verificar`, (4) dizer ao professor, em português simples, que terminou e como pedir ajuda. `validar_opencode(raiz) -> list[str]`: `opencode.json` é JSON estrito, `skills` é lista de strings, cada caminho relativo existe; `INSTALAR.md` cita as duas formas (v2 e estável).
- [ ] **Step 0:** reler `plataformas/opencode/FONTE.md` e as três URLs.
- [ ] **Step 1–4:** testes que falham (JSON inválido; `skills` como string), implementar, passar.
- [ ] **Step 5: Commit** — `git commit -m "feat: adaptador OpenCode com roteiro de instalação"`

### Tarefa 37: Sincronização de versão

**Files:**
- Create: `scripts/sincronizar-versao.py`, `acad/plataformas/versao.py`
- Test: `testes/unidade/test_versao.py`

**Interfaces:**
- Produces: `versao.ARQUIVOS = [("pyproject.toml", "project.version"), ("acad/__init__.py", "__version__"), (".claude-plugin/plugin.json", "version"), (".claude-plugin/marketplace.json", "plugins.0.version"), (".codex-plugin/plugin.json", "version")]` (o `plugin.json` da raiz fica fora: o Antigravity proíbe `version`); `versao.ler_todas(raiz) -> dict[str, str]`; `versao.aplicar(raiz, nova: str) -> None` (preserva formatação: troca só o valor com regex ancorada); `scripts/sincronizar-versao.py <nova>` e `--verificar` (sai 1 se houver mais de uma versão).
- [ ] **Step 1: Testes que falham:** no repositório, `ler_todas` devolve um único valor; numa cópia, `aplicar("0.2.0")` muda os cinco e mais nada (`git diff --stat` simulado comparando bytes fora das linhas de versão); `--verificar` sai 1 com uma versão divergente.
- [ ] **Step 2–4:** falhar, implementar, passar.
- [ ] **Step 5: Commit** — `git commit -m "chore: versão única sincronizada em todos os manifestos"`

### Tarefa 38: Pacotes de skills para o ChatGPT

**Files:**
- Create: `scripts/empacotar-chatgpt.py`, `acad/plataformas/chatgpt.py`, `scripts/trechos/chamar-nucleo-chatgpt.md`
- Test: `testes/unidade/test_chatgpt.py`

**Interfaces:**
- Produces: `chatgpt.empacotar(raiz: Path, destino: Path) -> list[Path]` — um `dist/chatgpt/<skill>.zip` por skill, com **uma pasta de topo** `<skill>/` e exatamente um `SKILL.md`; no `SKILL.md` empacotado, o trecho "Como chamar o núcleo" é trocado por `chamar-nucleo-chatgpt.md` ("Nesta versão do ChatGPT eu não acesso os arquivos do seu computador. Posso explicar, planejar com você e redigir textos; para gravar, conferir datas ou ler suas pastas, use o assistente instalado no computador."); tamanho ≤ 50 MB; `dist/` continua no `.gitignore`.
- [ ] **Step 0:** tentar de novo https://help.openai.com/en/articles/20001066-skills-in-chatgpt. Se abrir, atualizar `plataformas/chatgpt/FONTE.md` e ajustar o formato do zip ao que a página disser; se continuar inacessível, seguir o formato da API (registrado no `FONTE.md`) e anotar a pendência no `FONTE.md`.
- [ ] **Step 1: Testes que falham:** para cada zip, `ZipFile.namelist()` tem um único prefixo de topo igual ao nome da skill e exatamente um `SKILL.md`; o `SKILL.md` empacotado não contém `scripts/acad.py` nem `${CLAUDE_PLUGIN_ROOT}`; frontmatter preservado (`skills.problemas` sobre a pasta extraída, ignorando a regra do trecho comum).
- [ ] **Step 2–4:** falhar, implementar, passar.
- [ ] **Step 5: Commit** — `git commit -m "feat: pacotes de skills para o ChatGPT"`

### Tarefa 39: `INSTALAR.md` e `README.md`

**Files:**
- Create: `INSTALAR.md`
- Modify: `README.md`
- Test: `testes/unidade/test_documentacao.py`

**Interfaces:**
- Produces: `INSTALAR.md` com uma seção por superfície (Claude Code, app Claude/Cowork, Codex, Antigravity app/IDE/CLI, OpenCode, ChatGPT), cada uma com o caminho **sem terminal** primeiro (passos na interface gráfica, conforme `FONTE.md`; onde a interface não estiver documentada, dizer "peça ao assistente: 'instale o Librarius a partir de github.com/vnmartinez/librarius'"), e uma seção final `## Para usuários avançados` com todos os comandos de terminal (`claude plugin marketplace add vnmartinez/librarius`, `claude plugin install librarius@librarius`, `codex plugin marketplace add vnmartinez/librarius`, `agy plugin install https://github.com/vnmartinez/librarius`, OpenCode via `.opencode/INSTALAR.md`). `README.md` reescrito para o público do briefing (§1A): o que o Librarius faz, para quem, privacidade em linguagem simples (o que fica no computador, o que vai para o serviço de IA, o que nunca é lido), hosts suportados, estado do projeto, licença.
- [ ] **Step 1: Teste que falha**

```python
# testes/unidade/test_documentacao.py
from pathlib import Path
RAIZ = Path(__file__).resolve().parents[2]

def test_instalar_sem_terminal_antes_do_avancado():
    t = (RAIZ / "INSTALAR.md").read_text(encoding="utf-8")
    antes, _, depois = t.partition("## Para usuários avançados")
    assert depois, "falta a seção para usuários avançados"
    assert "```" not in antes                      # nenhum comando antes da seção avançada
    for host in ("Claude Code", "Cowork", "Codex", "Antigravity", "OpenCode", "ChatGPT"):
        assert host in antes
    assert "claude plugin marketplace add" in depois and "agy plugin install" in depois

def test_readme_publico_certo():
    t = (RAIZ / "README.md").read_text(encoding="utf-8")
    assert "sem conhecimento de programação" in t or "sem formação técnica" in t
    assert "alunos" in t and "MIT" in t
```

- [ ] **Step 2–4:** falhar, escrever, passar.
- [ ] **Step 5: Commit** — `git commit -m "docs: instalação por host e README para professores"`

---

## Fase 5 — Servidor MCP local do núcleo

### Tarefa 40: `acad mcp` (stdio) e declaração nos hosts

**Files:**
- Create: `acad/mcp.py`, `acad/comandos/mcp.py`, `.mcp.json`, `mcp_config.json`
- Modify: `acad/cli.py` (extrair `executar(argv) -> tuple[int, Resultado]` usado por `main` e pelo MCP), `opencode.json` (`mcp`), `pyproject.toml` (+ `mcp`, versão via `pip index versions mcp`), `acad/plataformas/manifestos.py`, `plataformas/*/FONTE.md`
- Test: `testes/integracao/test_mcp.py`, `testes/unidade/test_manifestos_hosts.py`

**Interfaces:**
- Consumes: `cli.executar`.
- Produces: ferramentas MCP (nomes com hífen) `ambiente-verificar`, `cronograma-consultar(data?, raiz?)`, `validar(disciplina?, raiz?)`, `encontros-gerar(disciplina, turma, raiz?)`, `plano-distribuir(disciplina, turma, raiz?)`, `plano-replanejar(disciplina, turma, cancelar, motivo?, raiz?)`, `gerar-aula(disciplina, aula, conteudo, revisar?, raiz?)` (`conteudo` como objeto; o servidor grava num arquivo temporário fora do workspace), `gerar-avaliacao(...)`, `aplicar(id)`, `desfazer()`; cada uma devolve o envelope JSON da spec §8 como texto. Descrição de cada ferramenta em português e com o aviso "só grava com `aplicar`".
- Declaração por host (fazer só depois de reler a fonte de cada um):
  - Claude (e Codex, pelo formato de compatibilidade) — `.mcp.json`: `{"mcpServers": {"librarius": {"command": "python", "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/acad.py", "mcp"]}}}`.
  - Antigravity — `mcp_config.json`: **formato ainda não verificado** (spec §12); Step 0 obrigatório: achar a documentação oficial do `mcp_config.json` de plugin; se não houver, não criar o arquivo e registrar a pendência no `FONTE.md`.
  - OpenCode — `opencode.json`: `"mcp": {"librarius": {"type": "local", "command": ["python", "./scripts/acad.py", "mcp"], "enabled": true}}`.

- [ ] **Step 0:** ler a documentação do SDK Python oficial (https://github.com/modelcontextprotocol/python-sdk, README da versão instalada) e usar só a API que estiver lá para servidor stdio e cliente stdio; reler `FONTE.md` de Claude, Codex, Antigravity e OpenCode na parte de MCP.
- [ ] **Step 1: Testes que falham**

```python
# testes/integracao/test_mcp.py
import json, sys
from pathlib import Path
import pytest

AMOSTRA = Path(__file__).resolve().parents[1] / "amostras" / "fasoft"

@pytest.mark.asyncio
async def test_lista_e_chama_ferramentas():
    # Usar o cliente stdio do SDK conforme o README lido no Step 0:
    # abrir `sys.executable -m acad mcp` com PYTHONPATH=raiz e ACAD_DADOS temporário,
    # inicializar a sessão, listar ferramentas e chamar `cronograma-consultar`.
    nomes, resposta = await _sessao_mcp(AMOSTRA, "cronograma-consultar", {"data": "2026-07-28", "raiz": str(AMOSTRA)})
    assert {"validar", "cronograma-consultar", "aplicar", "desfazer"} <= set(nomes)
    assert json.loads(resposta)["dados"]["quantidade_aulas"] == 1

@pytest.mark.asyncio
async def test_ferramenta_de_escrita_so_propoe(tmp_path, semestre_sintetico):
    _, resposta = await _sessao_mcp(semestre_sintetico, "validar", {"raiz": str(semestre_sintetico)})
    assert json.loads(resposta)["proposta"] is None
```

`_sessao_mcp(raiz, ferramenta, argumentos) -> tuple[list[str], str]` é um auxiliar no próprio arquivo de teste, escrito com a API do cliente stdio do SDK lida no Step 0. Se o SDK não trouxer suporte a `pytest` assíncrono, acrescentar `pytest-asyncio` (versão via `pip index versions`) às dependências de teste, ou usar `anyio.run` dentro de um teste síncrono — o que o README do SDK recomendar.
Acrescentar a `test_manifestos_hosts.py`: `.mcp.json` válido (Claude: `mcpServers.librarius.command`/`args` com `${CLAUDE_PLUGIN_ROOT}`), `opencode.json` com `mcp.librarius.type == "local"` e `command` lista.

- [ ] **Step 2–4:** falhar, implementar, passar (`$PY -m pytest testes/integracao/test_mcp.py -v` e a suíte inteira).
- [ ] **Step 5 (`hosts`, sem instalar):** `claude plugin validate . --strict` continua passando com o `.mcp.json` (a CLI também checa servidores MCP declarados).
- [ ] **Step 6: Commit** — `git commit -m "feat: servidor MCP local do núcleo"`

---

## Fase 6 — Instalação e teste em cada superfície (briefing §13)

### Tarefa 41: Roteiros da matriz por host e verificações automáticas não invasivas

**Files:**
- Create: `testes/hosts/claude-code.md`, `testes/hosts/claude-cowork.md`, `testes/hosts/codex.md`, `testes/hosts/antigravity-app.md`, `testes/hosts/antigravity-ide.md`, `testes/hosts/antigravity-cli.md`, `testes/hosts/opencode.md`, `testes/hosts/chatgpt.md`, `testes/hosts/resultados.md`, `testes/integracao/test_hosts.py`

**Interfaces:**
- Produces: cada roteiro com (a) pré-requisitos; (b) **caminho do professor, sem terminal** (passo a passo na interface do host, baseado no `FONTE.md`); (c) caminho avançado (comandos do `INSTALAR.md`); (d) as seis checagens da spec §15 com o resultado esperado e onde anotar: 1) plugin aparece instalado; 2) a skill `usando-agente-academico` carrega ("o que você sabe fazer?"); 3) `acad ambiente verificar` roda pelo lançador; 4) "qual a aula de hoje de Estrutura de Dados 2?" (ou `--data` fixa) bate com a saída do oráculo para a mesma data; 5) leitura do Drive real em modo leitura (hosts locais); 6) ferramentas MCP aparecem (onde houver). `resultados.md`: tabela host × checagem com data, versão do host, versão do plugin, resultado (ok / falhou / não se aplica) e observação. `ChatGPT`: só checagens 1–2 (skills carregam), 4 e 5 = "não se aplica (D1/D2)".
- `testes/integracao/test_hosts.py` (marcador `hosts`, só comandos que **não alteram** a configuração do usuário): `claude plugin validate . --strict`; `codex plugin marketplace --help` e `codex plugin marketplace list` (só leitura); `agy plugin list --json`; `opencode --version`. Cada um pulado se a CLI não existir.
- [ ] **Step 1: Escrever `test_hosts.py`** e rodar `$PY -m pytest -m hosts -v`; registrar a saída em `resultados.md` (seção "verificações automáticas").
- [ ] **Step 2: Escrever os oito roteiros e `resultados.md`** (tabela vazia).
- [ ] **Step 3: Revisar** os roteiros contra os `FONTE.md`: nenhum passo de interface que não esteja documentado; onde não houver documentação, o passo é "peça ao assistente para instalar a partir do endereço do repositório".
- [ ] **Step 4: Commit** — `git commit -m "test: roteiros da matriz de instalação por host"`

### Tarefa 42: Execução da matriz e critério de pronto (humano + agente)

Esta tarefa instala o plugin nos hosts reais da máquina: **só com autorização explícita do professor**, porque altera a configuração dos agentes dele. Leitura do Drive continua somente leitura.

**Files:**
- Modify: `testes/hosts/resultados.md`, `plataformas/<host>/FONTE.md` (achados), `docs/superpowers/specs/2026-10-22-plugin-academico-design.md` (só se um achado mudar contrato)

- [ ] **Step 1:** pedir autorização ao professor, host por host.
- [ ] **Step 2:** para cada host autorizado, seguir o roteiro (caminho sem terminal primeiro; avançado se a interface não permitir) e preencher `resultados.md`.
- [ ] **Step 3:** confirmar os pontos em aberto da spec §12: Codex aceita `path: "./"` e substitui `${CLAUDE_PLUGIN_ROOT}` no `.mcp.json`?; Antigravity aceita o `plugin.json` da raiz com `$schema` Agent Plugins? (se não: testar `.antigravity-plugin/plugin.json` e registrar); OpenCode estável ou v2?; Cowork carrega MCP stdio? Cada resposta vai para o `FONTE.md` do host; se exigir mudança de manifesto, abrir tarefa nova (TDD) antes de seguir.
- [ ] **Step 4: Critério de pronto do MVP (briefing §15), checklist:**
  - [ ] `acad validar` roda sem LLM sobre o Segundo Semestre de 2026 real (somente leitura) — Tarefa 22.
  - [ ] `acad cronograma consultar` reproduz a skill `cronograma` no Drive real — Tarefa 10 (`-m drive`).
  - [ ] O mesmo comando de consulta roda em Claude Code, Claude Cowork, Codex, Antigravity (app, IDE e CLI) e OpenCode — `resultados.md`.
  - [ ] As skills carregam no ChatGPT — `resultados.md`.
  - [ ] Primeiro caso de uso completo: ED2 2027-1 até as quatro primeiras aulas com material gerado, validado e aprovado — **depende de D3 (carga) e D4 (slides)** e do calendário 2027-1; registrar como pendente se as decisões não vierem.
  - [ ] Teste com dois professores sem formação técnica (instalam, concluem a configuração guiada e preparam uma aula sem ajuda) — etapa humana; registrar data, host e observações em `resultados.md`.
- [ ] **Step 5: Commit** — `git commit -m "test: resultados da matriz de instalação"`

---

## Ordem, dependências e bloqueios

- Fases em sequência (briefing §0). Dentro da Fase 2: 7→8→9→10→11→12 em ordem; 13→14→15→16→17; 18→19; 20→21→22; 23 após 12; 24→25; 26 **BLOQUEADA (D4)**; 27 após 21; 28 e 29 após 17.
- D1/D2: não bloqueiam nenhuma tarefa deste plano (ChatGPT recebe só skills; MCP remoto é v3).
- D3: nenhuma tarefa bloqueada; o veredito da carga real fica como aviso até a decisão.
- D4: só a Tarefa 26 e o item "quatro aulas com slides" do critério de pronto.
- Ao fim de cada fase: `$PY -m pytest -m "not drive and not hosts and not rede and not latex" -v` verde, depois os marcadores disponíveis na máquina.
