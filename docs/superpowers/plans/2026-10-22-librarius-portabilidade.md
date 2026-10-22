# Librarius — portabilidade para outras instituições — plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Um professor de outra instituição cria o perfil dele a partir da própria pasta, valida o semestre e gera slides sem a marca UniRV, enquanto o perfil `fasoft` do dono mantém exatamente o comportamento atual.

**Architecture:** O perfil (YAML validado por esquema, agora v2 com v1 ainda válido) passa a carregar estrutura de pastas, modelos e identidade visual; o código lê tudo do objeto `Perfil`. Perfis do usuário ficam em `dir_dados()/perfis/` e vencem os empacotados; sem configuração vale o perfil `neutro`. Um teste de referência, gravado antes da refatoração, prova que os slides do fasoft não mudam.

**Tech Stack:** Python ≥ 3.11, `pyyaml`, `jsonschema` (Draft 2020-12), `python-pptx` 1.x, `pytest`.

**Spec:** `docs/superpowers/specs/2026-10-22-librarius-portabilidade-design.md` (decisões P1–P11, compatibilidade §4, aceite §5). Leia a spec inteira antes da Tarefa 1.

## Global Constraints

- Trabalhe só neste worktree (`librarius-portabilidade`, branch `vnmartinez/librarius-portabilidade`). Nada na `main`.
- Nunca ler nem escrever em `G:\Meu Drive\Fasoft`, exceto os testes já marcados `drive` (só leitura). Nada de dado de aluno.
- Contrato: `acad <comando> --json` com envelope `ok/mensagem/avisos/erros/proposta`. Escrita só por proposta + `acad aplicar <id>` + `acad desfazer`. Não invente comandos além de `perfil criar`, `perfil importar`, `perfil listar`.
- Textos ao professor em português simples, sem nenhum termo de `acad.mensagens.TERMOS_PROIBIDOS` (`yaml`, `json`, `hash`, `sha`, `schema`, `stack`, `exception`, `traceback`, `path`, `stdout`).
- Nomes de arquivos e pastas novos do projeto: minúsculas, sem acento.
- Perfis v1 continuam válidos (`versao_esquema: 1`), provado por teste.
- Com o perfil `fasoft`: slides idênticos (resumos de `testes/esperados/slides-fasoft.json`) e validações/cronograma iguais (suíte existente verde).
- Comando da suíte: `.venv/Scripts/python -m pytest -q`. Marcadores extras: `-m drive`, `-m hosts`, `-m rede`, `-m latex`.
- Siga o estilo do código vizinho: nomes em português, `from __future__ import annotations`, comentários raros.
- Commit ao fim de cada tarefa, mensagem em português no formato `tipo: resumo`, terminando com `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Mapa de arquivos

| Arquivo | Papel |
|---|---|
| `testes/ferramentas/referencia_slides.py` (novo) | `resumos(bytes) -> dict` e gravação da referência |
| `testes/esperados/slides-fasoft.json` (novo) | Resumos SHA-256 das partes do `.pptx` fasoft, gravados de `d944cbe` |
| `testes/esperados/perfil-fasoft-v1.yaml` (novo) | Cópia literal do `fasoft.yaml` v1 |
| `esquemas/perfil.schema.json` | v2: `estrutura`, `modelos`, `slides` opcionais |
| `acad/perfil/padroes.py` (novo) | Padrões de `estrutura` para v1 |
| `acad/perfil/perfil.py` | `Perfil` ampliado; leitura usuário → pacote |
| `acad/perfil/validar.py` (novo) | `problemas_do_perfil` em português simples |
| `acad/perfil/perfis/fasoft.yaml` | Migra para v2 explícito |
| `acad/perfil/perfis/neutro.yaml` (novo) | Perfil sem marca |
| `acad/geracao/identidade.py` (novo) | `IdentidadeSlides`, `IDENTIDADE_NEUTRA`, `paleta_de_cor` |
| `acad/geracao/slides_pptx.py`, `acad/geracao/slides.py` | Identidade injetada |
| `acad/perfil/detectar.py`, `acad/cronograma/consulta.py` | Semestre e raiz pela estrutura |
| `acad/perfil/inferir.py` (novo) | Perfil a partir da pasta |
| `acad/comandos/perfil.py` | `perfil criar/importar/listar`; fim do padrão `fasoft` |
| `acad/contexto.py` | `PERFIL_PADRAO = "neutro"` |
| Demais com literais (Tarefa 7) | Nomes de pasta pelo perfil |
| `skills/organizador-academico/SKILL.md`, `skills/usando-agente-academico/SKILL.md` | Fluxo do perfil |
| `testes/integracao/test_outra_instituicao.py` (novo) | Ponta a ponta |

## Ordem de execução

0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13 (a 12 é a ponta a ponta de outra instituição; a 13 é a verificação final). A Tarefa 1 **precisa** rodar antes de qualquer mudança em `acad/` (grava a referência a partir do código de `d944cbe`).

---

### Task 0: Ambiente e linha de base

**Files:** nenhum versionado (`.venv/` já é ignorado; confira com `git check-ignore .venv`).

- [x] **Step 1: Criar o venv local**

Run (PowerShell): `py -3 -m venv .venv; .venv\Scripts\pip install -e ".[dev]"` — se o extra `dev` não existir em `pyproject.toml`, rode `.venv\Scripts\pip install -e . pytest`.

- [x] **Step 2: Rodar a suíte de base**

Run: `.venv/Scripts/python -m pytest -q`
Expected: tudo verde (312 passam no padrão; os marcados ficam de fora). Anote o número exato; ele é a linha de base. Se algo falhar já aqui, pare e avise o orquestrador — não é falha deste plano.

- [x] **Step 3: Conferir `python-pptx`**

Run: `.venv/Scripts/python -c "import pptx; print(pptx.__version__)"` e anote a versão.

---

### Task 1: Referência de compatibilidade (antes de refatorar)

**Files:**
- Create: `testes/ferramentas/referencia_slides.py`
- Create: `testes/esperados/slides-fasoft.json` (gerado)
- Create: `testes/esperados/perfil-fasoft-v1.yaml` (cópia)
- Create: `testes/unidade/test_compat_fasoft.py`

**Interfaces:**
- Produces: `resumos(dados: bytes) -> dict[str, str]`; `gerar_referencia() -> bytes` (gera o `.pptx` fasoft com conteúdo e logos fixos); `ARQUIVO_REFERENCIA: Path`. A Tarefa 4 troca só a função que constrói o gerador.

- [x] **Step 1: Copiar o perfil v1**

Run: `git show d944cbe:acad/perfil/perfis/fasoft.yaml > testes/esperados/perfil-fasoft-v1.yaml` (Bash). Confira que o arquivo começa com `versao_esquema: 1`.

- [x] **Step 2: Escrever a ferramenta**

```python
# testes/ferramentas/referencia_slides.py
"""Referência dos slides fasoft: resumos das partes do .pptx (gravada a partir de d944cbe)."""
from __future__ import annotations

import hashlib
import io
import json
import sys
import tempfile
import zipfile
from pathlib import Path

import pptx

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from testes.unidade.test_slides_pptx import CONTEUDO, _png  # noqa: E402

ARQUIVO_REFERENCIA = RAIZ / "testes" / "esperados" / "slides-fasoft.json"
LOGOS = (("logo-header-unirv.png", 6), ("logo-unirv.png", 5), ("logo-fasoft.png", 4))


def resumos(dados: bytes) -> dict[str, str]:
    with zipfile.ZipFile(io.BytesIO(dados)) as pacote:
        return {nome: hashlib.sha256(pacote.read(nome)).hexdigest()
                for nome in sorted(pacote.namelist()) if nome != "docProps/core.xml"}


def gerador_fasoft():
    from acad.geracao.slides_pptx import GeradorSlidesPptx
    return GeradorSlidesPptx()


def gerar_referencia() -> bytes:
    with tempfile.TemporaryDirectory() as pasta:
        assets = Path(pasta) / "assets"
        assets.mkdir()
        for nome, largura in LOGOS:
            _png(assets / nome, w=largura)
        return gerador_fasoft().gerar({**CONTEUDO, "ano": 2026}, Path(pasta))


if __name__ == "__main__":
    ARQUIVO_REFERENCIA.write_text(json.dumps(
        {"python_pptx": pptx.__version__, "partes": resumos(gerar_referencia())},
        indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(ARQUIVO_REFERENCIA)
```

- [x] **Step 3: Gravar a referência com o código de `d944cbe`**

Run: `git diff --quiet d944cbe -- acad && .venv/Scripts/python testes/ferramentas/referencia_slides.py`
Expected: imprime o caminho do JSON; o `git diff` não acusa mudança em `acad/` (garante que a referência vem do código original).

- [x] **Step 4: Escrever o teste de compatibilidade**

```python
# testes/unidade/test_compat_fasoft.py
import json

import pptx
import pytest

from testes.ferramentas.referencia_slides import ARQUIVO_REFERENCIA, gerar_referencia, resumos


def test_slides_fasoft_identicos_a_referencia():
    referencia = json.loads(ARQUIVO_REFERENCIA.read_text(encoding="utf-8"))
    if referencia["python_pptx"] != pptx.__version__:
        pytest.fail(f"python-pptx mudou ({referencia['python_pptx']} -> {pptx.__version__}): "
                    "regrave a referência a partir de d944cbe (git worktree), nunca do código novo.")
    assert resumos(gerar_referencia()) == referencia["partes"]
```

- [x] **Step 5: Rodar**

Run: `.venv/Scripts/python -m pytest testes/unidade/test_compat_fasoft.py -v`
Expected: PASS (mesmo código que gerou a referência). Rode duas vezes para confirmar que a geração é determinística.

- [x] **Step 6: Commit**

```bash
git add testes/ferramentas/referencia_slides.py testes/esperados/slides-fasoft.json testes/esperados/perfil-fasoft-v1.yaml testes/unidade/test_compat_fasoft.py
git commit -m "test: referência de compatibilidade dos slides e do perfil fasoft"
```

---

### Task 2: Esquema v2 com `estrutura` e `modelos`, v1 ainda válido

**Files:**
- Modify: `esquemas/perfil.schema.json`
- Create: `acad/perfil/padroes.py`
- Modify: `acad/perfil/perfil.py`
- Modify: `acad/perfil/perfis/fasoft.yaml`
- Test: `testes/unidade/test_perfil.py`, `testes/unidade/test_compat_fasoft.py`

**Interfaces:**
- Produces (campos novos de `Perfil`): `re_semestre: re.Pattern`, `periodos: dict[str, int]` (vazio = `int(texto)`), `re_administracao: re.Pattern`, `papeis: dict[str, str]`, `modelo_slides: str | None`, `modelo_prova: str | None`. Métodos: `pasta(papel: str) -> str`, `semestre_de(pasta: Path) -> tuple[int, int] | None`, `base_semestre(pasta: Path) -> Path`, `partes_disciplina(nome: str) -> dict | None` (chaves `num`, `nome`, `periodo`, ausentes = `None`). Função `perfil_de_documento(documento: dict) -> Perfil`.

- [x] **Step 1: Testes que falham**

Acrescente a `testes/unidade/test_perfil.py`:

```python
from pathlib import Path

from acad import esquemas
from acad.perfil.perfil import perfil_de_documento

V1 = Path(__file__).resolve().parents[1] / "esperados" / "perfil-fasoft-v1.yaml"


def _v1():
    return esquemas.carregar_yaml(V1.read_text(encoding="utf-8"))


def test_perfil_v1_continua_valido():
    assert esquemas.validar("perfil", _v1()) == []


def test_v1_recebe_a_estrutura_que_o_mvp_usava():
    perfil = perfil_de_documento(_v1())
    assert perfil.pasta("planejamento") == "01 - Planejamento"
    assert perfil.pasta("aulas") == "02 - Aulas"
    assert perfil.pasta("arquivo") == "99 - Arquivo"
    assert perfil.re_administracao.match("00 - Administração Acadêmica")
    assert perfil.modelo_slides is None and perfil.modelo_prova is None


def test_fasoft_v2_tem_a_mesma_estrutura_do_v1():
    v1, v2 = perfil_de_documento(_v1()), carregar_perfil("fasoft")
    for campo in ("disciplina_pasta", "subpastas_disciplina", "pasta_arquivo", "pasta_avaliacoes",
                  "pasta_modelos", "etapas_avaliacao", "re_aula", "re_lista", "re_pasta",
                  "sufixos_proibidos", "unidade_carga", "minutos_hora_aula", "exclusao",
                  "re_semestre", "periodos", "re_administracao", "papeis"):
        assert getattr(v1, campo) == getattr(v2, campo), campo
    assert v2.modelo_slides == "Modelo de Slides UniRV"
    assert v2.modelo_prova == "Modelo LaTeX/modelo-prova.tex"


def test_semestre_de_e_base(tmp_path):
    perfil = carregar_perfil("fasoft")
    semestre = tmp_path / "Fasoft" / "2026" / "Segundo Semestre"
    assert perfil.semestre_de(semestre) == (2026, 2)
    assert perfil.base_semestre(semestre) == tmp_path / "Fasoft"
    assert perfil.semestre_de(tmp_path / "2026" / "Terceiro Semestre") is None


def test_partes_disciplina_sem_grupo_vira_none():
    perfil = carregar_perfil("fasoft")
    assert perfil.partes_disciplina("01 - Disc A") == {"num": "01", "nome": "Disc A", "periodo": None}
    assert perfil.partes_disciplina("sem numero") is None


def test_v2_aceita_blocos_novos_e_recusa_chave_desconhecida():
    documento = _v1()
    documento["versao_esquema"] = 2
    documento["perfil"]["estrutura"] = {"semestre": r"^(?P<ano>\d{4})-(?P<periodo>[12])$"}
    assert esquemas.validar("perfil", documento) == []
    documento["perfil"]["estrutura"]["outra"] = 1
    assert esquemas.validar("perfil", documento)
```

- [x] **Step 2: Rodar e ver falhar**

Run: `.venv/Scripts/python -m pytest testes/unidade/test_perfil.py -v`
Expected: FAIL (`ImportError: perfil_de_documento`).

- [x] **Step 3: Esquema**

Em `esquemas/perfil.schema.json`: troque `"versao_esquema": {"const": 1}` por `"versao_esquema": {"enum": [1, 2]}`; tire `"semestre_pasta"` da lista `required` de `perfil`; acrescente em `perfil.properties`:

```json
"estrutura": {
  "type": "object", "additionalProperties": false,
  "properties": {
    "semestre": {"type": "string"},
    "periodos": {"type": "object", "additionalProperties": {"enum": [1, 2]}},
    "administracao": {"type": "string"},
    "papeis": {
      "type": "object", "additionalProperties": false,
      "properties": {
        "planejamento": {"type": "string"}, "aulas": {"type": "string"},
        "atividades": {"type": "string"}, "projetos": {"type": "string"},
        "referencias": {"type": "string"}, "codigo": {"type": "string"},
        "arquivo": {"type": "string"}
      }
    }
  }
},
"modelos": {
  "type": "object", "additionalProperties": false,
  "properties": {"slides": {"type": ["string", "null"]}, "prova": {"type": ["string", "null"]}}
}
```

- [x] **Step 4: Padrões v1**

```python
# acad/perfil/padroes.py
"""Valores que o MVP usava fixos no código; valem para perfis sem o bloco `estrutura`."""

ESTRUTURA_V1 = {
    "semestre": r"^(?P<ano>\d{4})/(?P<periodo>Primeiro|Segundo) Semestre$",
    "periodos": {"Primeiro": 1, "Segundo": 2},
    "administracao": r"^00 - ",
    "papeis": {
        "planejamento": "01 - Planejamento",
        "aulas": "02 - Aulas",
        "atividades": "03 - Atividades e Listas",
        "projetos": "04 - Projetos e Entregáveis",
        "referencias": "05 - Materiais de Referência",
        "codigo": "06 - Código e Exemplos",
        "arquivo": "99 - Arquivo",
    },
}
```

- [x] **Step 5: `Perfil` ampliado**

Em `acad/perfil/perfil.py`: acrescente os campos ao dataclass (depois de `exclusao`), separe a montagem em `perfil_de_documento` e mantenha `carregar_perfil` lendo o empacotado (a leitura do usuário vem na Tarefa 3). Nesta tarefa `carregar_perfil` ainda tem `id: str = "fasoft"`; o padrão sai na Tarefa 5.

```python
from pathlib import Path
from acad.perfil.padroes import ESTRUTURA_V1

    # campos novos do dataclass Perfil
    re_semestre: re.Pattern
    periodos: dict
    re_administracao: re.Pattern
    papeis: dict
    modelo_slides: str | None
    modelo_prova: str | None

    def pasta(self, papel: str) -> str:
        return self.papeis[papel]

    def semestre_de(self, pasta: Path) -> tuple[int, int] | None:
        pasta = Path(pasta)
        alvo = f"{pasta.parent.name}/{pasta.name}" if "/" in self.re_semestre.pattern else pasta.name
        correspondencia = self.re_semestre.match(alvo)
        if not correspondencia:
            return None
        texto = correspondencia["periodo"]
        periodo = self.periodos.get(texto) if self.periodos else int(texto)
        return (int(correspondencia["ano"]), periodo) if periodo in (1, 2) else None

    def base_semestre(self, pasta: Path) -> Path:
        pasta = Path(pasta)
        return pasta.parent.parent if "/" in self.re_semestre.pattern else pasta.parent

    def partes_disciplina(self, nome: str) -> dict | None:
        correspondencia = self.disciplina_pasta.match(nome)
        if not correspondencia:
            return None
        grupos = correspondencia.groupdict()
        return {chave: grupos.get(chave) for chave in ("num", "nome", "periodo")}


def perfil_de_documento(documento: dict) -> Perfil:
    perfil = documento["perfil"]
    nomes = perfil["nomenclatura"]
    estrutura = {**ESTRUTURA_V1, **perfil.get("estrutura", {})}
    papeis = {**ESTRUTURA_V1["papeis"], "arquivo": perfil["pasta_arquivo"],
              **perfil.get("estrutura", {}).get("papeis", {})}
    modelos = perfil.get("modelos", {})
    return Perfil(
        # ... os mesmos argumentos que carregar_perfil passa hoje ...
        re_semestre=re.compile(estrutura["semestre"]),
        periodos=dict(perfil.get("estrutura", {}).get("periodos",
                      ESTRUTURA_V1["periodos"] if "estrutura" not in perfil else {})),
        re_administracao=re.compile(estrutura["administracao"]),
        papeis=papeis,
        modelo_slides=modelos.get("slides"),
        modelo_prova=modelos.get("prova"),
    )


def carregar_perfil(id: str = "fasoft") -> Perfil:
    texto = (resources.files("acad.perfil") / "perfis" / f"{id}.yaml").read_text(encoding="utf-8")
    documento = esquemas.carregar_yaml(texto)
    esquemas.validar_ou_falhar("perfil", documento)
    return perfil_de_documento(documento)
```

Regra de `periodos`: perfil sem `estrutura` → mapa v1 (`Primeiro/Segundo`); perfil com `estrutura` e sem `periodos` → mapa vazio (período numérico). `pasta_arquivo` continua obrigatório no v1 só pelo uso atual; use `perfil.get("pasta_arquivo", papeis["arquivo"])` se o campo faltar. Preencha o `# ...` com os argumentos exatos que `carregar_perfil` monta hoje (`id`, `instituicao`, `disciplina_pasta`, …, `exclusao`) — copie-os, não os resuma.

- [x] **Step 6: `fasoft.yaml` v2**

Mude `versao_esquema: 1` para `versao_esquema: 2` e acrescente ao fim de `perfil:` os blocos `estrutura` (exatamente os valores de `ESTRUTURA_V1`, com `periodos: {Primeiro: 1, Segundo: 2}`) e `modelos: {slides: "Modelo de Slides UniRV", prova: "Modelo LaTeX/modelo-prova.tex"}`. Mantenha os demais campos, inclusive `semestre_pasta` e o comentário D3.

- [x] **Step 7: Rodar**

Run: `.venv/Scripts/python -m pytest testes/unidade/test_perfil.py testes/unidade/test_esquemas.py testes/unidade/test_compat_fasoft.py -v` e depois `.venv/Scripts/python -m pytest -q`
Expected: tudo PASS; suíte inteira com a linha de base + os novos testes.

- [x] **Step 8: Commit**

```bash
git add esquemas/perfil.schema.json acad/perfil/padroes.py acad/perfil/perfil.py acad/perfil/perfis/fasoft.yaml testes/unidade/test_perfil.py
git commit -m "feat: perfil v2 com estrutura e modelos, v1 continua válido"
```

---

### Task 3: Perfil do usuário e mensagens em português simples

**Files:**
- Create: `acad/perfil/validar.py`
- Modify: `acad/perfil/perfil.py`
- Test: `testes/unidade/test_perfil_usuario.py` (novo)

**Interfaces:**
- Consumes: `perfil_de_documento` (Tarefa 2).
- Produces: `problemas_do_perfil(documento: dict) -> list[str]`; `validar_perfil_ou_falhar(documento: dict) -> None` (levanta `ErroAcad("perfil-invalido", …, saida=1)`); `pasta_perfis_usuario() -> Path` (`dir_dados() / "perfis"`); `ler_documento_perfil(id: str) -> dict`; `perfis_disponiveis() -> dict[str, str]` (id → `"usuario"` ou `"pacote"`); `ID_PERFIL: re.Pattern`.

- [x] **Step 1: Testes que falham**

```python
# testes/unidade/test_perfil_usuario.py
import pytest

from acad import esquemas
from acad.erros import ErroAcad
from acad.mensagens import contem_termo_tecnico
from acad.perfil.perfil import carregar_perfil, pasta_perfis_usuario, perfis_disponiveis
from acad.perfil.validar import problemas_do_perfil
from testes.unidade.test_perfil import _v1


def _gravar(id, documento):
    pasta = pasta_perfis_usuario()
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / f"{id}.yaml").write_text(esquemas.para_yaml(documento), encoding="utf-8")


def test_perfil_do_usuario_vence_o_empacotado():
    documento = _v1()
    documento["perfil"]["instituicao"] = "Minha cópia"
    _gravar("fasoft", documento)
    assert carregar_perfil("fasoft").instituicao == "Minha cópia"
    assert perfis_disponiveis()["fasoft"] == "usuario"


def test_perfil_novo_do_usuario():
    documento = _v1()
    documento["perfil"]["id"] = "faculdade-x"
    _gravar("faculdade-x", documento)
    assert carregar_perfil("faculdade-x").id == "faculdade-x"


@pytest.mark.parametrize("id", ["../fora", "Fasoft", "a/b", "", "x" * 41])
def test_id_invalido(id):
    with pytest.raises(ErroAcad) as erro:
        carregar_perfil(id)
    assert erro.value.codigo == "perfil-invalido"


def test_perfil_inexistente_pede_decisao():
    with pytest.raises(ErroAcad) as erro:
        carregar_perfil("nao-existe")
    assert erro.value.codigo == "perfil-nao-encontrado" and erro.value.saida == 4
    assert "criar" in erro.value.mensagem


def test_mensagens_simples():
    documento = _v1()
    del documento["perfil"]["instituicao"]
    documento["perfil"]["disciplina_pasta"] = "(sem fechar"
    documento["perfil"]["extra"] = 1
    problemas = problemas_do_perfil(documento)
    assert "Falta o nome da instituição." in problemas
    assert "O perfil tem uma informação que não conheço: “extra”." in problemas
    assert all(not contem_termo_tecnico(texto) for texto in problemas)


def test_regra_que_nao_compila():
    documento = _v1()
    documento["perfil"]["disciplina_pasta"] = "(sem fechar"
    assert problemas_do_perfil(documento) == ["A regra que reconhece as pastas das disciplinas não funciona."]


def test_perfil_quebrado_no_usuario_da_erro_simples():
    documento = _v1()
    del documento["perfil"]["instituicao"]
    _gravar("quebrado", documento)
    with pytest.raises(ErroAcad) as erro:
        carregar_perfil("quebrado")
    assert erro.value.codigo == "perfil-invalido"
    assert erro.value.mensagem == "O perfil da instituição tem problemas: Falta o nome da instituição."
```

`testes/conftest.py` já isola `ACAD_DADOS` por teste (fixture `dados_isolados`), então `pasta_perfis_usuario()` cai em `tmp_path`.

- [x] **Step 2: Rodar e ver falhar**

Run: `.venv/Scripts/python -m pytest testes/unidade/test_perfil_usuario.py -v`
Expected: FAIL (`ImportError`).

- [x] **Step 3: `acad/perfil/validar.py`**

```python
"""Problemas do perfil em português simples (o esquema dá o técnico; aqui vira frase)."""
from __future__ import annotations

import re

from jsonschema import Draft202012Validator

from acad import esquemas
from acad.erros import ErroAcad

NOMES = {
    "versao_esquema": "a versão do perfil", "perfil": "o perfil", "id": "o identificador do perfil",
    "instituicao": "o nome da instituição", "disciplina_pasta": "a regra que reconhece as pastas das disciplinas",
    "subpastas_disciplina": "a lista de pastas de cada disciplina", "pasta_arquivo": "a pasta de arquivo morto",
    "pasta_avaliacoes": "a regra da pasta de avaliações", "pasta_modelos": "a regra da pasta de modelos",
    "etapas_avaliacao": "as etapas de avaliação", "nomenclatura": "as regras de nomes",
    "aula": "a regra do nome das aulas", "lista": "a regra do nome das listas",
    "pasta": "a regra do nome das pastas", "sufixos_proibidos": "os finais de nome proibidos",
    "carga_horaria": "a carga horária", "unidade": "a unidade da carga horária",
    "minutos_hora_aula": "os minutos da hora-aula", "exclusao": "a lista de pastas protegidas",
    "estrutura": "a estrutura de pastas", "semestre": "a regra que reconhece a pasta do semestre",
    "periodos": "os nomes dos períodos", "administracao": "a regra da pasta de administração",
    "papeis": "os nomes das pastas da disciplina", "modelos": "os modelos da instituição",
    "slides": "o padrão visual dos slides",
}
REGRAS = [("disciplina_pasta",), ("pasta_avaliacoes",), ("pasta_modelos",),
          ("nomenclatura", "aula"), ("nomenclatura", "lista"), ("nomenclatura", "pasta"),
          ("estrutura", "semestre"), ("estrutura", "administracao")]
GRUPOS = {("estrutura", "semestre"): ("ano", "periodo"), ("disciplina_pasta",): ("nome",)}


def _nome(campo: str) -> str:
    return NOMES.get(campo, f"“{campo}”")


def _frase_do_esquema(erro) -> str:
    campos = [parte for parte in erro.absolute_path if isinstance(parte, str)]
    ultimo = campos[-1] if campos else "perfil"
    if erro.validator == "required":
        falta = re.findall(r"'([^']+)'", erro.message)[0]
        return f"Falta {_nome(falta)}."
    if erro.validator == "additionalProperties":
        extras = re.findall(r"'([^']+)'", erro.message)
        return f"O perfil tem uma informação que não conheço: “{extras[0]}”."
    if erro.validator == "pattern" and "paleta" in campos:
        return f"A cor “{erro.instance}” não é válida; use seis letras ou números, como 1F3A5F."
    if ultimo == "versao_esquema":
        return "A versão do perfil não é conhecida."
    texto = _nome(ultimo)
    return f"{texto[0].upper()}{texto[1:]} não está no formato esperado."


def problemas_do_perfil(documento: dict) -> list[str]:
    validador = Draft202012Validator(esquemas.carregar_esquema("perfil"))
    erros = sorted(validador.iter_errors(documento), key=lambda erro: [str(p) for p in erro.absolute_path])
    problemas = list(dict.fromkeys(_frase_do_esquema(erro) for erro in erros))
    perfil = documento.get("perfil") if isinstance(documento, dict) else None
    if not isinstance(perfil, dict):
        return problemas or ["O perfil está vazio."]
    for caminho in REGRAS:
        valor = perfil
        for parte in caminho:
            valor = valor.get(parte) if isinstance(valor, dict) else None
        if not isinstance(valor, str):
            continue
        texto = _nome(caminho[-1])
        try:
            regra = re.compile(valor)
        except re.error:
            problemas.append(f"{texto[0].upper()}{texto[1:]} não funciona.")
            continue
        faltando = [grupo for grupo in GRUPOS.get(caminho, ()) if grupo not in regra.groupindex]
        if faltando:
            problemas.append(f"{texto[0].upper()}{texto[1:]} precisa separar {' e '.join(faltando)}.")
    return problemas


def validar_perfil_ou_falhar(documento: dict) -> None:
    problemas = problemas_do_perfil(documento)
    if problemas:
        raise ErroAcad("perfil-invalido",
                       f"O perfil da instituição tem problemas: {' '.join(problemas[:3])}",
                       "; ".join(esquemas.validar("perfil", documento)) or "; ".join(problemas), saida=1)
```

Atenção: a mensagem do teste é `"O perfil da instituição tem problemas: Falta o nome da instituição."` — os itens já terminam em ponto e são unidos por espaço. O código precisa rodar em Python 3.11: não aninhe aspas iguais dentro de f-strings.

- [x] **Step 4: Leitura usuário → pacote em `acad/perfil/perfil.py`**

```python
from acad.config import dir_dados
from acad.erros import ErroAcad
from acad.perfil.validar import validar_perfil_ou_falhar

ID_PERFIL = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")


def pasta_perfis_usuario() -> Path:
    return dir_dados() / "perfis"


def _empacotados():
    return resources.files("acad.perfil") / "perfis"


def perfis_disponiveis() -> dict[str, str]:
    disponiveis = {item.name[:-5]: "pacote" for item in _empacotados().iterdir() if item.name.endswith(".yaml")}
    pasta = pasta_perfis_usuario()
    if pasta.is_dir():
        disponiveis.update({item.stem: "usuario" for item in pasta.glob("*.yaml") if ID_PERFIL.match(item.stem)})
    return dict(sorted(disponiveis.items()))


def ler_documento_perfil(id: str) -> dict:
    if not isinstance(id, str) or not ID_PERFIL.match(id):
        raise ErroAcad("perfil-invalido", "O nome do perfil só pode ter letras minúsculas, números e traços.",
                       repr(id), saida=1)
    usuario = pasta_perfis_usuario() / f"{id}.yaml"
    pacote = _empacotados() / f"{id}.yaml"
    if usuario.is_file():
        texto = usuario.read_text(encoding="utf-8")
    elif pacote.is_file():
        texto = pacote.read_text(encoding="utf-8")
    else:
        raise ErroAcad("perfil-nao-encontrado",
                       f"Não encontrei o perfil “{id}”. Quer criar um a partir da sua pasta?", id, saida=4)
    return esquemas.carregar_yaml(texto)


def carregar_perfil(id: str = "fasoft") -> Perfil:
    documento = ler_documento_perfil(id)
    validar_perfil_ou_falhar(documento)
    return perfil_de_documento(documento)
```

Confira se `acad.config` não importa `acad.perfil` (evita ciclo); hoje não importa.

- [x] **Step 5: Rodar**

Run: `.venv/Scripts/python -m pytest testes/unidade/test_perfil_usuario.py testes/unidade/test_perfil.py -v` e `.venv/Scripts/python -m pytest -q`
Expected: PASS; suíte verde.

- [x] **Step 6: Commit**

```bash
git add acad/perfil/validar.py acad/perfil/perfil.py testes/unidade/test_perfil_usuario.py
git commit -m "feat: perfis do usuário com prioridade e erros em português simples"
```

---

### Task 4: Identidade visual dos slides como dado do perfil

**Files:**
- Create: `acad/geracao/identidade.py`
- Modify: `acad/geracao/slides_pptx.py` (constantes 42-70, `_estilo`, `_estilizar`, `_capa` 201-223, `_moldura`, componentes, `_logo`, `_bordas`, `_linhas_de_codigo`, `avisos_editoriais`)
- Modify: `acad/geracao/slides.py` (`obter_gerador`)
- Modify: `esquemas/perfil.schema.json` (bloco `slides`), `acad/perfil/perfil.py` (campo `slides`), `acad/perfil/perfis/fasoft.yaml` (identidade UniRV)
- Modify: `testes/ferramentas/referencia_slides.py` (só `gerador_fasoft`)
- Modify: `testes/unidade/test_slides_pptx.py` (helper `_pres` e o teste de leitor injetado usam identidade fasoft)
- Test: `testes/unidade/test_identidade.py` (novo), `testes/unidade/test_compat_fasoft.py`

**Interfaces:**
- Consumes: `carregar_perfil`, `perfil_de_documento`.
- Produces: `IdentidadeSlides(largura_emu: int, altura_emu: int, fonte: str, fonte_codigo: str, paleta: dict[str, str], capa_linhas: tuple[str, ...], capa_local: str, logo_cabecalho: str | None, logos_capa: tuple[str, ...], limites: dict[str, int])`; `IDENTIDADE_NEUTRA`; `identidade_de(bloco: dict | None) -> IdentidadeSlides`; `paleta_de_cor(cor: str) -> dict[str, str]`; `mistura(a: str, b: str, t: float) -> str`; `Perfil.slides: IdentidadeSlides`; `GeradorSlidesPptx(ler_bytes=None, identidade=IDENTIDADE_NEUTRA)`; `avisos_editoriais(slides, limites=None)`; `obter_gerador(ler_bytes=None, identidade=None)`.

- [x] **Step 1: Testes que falham**

```python
# testes/unidade/test_identidade.py
import io

from pptx import Presentation

from acad.geracao.identidade import IDENTIDADE_NEUTRA, identidade_de, mistura, paleta_de_cor
from acad.geracao.slides_pptx import GeradorSlidesPptx, avisos_editoriais
from acad.perfil.perfil import carregar_perfil
from testes.unidade.test_slides_pptx import CONTEUDO, _png


def _textos(dados):
    p = Presentation(io.BytesIO(dados))
    return " ".join(s.text_frame.text for slide in p.slides for s in slide.shapes if s.has_text_frame)


def test_fasoft_traz_a_identidade_unirv():
    ident = carregar_perfil("fasoft").slides
    assert ident.paleta["principal"] == "015537" and ident.paleta["codigo_fundo"] == "10231B"
    assert ident.capa_linhas == ("UNIVERSIDADE DE RIO VERDE (UniRV)", "Bacharelado em Engenharia de Software")
    assert ident.capa_local == "RIO VERDE — {ano}"
    assert ident.logo_cabecalho == "logo-header-unirv.png"
    assert ident.logos_capa == ("logo-unirv.png", "logo-fasoft.png")


def test_neutra_nao_tem_marca(tmp_path):
    (tmp_path / "assets").mkdir()
    for nome in ("logo-header-unirv.png", "logo-unirv.png", "logo-fasoft.png"):
        _png(tmp_path / "assets" / nome)
    dados = GeradorSlidesPptx().gerar({**CONTEUDO, "ano": 2027}, tmp_path)
    texto = _textos(dados)
    assert "UniRV" not in texto and "RIO VERDE" not in texto and "Engenharia de Software" not in texto
    assert "2027" in texto
    p = Presentation(io.BytesIO(dados))
    assert not [s for slide in p.slides for s in slide.shapes if s.shape_type == 13]
    assert b"015537" not in b"".join(part.blob for part in p.part.package.iter_parts())


def test_bloco_parcial_completa_com_neutra():
    ident = identidade_de({"paleta": {"principal": "AA0000"}, "capa": {"linhas": ["Faculdade X"]}})
    assert ident.paleta["principal"] == "AA0000"
    assert ident.paleta["corpo"] == IDENTIDADE_NEUTRA.paleta["corpo"]
    assert ident.capa_linhas == ("Faculdade X",) and ident.capa_local == "{ano}"


def test_paleta_de_cor():
    assert mistura("000000", "FFFFFF", 0.5) == "808080"
    paleta = paleta_de_cor("1F3A5F")
    assert paleta["principal"] == "1F3A5F"
    assert paleta["claro"] == mistura("1F3A5F", "FFFFFF", 0.88)
    assert paleta["codigo_fundo"] == IDENTIDADE_NEUTRA.paleta["codigo_fundo"]


def test_limites_do_perfil_nos_avisos():
    slides = [{"tipo": "topicos", "titulo": "T", "lead": "l", "itens": ["a", "b", "c"]}]
    assert avisos_editoriais(slides) == []
    assert "mais de 2 itens" in avisos_editoriais(slides, {"topicos": 2, "linhas_codigo": 16, "linhas_tabela": 8})[0]
```

E em `test_compat_fasoft.py` nada muda: ele chama `gerador_fasoft()`, que você trocará no Step 6.

- [x] **Step 2: Rodar e ver falhar**

Run: `.venv/Scripts/python -m pytest testes/unidade/test_identidade.py -v`
Expected: FAIL (`ModuleNotFoundError: acad.geracao.identidade`).

- [x] **Step 3: `acad/geracao/identidade.py`**

```python
"""Identidade visual dos slides (cores, fontes, textos e logos); vem do perfil da instituição."""
from __future__ import annotations

from dataclasses import dataclass, field

PALETA_NEUTRA = {
    "principal": "2F3E4E", "secundaria": "4A6076", "claro": "E8ECF0", "claro2": "F4F6F8",
    "tinta": "1E2328", "corpo": "2E3338", "apagado": "6B737B", "linha": "CDD3D9", "fundo": "FFFFFF",
    "subtitulo_capa": "DCE2E8", "codigo_fundo": "1E252C", "codigo_comentario": "9AA8B5", "codigo_texto": "E1E6EB",
}
LIMITES_PADRAO = {"topicos": 6, "linhas_codigo": 16, "linhas_tabela": 8}


@dataclass(frozen=True)
class IdentidadeSlides:
    largura_emu: int = 9144000
    altura_emu: int = 5143500
    fonte: str = "Calibri"
    fonte_codigo: str = "Courier New"
    paleta: dict = field(default_factory=lambda: dict(PALETA_NEUTRA))
    capa_linhas: tuple[str, ...] = ()
    capa_local: str = "{ano}"
    logo_cabecalho: str | None = None
    logos_capa: tuple[str, ...] = ()
    limites: dict = field(default_factory=lambda: dict(LIMITES_PADRAO))


IDENTIDADE_NEUTRA = IdentidadeSlides()


def identidade_de(bloco: dict | None) -> IdentidadeSlides:
    if not bloco:
        return IDENTIDADE_NEUTRA
    base = IDENTIDADE_NEUTRA
    tamanho, fontes = bloco.get("tamanho", {}), bloco.get("fontes", {})
    capa, logos = bloco.get("capa", {}), bloco.get("logos", {})
    return IdentidadeSlides(
        largura_emu=tamanho.get("largura_emu", base.largura_emu),
        altura_emu=tamanho.get("altura_emu", base.altura_emu),
        fonte=fontes.get("texto", base.fonte),
        fonte_codigo=fontes.get("codigo", base.fonte_codigo),
        paleta={**base.paleta, **{chave: valor.upper() for chave, valor in bloco.get("paleta", {}).items()}},
        capa_linhas=tuple(capa.get("linhas", base.capa_linhas)),
        capa_local=capa.get("local", base.capa_local),
        logo_cabecalho=logos.get("cabecalho", base.logo_cabecalho),
        logos_capa=tuple(logos.get("capa", base.logos_capa)),
        limites={**base.limites, **bloco.get("limites", {})},
    )


def mistura(a: str, b: str, t: float) -> str:
    canais = []
    for i in (0, 2, 4):
        x, y = int(a[i:i + 2], 16), int(b[i:i + 2], 16)
        canais.append(f"{round(x + (y - x) * t):02X}")
    return "".join(canais)


def paleta_de_cor(cor: str) -> dict[str, str]:
    cor = cor.upper()
    return {**PALETA_NEUTRA, "principal": cor,
            "secundaria": mistura(cor, "FFFFFF", 0.25), "claro": mistura(cor, "FFFFFF", 0.88),
            "claro2": mistura(cor, "FFFFFF", 0.94), "linha": mistura(cor, "FFFFFF", 0.75),
            "subtitulo_capa": mistura(cor, "FFFFFF", 0.82)}
```

`round` do Python arredonda 0,5 para par: `mistura("000000","FFFFFF",0.5)` = `round(127.5)` = 128 = `80`. O teste confirma.

- [x] **Step 4: Esquema e perfil**

Em `esquemas/perfil.schema.json`, `perfil.properties` ganha:

```json
"slides": {
  "type": "object", "additionalProperties": false,
  "properties": {
    "tamanho": {"type": "object", "additionalProperties": false,
                "properties": {"largura_emu": {"type": "integer", "minimum": 1}, "altura_emu": {"type": "integer", "minimum": 1}}},
    "fontes": {"type": "object", "additionalProperties": false,
               "properties": {"texto": {"type": "string"}, "codigo": {"type": "string"}}},
    "paleta": {"type": "object", "additionalProperties": false,
               "properties": {
                 "principal": {"$ref": "#/$defs/cor"}, "secundaria": {"$ref": "#/$defs/cor"},
                 "claro": {"$ref": "#/$defs/cor"}, "claro2": {"$ref": "#/$defs/cor"},
                 "tinta": {"$ref": "#/$defs/cor"}, "corpo": {"$ref": "#/$defs/cor"},
                 "apagado": {"$ref": "#/$defs/cor"}, "linha": {"$ref": "#/$defs/cor"},
                 "fundo": {"$ref": "#/$defs/cor"}, "subtitulo_capa": {"$ref": "#/$defs/cor"},
                 "codigo_fundo": {"$ref": "#/$defs/cor"}, "codigo_comentario": {"$ref": "#/$defs/cor"},
                 "codigo_texto": {"$ref": "#/$defs/cor"}}},
    "capa": {"type": "object", "additionalProperties": false,
             "properties": {"linhas": {"type": "array", "maxItems": 2, "items": {"type": "string"}},
                            "local": {"type": "string"}}},
    "logos": {"type": "object", "additionalProperties": false,
              "properties": {"cabecalho": {"type": ["string", "null"]},
                             "capa": {"type": "array", "maxItems": 2, "items": {"type": "string"}}}},
    "limites": {"type": "object", "additionalProperties": false,
                "properties": {"topicos": {"type": "integer", "minimum": 1},
                               "linhas_codigo": {"type": "integer", "minimum": 1},
                               "linhas_tabela": {"type": "integer", "minimum": 1}}}
  }
}
```

e, na raiz do esquema, `"$defs": {"cor": {"type": "string", "pattern": "^[0-9A-Fa-f]{6}$"}}`.

Em `Perfil`: campo `slides: IdentidadeSlides` e, em `perfil_de_documento`, `slides=identidade_de(perfil.get("slides"))`.

Em `fasoft.yaml`, acrescente o bloco `slides:` da spec P3 com os valores exatos (paleta das 13 cores de `slides_pptx.py:43-55`, `capa.local: "RIO VERDE — {ano}"` com o travessão `—` de `slides_pptx.py:221`, logos e limites 6/16/8, tamanho 9144000 × 5143500, fontes Calibri/Courier New).

- [x] **Step 5: Refatorar `slides_pptx.py`**

Regra: **nenhuma mudança de geometria nem de ordem de criação de formas** (a referência compara bytes). Passos mecânicos:

1. Apague as constantes de paleta, `FONTE`, `FONTE_CODIGO`, `LARGURA`, `ALTURA`, `LOGOS`, `MAX_*`; importe `from acad.geracao.identidade import IDENTIDADE_NEUTRA, LIMITES_PADRAO, IdentidadeSlides`.
2. `GeradorSlidesPptx.__init__(self, ler_bytes=None, identidade: IdentidadeSlides = IDENTIDADE_NEUTRA)` guarda `self._id = identidade` e `self._p = identidade.paleta`.
3. Os helpers de módulo `_estilo`, `_estilizar`, `_texto` recebem a fonte por parâmetro sem valor padrão de marca: `_estilo(tamanho, cor, negrito=False, italico=False, fonte="Calibri")` continua, mas **todas** as chamadas dentro da classe passam `fonte=self._id.fonte` — crie `def _e(self, tamanho, cor, negrito=False, italico=False, codigo=False)` que devolve `_estilo(tamanho, cor, negrito, italico, self._id.fonte_codigo if codigo else self._id.fonte)` e troque cada `_estilo(...)` da classe por `self._e(...)`. O valor padrão `cor=CORPO` de `_estilo` some: passe `self._p["corpo"]` explicitamente onde a chamada omitia a cor (`_texto` em `_cards`, `_fluxo`, `_nota`).
4. Os `@staticmethod` (`_lead`, `_nota`, `_topicos`, `_codigo`, `_tabela`) viram métodos de instância para ler `self._p`. Mapa de troca: `VERDE→self._p["principal"]`, `VERDE2→"secundaria"`, `VERDE_CLARO→"claro"`, `VERDE_CLARO2→"claro2"`, `TINTA→"tinta"`, `CORPO→"corpo"`, `APAGADO→"apagado"`, `LINHA→"linha"`, `BRANCO→"fundo"`, `SUBTITULO_CAPA→"subtitulo_capa"`, `CODIGO_FUNDO→"codigo_fundo"`, `CODIGO_COMENTARIO→"codigo_comentario"`, `CODIGO_TEXTO→"codigo_texto"`. Atenção: `BRANCO` também é usado como cor de **texto** sobre a barra (título, cabeçalho da tabela, selo dos cards, curso na capa); use `"fundo"` nesses casos também — no fasoft e no neutro ambos são `FFFFFF`.
5. `gerar`: `Emu(self._id.largura_emu)`, `Emu(self._id.altura_emu)`.
6. `_logo(self, slide, arquivo: str | None, x, y, w, h)`: recebe o nome do arquivo; `if self._template is None or not arquivo: return`; lê `self._template / "assets" / arquivo`.
7. `_capa`: troque as duas chamadas de logo por
   ```python
   posicoes = [(4.02, 3.16, 0.72, 0.72), (4.96, 3.29, 0.87, 0.58)]
   for arquivo, (x, y, w, h) in zip(self._id.logos_capa, posicoes):
       self._logo(s, arquivo, x, y, w, h)
   for linha, y in zip(self._id.capa_linhas, (4.02, 4.26)):
       _texto(s, 0.7, y, 8.6, 0.26, [[(linha, self._e(11.5, self._p["corpo"]))]], PP_ALIGN.CENTER)
   if self._id.capa_local:
       _texto(s, 0.7, 4.62, 8.6, 0.28, [[(self._id.capa_local.format(ano=ano), self._e(11, self._p["principal"], True))]],
              PP_ALIGN.CENTER)
   ```
   mantendo a ordem original: retângulo, curso, rótulo, professor, período, logos, linhas, local, filete.
8. `_moldura`: `self._logo(s, self._id.logo_cabecalho, 7.65, 0.28, 1.91, 0.63)`.
9. `_bordas(celula, cor_linha)` e `_linhas_de_codigo(item, cor_comentario)` recebem a cor por parâmetro.
10. `avisos_editoriais(slides, limites=None)`: `limites = limites or LIMITES_PADRAO`; troque `MAX_TOPICOS`/`MAX_LINHAS_CODIGO`/`MAX_LINHAS_TABELA` por `limites["topicos"]`, `limites["linhas_codigo"]`, `limites["linhas_tabela"]`; a contagem de linhas de código usa `_linhas_de_codigo(item, "")` (cor irrelevante).
11. Atualize a docstring do módulo: o padrão visual vem do perfil; os números de geometria ficam.

`acad/geracao/slides.py`: `obter_gerador(ler_bytes=None, identidade=None)` → `GeradorSlidesPptx(ler_bytes, identidade or IDENTIDADE_NEUTRA)`; docstring sem "UniRV".

- [x] **Step 6: Ferramenta e testes antigos usam a identidade fasoft**

Em `testes/ferramentas/referencia_slides.py`:

```python
def gerador_fasoft():
    from acad.geracao.slides_pptx import GeradorSlidesPptx
    from acad.perfil.perfil import carregar_perfil
    return GeradorSlidesPptx(identidade=carregar_perfil("fasoft").slides)
```

Em `testes/unidade/test_slides_pptx.py`: `FASOFT = carregar_perfil("fasoft").slides`; `_pres` usa `GeradorSlidesPptx(identidade=FASOFT)`; `test_leitor_injetado_e_usado` usa `GeradorSlidesPptx(ler, FASOFT)`. Nenhuma asserção muda.

- [x] **Step 7: Rodar**

Run: `.venv/Scripts/python -m pytest testes/unidade/test_compat_fasoft.py testes/unidade/test_identidade.py testes/unidade/test_slides_pptx.py -v` e `.venv/Scripts/python -m pytest -q`
Expected: tudo PASS. Se `test_slides_fasoft_identicos_a_referencia` falhar, compare as partes divergentes (`resumos` dos dois lados) e corrija a ordem de criação/cor — **nunca** regrave a referência.

- [x] **Step 8: Commit**

```bash
git add acad/geracao/identidade.py acad/geracao/slides_pptx.py acad/geracao/slides.py esquemas/perfil.schema.json acad/perfil/perfil.py acad/perfil/perfis/fasoft.yaml testes/ferramentas/referencia_slides.py testes/unidade/test_slides_pptx.py testes/unidade/test_identidade.py
git commit -m "feat: padrão visual dos slides vem do perfil, com identidade neutra"
```

---

### Task 5: Perfil neutro e fim do padrão silencioso `fasoft`

**Files:**
- Create: `acad/perfil/perfis/neutro.yaml`
- Modify: `acad/perfil/perfil.py:carregar_perfil` (sem valor padrão)
- Modify: `acad/contexto.py:48-50`
- Modify: `acad/comandos/perfil.py:33-55` (`iniciar`) e `:68-72` (`disciplina criar`)
- Modify: `testes/conftest.py` (fixture `perfil_fasoft`; `semestre_sintetico` depende dela)
- Modify: chamadas `carregar_perfil()` sem argumento em `testes/unidade/{test_escrita,test_estrutura,test_nomenclatura,test_perfil,test_privacidade,test_consulta}.py`, `testes/integracao/test_paridade_cronograma.py`, `testes/ferramentas/espelhar-amostras.py` → `carregar_perfil("fasoft")`
- Test: `testes/unidade/test_perfil_padrao.py` (novo)

**Interfaces:**
- Consumes: Tarefas 2–4.
- Produces: `contexto.PERFIL_PADRAO = "neutro"`; `carregar_perfil(id: str)` obrigatório; fixture `perfil_fasoft`.

- [ ] **Step 1: Testes que falham**

```python
# testes/unidade/test_perfil_padrao.py
import json

from acad import contexto
from acad.cli import main
from acad.config import dir_dados
from acad.perfil.perfil import carregar_perfil


def test_sem_configuracao_usa_neutro():
    assert contexto.perfil().id == "neutro"


def test_neutro_sem_marca_e_com_pastas_minusculas():
    neutro = carregar_perfil("neutro")
    assert neutro.slides.capa_linhas == () and neutro.slides.logos_capa == ()
    assert neutro.pasta("planejamento") == "planejamento" and neutro.pasta("arquivo") == "arquivo"
    assert neutro.semestre_de(dir_dados() / "2027-1") == (2027, 1)
    assert neutro.unidade_carga is None
    assert "*/projetos" in neutro.exclusao and "*Notas*" in neutro.exclusao


def test_iniciar_sem_perfil_nao_grava_fasoft(tmp_path, capsys):
    semestre = tmp_path / "2027-1"
    semestre.mkdir()
    assert main(["iniciar", "2027-1", "--raiz", str(semestre), "--confirmar", "--json"]) == 0
    saida = json.loads(capsys.readouterr().out)
    assert saida["dados"]["perfil"] == "neutro"
    assert any("perfil neutro" in aviso for aviso in saida["avisos"])
    assert contexto.carregar_configuracao()["perfil"] == "neutro"


def test_iniciar_sem_perfil_mantem_o_da_configuracao(tmp_path, capsys):
    semestre = tmp_path / "2027-1"
    semestre.mkdir()
    main(["iniciar", "2027-1", "--raiz", str(semestre), "--perfil", "fasoft", "--confirmar", "--json"])
    main(["iniciar", "2027-1", "--raiz", str(semestre), "--confirmar", "--json"])
    capsys.readouterr()
    assert contexto.carregar_configuracao()["perfil"] == "fasoft"


def test_iniciar_com_perfil_inexistente_para(tmp_path, capsys):
    semestre = tmp_path / "2027-1"
    semestre.mkdir()
    assert main(["iniciar", "2027-1", "--raiz", str(semestre), "--perfil", "nao-existe", "--json"]) == 4
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv/Scripts/python -m pytest testes/unidade/test_perfil_padrao.py -v`
Expected: FAIL (`perfil-nao-encontrado` para `neutro` / `id == "fasoft"`).

- [ ] **Step 3: `neutro.yaml`**

```yaml
versao_esquema: 2
perfil:
  id: neutro
  instituicao: "Instituição de ensino"
  disciplina_pasta: '^(?P<nome>[^.~_].*)$'
  subpastas_disciplina: [planejamento, aulas, atividades, projetos, referencias, codigo, arquivo]
  pasta_arquivo: arquivo
  pasta_avaliacoes: '(?i)^(\d{2} - )?avalia'
  pasta_modelos: '(?i)^(\d{2} - )?modelos?$'
  etapas_avaliacao: [AV1, AV2, AV3]
  nomenclatura:
    aula: '^Aula \d{2} - '
    lista: '^(Lista|Atividade|Aula) \d{2} - '
    pasta: '^'
    sufixos_proibidos: ['\(Revisado\)', '_v\d+\b', '\(v\d+\)', ' - [Cc][oó]pia\b', ' \(\d+\)\.', '\.bak$']
  carga_horaria: { unidade: null, minutos_hora_aula: null }
  exclusao: ["*Notas*", "*notas*", "*NOTAS*", "*Alunos*", "*alunos*", "*Relatórios*", "*relatorios*",
             "*Relatorios*", "*Entregas*", "*entregas*", "*TFC*", "*TCC*", "*tcc*", "*Estágio*", "*estagio*",
             "*/projetos"]
  estrutura:
    semestre: '^(?P<ano>\d{4})[-._ ](?P<periodo>[12])$'
    administracao: '(?i)^(\d{2} - )?administra'
    papeis: { planejamento: planejamento, aulas: aulas, atividades: atividades, projetos: projetos,
              referencias: referencias, codigo: codigo, arquivo: arquivo }
```

- [ ] **Step 4: Código**

`acad/perfil/perfil.py`: `def carregar_perfil(id: str) -> Perfil:` (sem padrão).

`acad/contexto.py`:

```python
PERFIL_PADRAO = "neutro"


def perfil() -> Perfil:
    configuracao = carregar_configuracao()
    return carregar_perfil((configuracao or {}).get("perfil") or PERFIL_PADRAO)
```

`acad/comandos/perfil.py`, `iniciar`: `parser.add_argument("--perfil")` (sem default); no `executar`, antes do documento:

```python
avisos = []
escolhido = args.perfil or (contexto.carregar_configuracao() or {}).get("perfil")
if not escolhido:
    escolhido = contexto.PERFIL_PADRAO
    if escolhido == "neutro":
        avisos.append("Usei o perfil neutro, sem marca de instituição. Se quiser, crio o perfil da sua "
                      "instituição a partir da sua pasta.")
carregar_perfil(escolhido)  # falha cedo, com a mensagem simples, se o perfil não existir
documento = {"versao_esquema": 1, "perfil": escolhido, ...}
...
return Resultado(ok=True, mensagem=mensagem, dados=documento, avisos=avisos)
```

`disciplina criar`: `padrao = contexto.perfil()` no lugar de `carregar_perfil()`.

- [ ] **Step 5: Fixture e testes antigos**

Em `testes/conftest.py`:

```python
@pytest.fixture
def perfil_fasoft(monkeypatch):
    from acad import contexto
    monkeypatch.setattr(contexto, "PERFIL_PADRAO", "fasoft")


@pytest.fixture
def semestre_sintetico(tmp_path, perfil_fasoft) -> Path:
    ...  # corpo atual sem mudança
```

Troque `carregar_perfil()` por `carregar_perfil("fasoft")` nos arquivos listados em **Files**. Depois rode a suíte; para cada teste que ainda falhar porque espera o comportamento fasoft sem usar `semestre_sintetico` (ex.: testes que usam `testes/amostras/fasoft` direto, testes de MCP e de CLI), acrescente `perfil_fasoft` aos parâmetros do teste — ou `pytestmark = pytest.mark.usefixtures("perfil_fasoft")` no módulo quando todos os testes dele usam a árvore Fasoft. Não altere asserções.

- [ ] **Step 6: Rodar**

Run: `.venv/Scripts/python -m pytest -q` e `.venv/Scripts/python -m pytest -q -m "drive or hosts or rede or latex"`
Expected: verde (marcados: `skip` onde o ambiente não tem a ferramenta, como na linha de base).

- [ ] **Step 7: Commit**

```bash
git add acad/perfil/perfis/neutro.yaml acad/perfil/perfil.py acad/contexto.py acad/comandos/perfil.py testes
git commit -m "feat: perfil neutro de reserva e fim do padrão fasoft implícito"
```

---

### Task 6: Mensagens e avisos de modelos (slides e prova)

**Files:**
- Modify: `acad/geracao/aula.py:102-115`
- Modify: `acad/comandos/gerar.py:23-47` (`gerar aula`: passa identidade) e `:93-104` (modelo de prova)
- Test: `testes/unidade/test_gerar_aula.py`, `testes/unidade/test_avaliacao.py`

**Interfaces:**
- Consumes: `Perfil.modelo_slides`, `Perfil.modelo_prova`, `Perfil.slides`, `Perfil.pasta_modelos`, `obter_gerador(ler_bytes, identidade)`.
- Produces: `planejar_aula(..., perfil=None)` — novo parâmetro nomeado opcional no fim (padrão `contexto.perfil()`).

- [ ] **Step 1: Testes que falham**

Em `testes/unidade/test_gerar_aula.py` acrescente (use os fixtures `disc`/`semestre_sintetico` e a forma como os testes vizinhos chamam `planejar_aula`; copie a chamada de um teste existente e acrescente `perfil=`):

```python
from dataclasses import replace

from acad.perfil.perfil import carregar_perfil


def _planejar(ws, semestre, disc, perfil):
    return planejar_aula(ws, semestre, disc, "Aula 03", CONTEUDO, GeradorSlidesFalso(),
                         datetime(2026, 9, 1).astimezone(), False, perfil=perfil)


def test_modelo_de_slides_com_outro_nome(disc, semestre_sintetico):
    (semestre_sintetico / "09 - Modelos" / "Slides da Casa").mkdir()
    perfil = replace(carregar_perfil("fasoft"), modelo_slides="Slides da Casa")
    ws = Workspace(semestre_sintetico, perfil.exclusao)
    _, avisos = _planejar(ws, semestre_sintetico, disc, perfil)
    assert not any("logotipos" in aviso for aviso in avisos)


def test_sem_modelo_declarado_nao_avisa_logo(disc, semestre_sintetico):
    perfil = replace(carregar_perfil("fasoft"), modelo_slides=None)
    ws = Workspace(semestre_sintetico, perfil.exclusao)
    _, avisos = _planejar(ws, semestre_sintetico, disc, perfil)
    assert not any("logotipos" in aviso for aviso in avisos)


def test_modelo_declarado_ausente_avisa(disc, semestre_sintetico):
    perfil = carregar_perfil("fasoft")
    ws = Workspace(semestre_sintetico, perfil.exclusao)
    _, avisos = _planejar(ws, semestre_sintetico, disc, perfil)
    assert any("logotipos" in aviso for aviso in avisos)
```

Em `testes/unidade/test_avaliacao.py`, ache o teste que gera prova sem `Modelo LaTeX` (cai no genérico) e acrescente a asserção `assert "Usei o modelo simples de prova, sem o cabeçalho da instituição." in dados["avisos"]`; se não houver esse teste, crie um copiando o teste de geração de prova mais simples do arquivo. No teste que usa o modelo institucional (se existir), garanta que esse aviso **não** aparece.

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv/Scripts/python -m pytest testes/unidade/test_gerar_aula.py testes/unidade/test_avaliacao.py -v`
Expected: FAIL (`planejar_aula() got an unexpected keyword argument 'perfil'`; aviso ausente).

- [ ] **Step 3: `aula.py`**

Assinatura: acrescente `perfil=None` como último parâmetro; no início, `perfil = perfil or contexto.perfil()` (import local `from acad import contexto` se houver risco de ciclo). Troque o bloco 102-115 por:

```python
    pasta_modelos = next((p for p in ws.listar(semestre)
                          if p.is_dir() and perfil.pasta_modelos.match(p.name)), None)
    if "slides" in conteudo:
        modelo_slides = None
        if pasta_modelos is not None and perfil.modelo_slides:
            candidato = pasta_modelos / perfil.modelo_slides
            modelo_slides = candidato if candidato.is_dir() else None
        ...  # dados_disciplina, contexto, adicionar e avisos_editoriais como hoje
        avisos += avisos_editoriais(conteudo["slides"]["slides"], perfil.slides.limites)
        quer_logos = bool(perfil.slides.logo_cabecalho or perfil.slides.logos_capa)
        if perfil.modelo_slides and quer_logos and modelo_slides is None:
            avisos.append("Não achei o modelo de slides na pasta de modelos; os slides saem sem os logotipos.")
```

No fasoft (`pasta_modelos` = `^\d{2} - Modelos$`, modelo `Modelo de Slides UniRV`, com logos) o resultado é o de hoje. Os demais literais de `aula.py` (`01 - Planejamento`, `05 - Materiais de Referência`) ficam para a Tarefa 7.

- [ ] **Step 4: `gerar.py`**

`gerar aula`: `perfil = contexto.perfil()`; `obter_gerador(ws.ler_bytes, perfil.slides)`; passe `perfil=perfil` a `planejar_aula`.

Modelo de prova (linhas 93-104):

```python
        perfil = contexto.perfil()
        pasta_modelos = next((p for p in ws.listar(semestre)
                              if p.is_dir() and perfil.pasta_modelos.match(p.name)), None)
        modelo_institucional = (pasta_modelos / perfil.modelo_prova
                                if pasta_modelos and perfil.modelo_prova else None)
        if modelo_institucional and ws.existe(modelo_institucional):
            ...  # como hoje
        else:
            ...  # como hoje
            avisos_modelo = ["Usei o modelo simples de prova, sem o cabeçalho da instituição."]
```

Inicialize `avisos_modelo = []` antes do `if` e some `avisos_modelo` à lista `avisos` que já existe logo abaixo (`avisos = []` → `avisos = list(avisos_modelo)`).

- [ ] **Step 5: Rodar**

Run: `.venv/Scripts/python -m pytest testes/unidade/test_gerar_aula.py testes/unidade/test_avaliacao.py -v`, `.venv/Scripts/python -m pytest -q` e `.venv/Scripts/python -m pytest -q -m latex`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add acad/geracao/aula.py acad/comandos/gerar.py testes/unidade/test_gerar_aula.py testes/unidade/test_avaliacao.py
git commit -m "feat: modelos de slides e prova pelo perfil, com aviso no modelo simples"
```

---

### Task 7: Nomes de subpasta pelo perfil

**Files (literal → substituição):**
- `acad/contexto.py:59-60` — `p.name.startswith("00 - ")` → `perfil().re_administracao.match(p.name)`; `:71-79` — `"01 - Planejamento"` → `perfil_atual.pasta("planejamento")`; use `partes = perfil_atual.partes_disciplina(pasta.name)` e compare `identificador == sem_acento(partes["num"] or "")` e `identificador in sem_acento(partes["nome"] or "")` (evita `None`).
- `acad/validacao/validar.py:41-42` → `perfil.re_administracao.match(p.name)`; `:52` → `disc / perfil.pasta("planejamento")`; `:87` → `disc / perfil.pasta("aulas")`.
- `acad/validacao/nomenclatura.py:18` → `ws.existe(caminho / perfil.pasta("planejamento"))`; `:45-46` → `perfil.pasta("aulas")`, `perfil.pasta("atividades")`.
- `acad/geracao/nomes.py` — `arquivos_da_aula(num, tema, perfil)`: `f"{perfil.pasta('aulas')}/Aula {numero} - {limpo}.pptx"`, idem roteiro; `f"{perfil.pasta('codigo')}/aula-{numero}-{slug(limpo)}"`; `f"{perfil.pasta('atividades')}/Lista {numero} - {limpo}.md"`.
- `acad/geracao/aula.py:48, 71, 109, 119, 122, 129` — `"01 - Planejamento"` → `perfil.pasta("planejamento")`; `"05 - Materiais de Referência"` → `perfil.pasta("referencias")`; `arquivos_da_aula(num, conteudo["tema"], perfil)`.
- `acad/planejamento/arquivos.py:10-15` — `_planejamento` e `caminho` usam `contexto.perfil().pasta("planejamento")` (import local `from acad import contexto` dentro da função).
- `acad/comandos/perfil.py:81` — `periodo = 1 if semestre.name.startswith("Primeiro") else 2` → `ano, periodo = contexto.perfil().semestre_de(semestre) or (int(semestre.parent.name), 2)` e `"semestre": f"{ano}-{periodo}"` (remove o uso de `semestre.parent.name`); `:91, 125` → `contexto.perfil().pasta("planejamento")`.
- `acad/comandos/encontros.py:36`, `acad/comandos/cronograma.py:33`, `acad/comandos/aula.py:39` — `"01 - Planejamento"` → `contexto.perfil().pasta("planejamento")`.
- `acad/cronograma/consulta.py` — `consultar(raiz, alvo, perfil)` (era `exclusao`), `ws = Workspace(raiz, perfil.exclusao)`; `_materiais(ws, disciplina, numero, topico, perfil)` com `perfil.pasta("aulas" | "atividades" | "codigo")`; `_cronogramas(ws, pasta, perfil)` com `caminho.name != perfil.pasta("arquivo")`; `cronograma.parent.parent` fica.
- `acad/comandos/base.py:47` → `consulta.consultar(raiz, alvo, contexto.perfil())`; testes `test_consulta.py:19,25`, `test_paridade_cronograma.py:45,55` passam `carregar_perfil("fasoft")` em vez de `.exclusao`.
- `acad/perfil/detectar.py:44` fica para a Tarefa 8.

- Test: `testes/unidade/test_estrutura_neutra.py` (novo)

**Interfaces:**
- Consumes: `Perfil.pasta`, `partes_disciplina`, `semestre_de`, `re_administracao`.
- Produces: `arquivos_da_aula(num: str, tema: str, perfil: Perfil) -> dict[str, str]`; `consultar(raiz: Path, alvo: date, perfil: Perfil) -> dict`.

- [ ] **Step 1: Fixture neutra e testes que falham**

Acrescente em `testes/conftest.py`:

```python
@pytest.fixture
def semestre_neutro(tmp_path) -> Path:
    """Outra instituição: `Materiais/2027-1`, pastas minúsculas, sem número."""
    semestre = tmp_path / "Materiais" / "2027-1"
    (semestre / "administracao").mkdir(parents=True)
    (semestre / "avaliacoes" / "AV1").mkdir(parents=True)
    (semestre / "modelos").mkdir()
    for disciplina in ("Algoritmos", "Banco de Dados"):
        for subpasta in ("planejamento", "aulas", "atividades", "referencias", "codigo", "arquivo"):
            (semestre / disciplina / subpasta).mkdir(parents=True)
    _mk(semestre / "Algoritmos" / "projetos" / "entrega-aluno.txt", "nome do aluno")
    _mk(semestre / "Notas 2027-1.xlsx", "x")
    return semestre
```

```python
# testes/unidade/test_estrutura_neutra.py
from acad.arquivos.privacidade import Workspace
from acad.contexto import localizar_disciplina
from acad.geracao.nomes import arquivos_da_aula
from acad.perfil.perfil import carregar_perfil
from acad.validacao.nomenclatura import disciplinas, validar_nomes
from acad.validacao.validar import validar_semestre

NEUTRO = carregar_perfil("neutro")


def test_nomes_dos_arquivos_seguem_o_perfil():
    nomes = arquivos_da_aula("03", "Grafos", NEUTRO)
    assert nomes["slides"] == "aulas/Aula 03 - Grafos.pptx"
    assert nomes["codigo"] == "codigo/aula-03-grafos"
    assert nomes["lista"] == "atividades/Lista 03 - Grafos.md"
    assert arquivos_da_aula("03", "Grafos", carregar_perfil("fasoft"))["slides"] == "02 - Aulas/Aula 03 - Grafos.pptx"


def test_disciplinas_da_outra_instituicao(semestre_neutro):
    ws = Workspace(semestre_neutro, NEUTRO.exclusao)
    assert sorted(p.name for p in disciplinas(ws, semestre_neutro, NEUTRO)) == ["Algoritmos", "Banco de Dados"]


def test_localizar_sem_numero(semestre_neutro):
    ws = Workspace(semestre_neutro, NEUTRO.exclusao)
    assert localizar_disciplina(ws, semestre_neutro, "algoritmos").name == "Algoritmos"


def test_validar_sem_erro_de_estrutura(semestre_neutro):
    ws = Workspace(semestre_neutro, NEUTRO.exclusao)
    achados = validar_semestre(ws, semestre_neutro, NEUTRO) + validar_nomes(ws, semestre_neutro, NEUTRO)
    assert not [a for a in achados if a.nivel == "erro"], achados
    assert ws.excluido(semestre_neutro / "Algoritmos" / "projetos")
```

`localizar_disciplina` usa `contexto.perfil()`, que sem configuração já é `neutro`; não use `perfil_fasoft` nestes testes.

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv/Scripts/python -m pytest testes/unidade/test_estrutura_neutra.py -v`
Expected: FAIL (`arquivos_da_aula() takes 2 positional arguments`; disciplinas vazias).

- [ ] **Step 3: Aplicar as substituições da lista Files**, uma por arquivo. Atualize `test_gerar_aula.py:38` para `arquivos_da_aula("03", "Rotações AVL: casos?", carregar_perfil("fasoft"))`.

- [ ] **Step 4: Conferir que não sobrou literal**

Run: `grep -rnE '"0[0-9] - |"99 - |startswith\("Primeiro"\)|"Modelos"' acad --include=*.py`
Expected: só `acad/perfil/padroes.py` e `acad/perfil/detectar.py` (Tarefa 8).

- [ ] **Step 5: Rodar**

Run: `.venv/Scripts/python -m pytest -q` e `.venv/Scripts/python -m pytest -q -m drive`
Expected: verde (`drive` passa ou fica `skip` sem o Drive, como na linha de base).

- [ ] **Step 6: Commit**

```bash
git add acad testes
git commit -m "refactor: nomes de subpasta e período lidos do perfil"
```

---

### Task 8: Detecção de semestre e raiz pela estrutura

**Files:**
- Modify: `acad/perfil/detectar.py` (reescrita)
- Modify: `acad/cronograma/consulta.py:22-36` (`encontrar_raiz`)
- Modify: `acad/comandos/base.py:44`
- Test: `testes/unidade/test_consulta.py`, `testes/unidade/test_configuracao_guiada.py`, `testes/unidade/test_raiz_estrutura.py` (novo)

**Interfaces:**
- Consumes: `Perfil.semestre_de`, `base_semestre`, `disciplinas` (de `acad.validacao.nomenclatura`).
- Produces: `encontrar_raiz(inicio: Path, perfil: Perfil) -> Path | None`; `semestre_valido(pasta: Path, perfil: Perfil) -> bool` (em `consulta.py`); `detectar(raiz, perfil)` devolve também `"raiz"` (mesmo valor de `"raiz_fasoft"`).

- [ ] **Step 1: Testes que falham**

```python
# testes/unidade/test_raiz_estrutura.py
from pathlib import Path

from acad.cronograma.consulta import encontrar_raiz
from acad.perfil.detectar import detectar
from acad.perfil.perfil import carregar_perfil

AMOSTRA = Path(__file__).resolve().parents[1] / "amostras" / "fasoft"
FASOFT, NEUTRO = carregar_perfil("fasoft"), carregar_perfil("neutro")


def test_fasoft_de_qualquer_ponto_acha_a_raiz():
    semestre = AMOSTRA / "2026" / "Segundo Semestre"
    disciplina = semestre / "04 - Estrutura de Dados 2 - 5º Período" / "02 - Aulas"
    for inicio in (AMOSTRA, semestre, disciplina):
        assert encontrar_raiz(inicio, FASOFT) == AMOSTRA


def test_nao_le_agents_md(tmp_path):
    (tmp_path / "AGENTS.md").write_text("# Fasoft\n", encoding="utf-8")
    assert encontrar_raiz(tmp_path, FASOFT) is None


def test_outra_instituicao(semestre_neutro):
    base = semestre_neutro.parent
    for inicio in (base, semestre_neutro, semestre_neutro / "Algoritmos" / "aulas"):
        assert encontrar_raiz(inicio, NEUTRO) == base


def test_detectar_outra_instituicao(semestre_neutro):
    dados = detectar(semestre_neutro, NEUTRO)
    assert dados["semestres"] == [{"pasta": "2027-1", "ano": 2027, "periodo": 1}]
    assert dados["raiz"] == str(semestre_neutro.parent) == dados["raiz_fasoft"]
    assert sorted(d["nome"] for d in dados["disciplinas"]) == ["Algoritmos", "Banco de Dados"]
    assert dados["pasta_avaliacoes"] == "avaliacoes" and dados["pasta_modelos"] == "modelos"
    algoritmos = next(d for d in dados["disciplinas"] if d["nome"] == "Algoritmos")
    assert algoritmos["subpastas_faltando"] == []  # "projetos" existe (protegida, mas existe)
    banco = next(d for d in dados["disciplinas"] if d["nome"] == "Banco de Dados")
    assert banco["subpastas_faltando"] == ["projetos"]
```

Atualize `testes/unidade/test_consulta.py:11` para `encontrar_raiz(AMOSTRA / "2026" / "Segundo Semestre", carregar_perfil("fasoft")) == AMOSTRA`.

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv/Scripts/python -m pytest testes/unidade/test_raiz_estrutura.py testes/unidade/test_consulta.py -v`
Expected: FAIL (`encontrar_raiz() takes 1 positional argument`).

- [ ] **Step 3: `encontrar_raiz`**

```python
def semestre_valido(pasta: Path, perfil) -> bool:
    if not pasta.is_dir() or perfil.semestre_de(pasta) is None:
        return False
    from acad.validacao.nomenclatura import disciplinas
    return bool(disciplinas(Workspace(pasta, perfil.exclusao), pasta, perfil))


def _semestre_em(pasta: Path, perfil, profundidade: int = 2) -> Path | None:
    if semestre_valido(pasta, perfil):
        return pasta
    if profundidade == 0:
        return None
    for filho in Workspace(pasta, perfil.exclusao).listar(pasta):
        if filho.is_dir() and not filho.name.startswith("."):
            achado = _semestre_em(filho, perfil, profundidade - 1)
            if achado is not None:
                return achado
    return None


def encontrar_raiz(inicio: Path, perfil) -> Path | None:
    atual = Path(inicio).resolve()
    while True:
        semestre = _semestre_em(atual, perfil)
        if semestre is not None:
            return perfil.base_semestre(semestre)
        if atual.parent == atual:
            return None
        atual = atual.parent
```

Se `Workspace.listar` falhar em pasta sem permissão, envolva o `for` em `try/except OSError: return None`. `acad/comandos/base.py:44`: `consulta.encontrar_raiz(..., contexto.perfil())`.

- [ ] **Step 4: Reescrever `detectar.py`**

```python
from __future__ import annotations

from pathlib import Path

from acad.arquivos.caminhos import relativo_posix
from acad.arquivos.privacidade import Workspace
from acad.cronograma.consulta import semestre_valido


def _semestres(raiz: Path, perfil) -> list[Path]:
    if perfil.semestre_de(raiz) is not None:
        return [raiz]
    achados = []
    ws = Workspace(raiz, perfil.exclusao)
    for filho in ws.listar(raiz):
        if not filho.is_dir():
            continue
        if perfil.semestre_de(filho) is not None:
            achados.append(filho)
        else:
            achados += [neto for neto in ws.listar(filho)
                        if neto.is_dir() and perfil.semestre_de(neto) is not None]
    return sorted(achados)


def detectar(raiz: Path, perfil) -> dict:
    raiz = Path(raiz).resolve()
    semestres = _semestres(raiz, perfil)
    base = perfil.base_semestre(semestres[0]) if semestres else None
    saida = {"raiz": str(base) if base else None, "raiz_fasoft": str(base) if base else None,
             "semestres": [], "disciplinas": [], "pasta_avaliacoes": None, "pasta_modelos": None}
    for semestre in semestres:
        ano, periodo = perfil.semestre_de(semestre)
        saida["semestres"].append({"pasta": relativo_posix(semestre, base), "ano": ano, "periodo": periodo})
        ws_sem = Workspace(semestre, perfil.exclusao)
        for pasta in ws_sem.listar(semestre):
            if not pasta.is_dir():
                continue
            if perfil.pasta_avaliacoes.match(pasta.name):
                saida["pasta_avaliacoes"] = pasta.name
            elif perfil.pasta_modelos.match(pasta.name):
                saida["pasta_modelos"] = pasta.name
            elif perfil.re_administracao.match(pasta.name):
                continue
            else:
                partes = perfil.partes_disciplina(pasta.name)
                planejamento = pasta / perfil.pasta("planejamento")
                if not partes or not planejamento.is_dir():
                    continue
                tem_cronograma = any(item.name.startswith("Cronograma") and item.suffix.lower() == ".xlsx"
                                     for item in ws_sem.listar(planejamento))
                saida["disciplinas"].append({
                    "pasta": relativo_posix(pasta, semestre), "numero": partes["num"],
                    "nome": partes["nome"], "periodo": partes["periodo"], "tem_cronograma": tem_cronograma,
                    "subpastas_faltando": [nome for nome in perfil.subpastas_disciplina
                                           if not (pasta / nome).is_dir()],
                })
    return saida
```

Diferenças conscientes frente ao MVP (registre no commit): `raiz` nova; com o fasoft, a pasta de administração (`00 - …`) nunca casava `disciplina_pasta` com `01 - Planejamento` dentro, então pular `re_administracao` não muda o resultado. Se `semestre_valido` não for usado aqui, não o importe. Confira se `relativo_posix` aceita base `None`; se `base` for `None` não há semestres, então o laço não roda.

- [ ] **Step 5: Rodar**

Run: `.venv/Scripts/python -m pytest testes/unidade/test_raiz_estrutura.py testes/unidade/test_consulta.py testes/unidade/test_configuracao_guiada.py testes/integracao/test_paridade_cronograma.py -v`, `.venv/Scripts/python -m pytest -q`, `.venv/Scripts/python -m pytest -q -m drive`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add acad/perfil/detectar.py acad/cronograma/consulta.py acad/comandos/base.py testes
git commit -m "feat: semestre e raiz reconhecidos pela estrutura do perfil, não pela palavra Fasoft"
```

---

### Task 9: Inferir o perfil a partir da pasta

**Files:**
- Create: `acad/perfil/inferir.py`
- Test: `testes/unidade/test_inferir.py` (novo)

**Interfaces:**
- Consumes: `ler_documento_perfil("neutro")`, `paleta_de_cor`, `problemas_do_perfil`, `sem_acento` (`acad.arquivos.caminhos`), `Workspace`.
- Produces: `inferir_perfil(semestre: Path, id: str, instituicao: str, cor: str | None = None, rodape: list[str] | None = None, local: str | None = None) -> tuple[dict, dict]` — devolve `(documento_v2, resumo)` com `resumo = {"ano": int, "periodo": int, "disciplinas": list[str], "papeis_criados": list[str]}`. Levanta `ErroAcad("semestre-nao-reconhecido", …, saida=4)`.

- [ ] **Step 1: Testes que falham**

```python
# testes/unidade/test_inferir.py
import pytest

from acad.erros import ErroAcad
from acad.perfil.inferir import inferir_perfil
from acad.perfil.perfil import perfil_de_documento
from acad.perfil.validar import problemas_do_perfil


def test_infere_a_outra_instituicao(semestre_neutro):
    documento, resumo = inferir_perfil(semestre_neutro, "faculdade-x", "Faculdade X")
    assert problemas_do_perfil(documento) == []
    perfil = perfil_de_documento(documento)
    assert perfil.id == "faculdade-x" and perfil.instituicao == "Faculdade X"
    assert perfil.semestre_de(semestre_neutro) == (2027, 1)
    assert perfil.pasta("aulas") == "aulas" and perfil.pasta("referencias") == "referencias"
    assert perfil.pasta("projetos") == "projetos"
    assert "*/projetos" in perfil.exclusao
    assert resumo == {"ano": 2027, "periodo": 1, "disciplinas": ["Algoritmos", "Banco de Dados"],
                      "papeis_criados": []}
    assert perfil.slides.capa_linhas == ()


def test_papel_ausente_ganha_nome_neutro(tmp_path):
    semestre = tmp_path / "2026" / "2º Semestre"
    for disciplina in ("01 - Redes", "02 - Sistemas"):
        for subpasta in ("01 - Planejamento das Aulas", "02 - Aulas", "03 - Exercícios"):
            (semestre / disciplina / subpasta).mkdir(parents=True)
    documento, resumo = inferir_perfil(semestre, "x", "X")
    perfil = perfil_de_documento(documento)
    assert perfil.semestre_de(semestre) == (2026, 2)
    assert perfil.pasta("planejamento") == "01 - Planejamento das Aulas"
    assert perfil.pasta("atividades") == "03 - Exercícios"
    assert perfil.partes_disciplina("01 - Redes")["nome"] == "Redes"
    assert perfil.re_pasta.pattern == r"^\d{2} - "
    assert set(resumo["papeis_criados"]) == {"projetos", "referencias", "codigo", "arquivo"}
    assert perfil.subpastas_disciplina[-4:] == ("projetos", "referencias", "codigo", "arquivo")


def test_cor_e_rodape(semestre_neutro):
    documento, _ = inferir_perfil(semestre_neutro, "x", "X", cor="1f3a5f",
                                  rodape=["FACULDADE X", "Curso Y"], local="Cidade — {ano}")
    slides = perfil_de_documento(documento).slides
    assert slides.paleta["principal"] == "1F3A5F"
    assert slides.capa_linhas == ("FACULDADE X", "Curso Y") and slides.capa_local == "Cidade — {ano}"


def test_modelos_achados(semestre_neutro):
    (semestre_neutro / "modelos" / "slides da casa").mkdir()
    (semestre_neutro / "modelos" / "latex").mkdir()
    (semestre_neutro / "modelos" / "latex" / "prova-base.tex").write_text("x", encoding="utf-8")
    perfil = perfil_de_documento(inferir_perfil(semestre_neutro, "x", "X")[0])
    assert perfil.modelo_slides == "slides da casa"
    assert perfil.modelo_prova == "latex/prova-base.tex"


def test_semestre_sem_ano_pede_decisao(tmp_path):
    (tmp_path / "semestre atual" / "Disc" / "aulas").mkdir(parents=True)
    with pytest.raises(ErroAcad) as erro:
        inferir_perfil(tmp_path / "semestre atual", "x", "X")
    assert erro.value.saida == 4 and "2027-1" in erro.value.mensagem


def test_nao_entra_em_pasta_protegida(semestre_neutro, monkeypatch):
    lidos = []
    from acad.arquivos import privacidade
    original = privacidade.Workspace.listar
    monkeypatch.setattr(privacidade.Workspace, "listar",
                        lambda self, pasta: lidos.append(pasta.name) or original(self, pasta))
    inferir_perfil(semestre_neutro, "x", "X")
    assert "projetos" not in lidos
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv/Scripts/python -m pytest testes/unidade/test_inferir.py -v`
Expected: FAIL (`ModuleNotFoundError`).

- [ ] **Step 3: Implementar `acad/perfil/inferir.py`**

```python
"""Monta o perfil de uma instituição pela organização da pasta do semestre (só nomes de pastas)."""
from __future__ import annotations

import copy
import re
from pathlib import Path

from acad.arquivos.caminhos import sem_acento
from acad.arquivos.privacidade import Workspace
from acad.erros import ErroAcad
from acad.geracao.identidade import paleta_de_cor
from acad.perfil.padroes import ESTRUTURA_V1
from acad.perfil.perfil import ler_documento_perfil

FORMAS_SEMESTRE = [
    (ESTRUTURA_V1["semestre"], ESTRUTURA_V1["periodos"]),
    (r"^(?P<ano>\d{4})/(?P<periodo>[12])(?:º|o)?(?: [Ss]emestre)?$", None),
    (r"^(?P<ano>\d{4})[-._ ](?P<periodo>[12])$", None),
]
PAPEIS = [("planejamento", r"planej"), ("aulas", r"aula"), ("atividades", r"ativ|lista|exerc"),
          ("projetos", r"proj|entreg|trabalho"), ("referencias", r"refer|biblio|material"),
          ("codigo", r"codig|exemplo|fonte"), ("arquivo", r"arquivo|antig|morto")]
COM_NUMERO = r"^(?P<num>\d{2}) - (?P<nome>.+?)(?: - (?P<periodo>.+ Período))?$"


def _semestre(semestre: Path):
    for padrao, periodos in FORMAS_SEMESTRE:
        alvo = f"{semestre.parent.name}/{semestre.name}" if "/" in padrao else semestre.name
        correspondencia = re.match(padrao, alvo)
        if correspondencia:
            texto = correspondencia["periodo"]
            return padrao, periodos, int(correspondencia["ano"]), (periodos[texto] if periodos else int(texto))
    raise ErroAcad("semestre-nao-reconhecido",
                   "Não reconheci o ano e o período pelo nome da pasta do semestre. "
                   "Renomeie para algo como 2027-1 ou me diga qual é.", semestre.name, saida=4)


def inferir_perfil(semestre: Path, id: str, instituicao: str, cor: str | None = None,
                   rodape: list[str] | None = None, local: str | None = None) -> tuple[dict, dict]:
    semestre = Path(semestre).resolve()
    documento = copy.deepcopy(ler_documento_perfil("neutro"))
    perfil = documento["perfil"]
    padrao, periodos, ano, periodo = _semestre(semestre)
    ws = Workspace(semestre, perfil["exclusao"])
    especiais = [re.compile(perfil[chave]) for chave in ("pasta_avaliacoes", "pasta_modelos")]
    especiais.append(re.compile(perfil["estrutura"]["administracao"]))
    pastas = [p for p in ws.listar(semestre) if p.is_dir() and not p.name.startswith((".", "~", "_"))]
    disciplinas = {}
    for pasta in pastas:
        if any(regra.match(pasta.name) for regra in especiais):
            continue
        subpastas = [s.name for s in ws.listar(pasta) if s.is_dir()] + [
            Path(p).name for p in ws.protegidas if Path(p).parent.name == pasta.name]
        if len(set(subpastas)) >= 2:
            disciplinas[pasta.name] = sorted(set(subpastas))
    if not disciplinas:
        raise ErroAcad("disciplinas-nao-encontradas",
                       "Não encontrei pastas de disciplina nesse semestre.", str(semestre), saida=4)
    contagem = {}
    for nomes in disciplinas.values():
        for nome in nomes:
            contagem[nome] = contagem.get(nome, 0) + 1
    subpastas = sorted(nome for nome, vezes in contagem.items() if vezes * 2 >= len(disciplinas))
    papeis, criados = {}, []
    for papel, regra in PAPEIS:
        achado = next((nome for nome in subpastas if nome not in papeis.values()
                       and re.search(regra, sem_acento(nome).lower())), None)
        if achado is None:
            achado = papel
            criados.append(papel)
            subpastas.append(papel)
        papeis[papel] = achado
    numeradas = all(re.match(r"^\d{2} - ", nome) for nome in disciplinas)
    perfil.update({"id": id, "instituicao": instituicao, "subpastas_disciplina": subpastas,
                   "pasta_arquivo": papeis["arquivo"]})
    if numeradas:
        perfil["disciplina_pasta"] = COM_NUMERO
        perfil["nomenclatura"]["pasta"] = r"^\d{2} - "
    perfil["estrutura"] = {"semestre": padrao, "administracao": perfil["estrutura"]["administracao"],
                           "papeis": papeis, **({"periodos": periodos} if periodos else {})}
    projetos = f"*/{papeis['projetos']}"
    if projetos not in perfil["exclusao"]:
        perfil["exclusao"].append(projetos)
    modelos = _modelos(ws, semestre, re.compile(perfil["pasta_modelos"]))
    if modelos:
        perfil["modelos"] = modelos
    slides = {}
    if cor:
        slides["paleta"] = paleta_de_cor(cor)
    if rodape is not None or local is not None:
        slides["capa"] = {**({"linhas": list(rodape)} if rodape is not None else {}),
                          **({"local": local} if local is not None else {})}
    if slides:
        perfil["slides"] = slides
    resumo = {"ano": ano, "periodo": periodo, "disciplinas": sorted(disciplinas), "papeis_criados": criados}
    return documento, resumo


def _modelos(ws: Workspace, semestre: Path, regra) -> dict:
    pasta = next((p for p in ws.listar(semestre) if p.is_dir() and regra.match(p.name)), None)
    if pasta is None:
        return {}
    modelos = {}
    filhos = [p for p in ws.listar(pasta) if p.is_dir()]
    slides = next((p for p in filhos if "slide" in sem_acento(p.name).lower()), None)
    if slides:
        modelos["slides"] = slides.name
    for candidato in [pasta, *filhos]:
        tex = next((a for a in ws.listar(candidato)
                    if a.is_file() and a.suffix == ".tex" and "prova" in a.name.lower()), None)
        if tex:
            modelos["prova"] = tex.relative_to(pasta).as_posix()
            break
    return modelos
```

Confirme como `Workspace.protegidas` está definido em `acad/arquivos/privacidade.py` (é usado em `validacao/nomenclatura.py:36` como lista de caminhos relativos em texto `a/b`). Se o formato for outro, ajuste só a expressão que recupera os nomes das subpastas protegidas — a pasta protegida conta como existente, mas **não** é listada por dentro. Se `listar` de uma pasta ainda não registra protegidas antes de ser chamado na pasta-mãe, a ordem acima (listar a disciplina primeiro) já resolve.

- [ ] **Step 4: Rodar**

Run: `.venv/Scripts/python -m pytest testes/unidade/test_inferir.py -v` e `.venv/Scripts/python -m pytest -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add acad/perfil/inferir.py testes/unidade/test_inferir.py
git commit -m "feat: perfil da instituição inferido pela organização das pastas"
```

---

### Task 10: Comandos `perfil criar`, `perfil importar`, `perfil listar`

**Files:**
- Modify: `acad/comandos/perfil.py`
- Modify: `acad/mcp.py` **só se** ele tiver lista fixa de comandos expostos (confira com `grep -n "perfil detectar" acad/mcp.py`); se houver, acrescente os três com a mesma forma das entradas vizinhas.
- Test: `testes/unidade/test_comando_perfil.py` (novo)

**Interfaces:**
- Consumes: `inferir_perfil`, `problemas_do_perfil`, `validar_perfil_ou_falhar`, `pasta_perfis_usuario`, `perfis_disponiveis`, `criar_proposta`, `Operacao`, `contexto.perfil`.
- Produces: comandos CLI `perfil criar --raiz R --id I --instituicao T [--cor C] [--rodape L]... [--local X]`, `perfil importar --arquivo A`, `perfil listar`.

- [ ] **Step 1: Testes que falham**

```python
# testes/unidade/test_comando_perfil.py
import json

from acad import esquemas
from acad.cli import main
from acad.mensagens import contem_termo_tecnico
from acad.perfil.perfil import carregar_perfil, pasta_perfis_usuario


def _rodar(capsys, *argumentos):
    codigo = main([*argumentos, "--json"])
    return codigo, json.loads(capsys.readouterr().out)


def test_criar_so_propoe_e_aplicar_grava(capsys, semestre_neutro):
    codigo, saida = _rodar(capsys, "perfil", "criar", "--raiz", str(semestre_neutro),
                           "--id", "faculdade-x", "--instituicao", "Faculdade X", "--cor", "1F3A5F")
    assert codigo == 0 and saida["proposta"]
    assert "2027-1" in saida["mensagem"] and "2 disciplinas" in saida["mensagem"]
    assert not contem_termo_tecnico(saida["mensagem"])
    assert not (pasta_perfis_usuario() / "faculdade-x.yaml").exists()
    assert _rodar(capsys, "aplicar", saida["proposta"]["id"])[0] == 0
    assert carregar_perfil("faculdade-x").slides.paleta["principal"] == "1F3A5F"


def test_criar_de_novo_substitui_e_desfazer_volta(capsys, semestre_neutro):
    base = ["perfil", "criar", "--raiz", str(semestre_neutro), "--id", "fx"]
    _, primeira = _rodar(capsys, *base, "--instituicao", "Antes")
    _rodar(capsys, "aplicar", primeira["proposta"]["id"])
    _, segunda = _rodar(capsys, *base, "--instituicao", "Depois")
    assert segunda["proposta"]["itens"][0]["tipo"] == "substituir"
    _rodar(capsys, "aplicar", segunda["proposta"]["id"])
    assert carregar_perfil("fx").instituicao == "Depois"
    _rodar(capsys, "desfazer")
    assert carregar_perfil("fx").instituicao == "Antes"


def test_importar_valida(capsys, tmp_path):
    from testes.unidade.test_perfil import _v1
    documento = _v1()
    documento["perfil"]["id"] = "colega"
    arquivo = tmp_path / "colega.yaml"
    arquivo.write_text(esquemas.para_yaml(documento), encoding="utf-8")
    codigo, saida = _rodar(capsys, "perfil", "importar", "--arquivo", str(arquivo))
    assert codigo == 0 and saida["proposta"]["itens"][0]["destino"] == "colega.yaml"
    del documento["perfil"]["instituicao"]
    arquivo.write_text(esquemas.para_yaml(documento), encoding="utf-8")
    codigo, saida = _rodar(capsys, "perfil", "importar", "--arquivo", str(arquivo))
    assert codigo == 1 and "Falta o nome da instituição." in saida["mensagem"]


def test_listar_mostra_o_em_uso(capsys):
    codigo, saida = _rodar(capsys, "perfil", "listar")
    assert codigo == 0
    assert saida["dados"]["em_uso"] == "neutro"
    assert {"fasoft", "neutro"} <= set(saida["dados"]["perfis"])


def test_criar_com_id_invalido(capsys, semestre_neutro):
    codigo, saida = _rodar(capsys, "perfil", "criar", "--raiz", str(semestre_neutro),
                           "--id", "Minha Faculdade", "--instituicao", "X")
    assert codigo == 1 and "letras minúsculas" in saida["mensagem"]
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `.venv/Scripts/python -m pytest testes/unidade/test_comando_perfil.py -v`
Expected: FAIL (comando desconhecido; `argparse` sai com 2).

- [ ] **Step 3: Implementar em `acad/comandos/perfil.py`**

```python
from acad.perfil.inferir import inferir_perfil
from acad.perfil.perfil import ID_PERFIL, carregar_perfil, pasta_perfis_usuario, perfis_disponiveis
from acad.perfil.validar import validar_perfil_ou_falhar


def _checar_id(id: str) -> None:
    if not ID_PERFIL.match(id):
        raise ErroAcad("perfil-invalido", "O nome do perfil só pode ter letras minúsculas, números e traços.",
                       id, saida=1)


def _propor_perfil(documento: dict, resumo: str) -> dict:
    validar_perfil_ou_falhar(documento)
    pasta = pasta_perfis_usuario()
    pasta.mkdir(parents=True, exist_ok=True)
    id = documento["perfil"]["id"]
    tipo = "substituir" if (pasta / f"{id}.yaml").exists() else "criar"
    return criar_proposta(pasta, [Operacao(tipo, f"{id}.yaml", esquemas.para_yaml(documento).encode("utf-8"),
                                           "perfil da instituição")], resumo)


@registrar("perfil criar", "Monta o perfil da instituição a partir da pasta do semestre")
def _perfil_criar(parser):
    parser.add_argument("--raiz", required=True)
    parser.add_argument("--id", required=True)
    parser.add_argument("--instituicao", required=True)
    parser.add_argument("--cor")
    parser.add_argument("--rodape", action="append")
    parser.add_argument("--local")

    def executar(args) -> Resultado:
        _checar_id(args.id)
        raiz = Path(args.raiz)
        if not raiz.is_dir():
            raise ErroAcad("raiz-nao-encontrada", "Não encontrei a pasta do semestre.")
        documento, resumo = inferir_perfil(raiz, args.id, args.instituicao, args.cor, args.rodape, args.local)
        proposta = _propor_perfil(documento, "Confira o perfil da instituição antes de guardar.")
        mensagem = (f"Reconheci o semestre {resumo['ano']}-{resumo['periodo']} com "
                    f"{len(resumo['disciplinas'])} disciplinas e preparei o perfil da {args.instituicao}. "
                    "Posso guardar?")
        avisos = ([f"Vou considerar estas pastas da disciplina, que ainda não existem: "
                   f"{', '.join(resumo['papeis_criados'])}."] if resumo["papeis_criados"] else [])
        return Resultado(ok=True, mensagem=mensagem, dados={"resumo": resumo}, avisos=avisos, proposta=proposta)

    return executar


@registrar("perfil importar", "Traz o perfil da instituição recebido de um colega")
def _perfil_importar(parser):
    parser.add_argument("--arquivo", required=True)

    def executar(args) -> Resultado:
        try:
            documento = esquemas.carregar_yaml(Path(args.arquivo).read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as erro:
            raise ErroAcad("arquivo-ilegivel", "Não consegui abrir o arquivo do perfil.", str(erro)) from erro
        validar_perfil_ou_falhar(documento)
        _checar_id(documento["perfil"]["id"])
        proposta = _propor_perfil(documento, "Confira o perfil recebido antes de guardar.")
        return Resultado(ok=True, mensagem=f"O perfil da {documento['perfil']['instituicao']} está certo. Posso guardar?",
                         proposta=proposta)

    return executar


@registrar("perfil listar", "Mostra os perfis de instituição disponíveis")
def _perfil_listar(parser):
    def executar(args) -> Resultado:
        em_uso = contexto.perfil().id
        perfis = perfis_disponiveis()
        nomes = ", ".join(perfis)
        return Resultado(ok=True, mensagem=f"Perfis disponíveis: {nomes}. Em uso: {em_uso}.",
                         dados={"perfis": perfis, "em_uso": em_uso})

    return executar
```

Se `esquemas.carregar_yaml` levantar `yaml.YAMLError` para arquivo malformado, capture também e use a mesma mensagem. `aplicar` e `desfazer` recebem `contexto.perfil()`; a substituição vai para `perfis/<pasta_arquivo do perfil em uso>/` — esperado (spec P4).

- [ ] **Step 4: Rodar**

Run: `.venv/Scripts/python -m pytest testes/unidade/test_comando_perfil.py testes/unidade/test_cli.py testes/integracao/test_mcp.py -v` e `.venv/Scripts/python -m pytest -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add acad/comandos/perfil.py acad/mcp.py testes/unidade/test_comando_perfil.py
git commit -m "feat: comandos para criar, importar e listar perfis de instituição"
```

---

### Task 11: Skills e documentação do professor

**Files:**
- Modify: `skills/organizador-academico/SKILL.md`
- Modify: `skills/usando-agente-academico/SKILL.md`
- Modify: `INSTALAR.md` e `README.md` só onde disserem que o plugin é da UniRV/Fasoft (confira com `grep -n "Fasoft\|UniRV" README.md INSTALAR.md`)
- Run: `scripts/sincronizar-skills.py`
- Test: `testes/unidade/test_skills.py`, `testes/unidade/test_documentacao.py`, `testes/unidade/test_agents_md.py`

- [ ] **Step 1: Texto da skill organizadora** — antes do passo atual de `acad iniciar`, acrescente, no tom das linhas vizinhas:

```markdown
1. Pergunte de qual instituição é o professor. Rode `acad perfil listar`. Se já houver um perfil dela, use esse.
2. Se não houver, peça a pasta do semestre e rode `acad perfil criar --raiz <pasta> --id <nome-curto> --instituicao "<nome>"`
   (com `--cor`, `--rodape` e `--local` só se o professor disser a cor e os textos da capa). Mostre o resumo e, com o "sim", rode `acad aplicar <id>`.
   Se um colega mandou o perfil da instituição, use `acad perfil importar --arquivo <arquivo>`.
3. Rode `acad iniciar … --perfil <nome-curto>` e, com o "sim", repita com `--confirmar`.
```

Renumere os passos seguintes. Em `usando-agente-academico`, acrescente uma linha: "Funciona com qualquer instituição: o organizador monta o perfil a partir da pasta do professor; sem perfil, os slides saem sem marca."

- [ ] **Step 2: Sincronizar e testar**

Run: `.venv/Scripts/python scripts/sincronizar-skills.py` e `.venv/Scripts/python -m pytest testes/unidade/test_skills.py testes/unidade/test_documentacao.py testes/unidade/test_agents_md.py -v`
Expected: PASS. Se algum teste fixar trecho de texto da skill, ajuste o texto da skill, não o teste.

- [ ] **Step 3: Commit**

```bash
git add skills scripts README.md INSTALAR.md
git commit -m "docs: skills orientam a criar o perfil da instituição"
```

---

### Task 12: Ponta a ponta — perfil neutro de outra instituição

**Files:**
- Create: `testes/integracao/test_outra_instituicao.py`

**Interfaces:**
- Consumes: todos os comandos CLI (`perfil criar`, `aplicar`, `iniciar`, `perfil detectar`, `disciplina criar`, `validar`, `gerar aula`, `cronograma consultar`) e a fixture `semestre_neutro`.

- [ ] **Step 1: Escrever o teste**

```python
# testes/integracao/test_outra_instituicao.py
import io
import json
import zipfile

from pptx import Presentation

from acad.cli import main
from acad.mensagens import contem_termo_tecnico

MARCAS = ("UniRV", "RIO VERDE", "Rio Verde", "Engenharia de Software", "Fasoft")


def _rodar(capsys, *argumentos):
    codigo = main([*argumentos, "--json"])
    saida = json.loads(capsys.readouterr().out)
    assert not contem_termo_tecnico(saida["mensagem"]), saida["mensagem"]
    return codigo, saida


def test_professor_de_outra_instituicao(capsys, semestre_neutro, tmp_path):
    raiz = str(semestre_neutro)
    codigo, saida = _rodar(capsys, "perfil", "criar", "--raiz", raiz, "--id", "faculdade-x",
                           "--instituicao", "Faculdade X", "--cor", "7A1F2B", "--rodape", "FACULDADE X")
    assert codigo == 0
    assert _rodar(capsys, "aplicar", saida["proposta"]["id"])[0] == 0
    assert _rodar(capsys, "iniciar", "2027-1", "--raiz", raiz, "--perfil", "faculdade-x", "--confirmar")[0] == 0

    codigo, saida = _rodar(capsys, "perfil", "detectar", "--raiz", raiz)
    assert codigo == 0 and len(saida["dados"]["disciplinas"]) == 2

    codigo, saida = _rodar(capsys, "disciplina", "criar", "ALG", "--pasta", "Algoritmos", "--nome", "Algoritmos",
                           "--carga", "60", "--unidade", "hora_relogio")
    assert codigo == 0 and saida["dados"]["disciplina"]["semestre"] == "2027-1"
    assert _rodar(capsys, "aplicar", saida["proposta"]["id"])[0] == 0

    codigo, saida = _rodar(capsys, "validar", "--raiz", raiz)
    assert codigo == 0, saida
    assert not [e for e in saida.get("erros", []) if "pasta" in e.get("codigo", "")]

    planejamento = semestre_neutro / "Algoritmos" / "planejamento"
    (planejamento / "aulas.yaml").write_text(
        "versao_esquema: 1\ndisciplina: ALG\naulas:\n- id: Aula 01\n  tema: Grafos\n  status: planejada\n"
        "  objetivos: []\n  prerequisitos: []\n  encontros_necessarios: 1\n", encoding="utf-8")
    conteudo = tmp_path / "conteudo.json"
    conteudo.write_text(json.dumps({
        "tema": "Grafos", "professor": "Profa. Exemplo",
        "roteiro": {"objetivo": "Conhecer grafos", "blocos": [{"titulo": "Grafos", "minutos": 50, "texto": "…"}]},
        "slides": {"slides": [
            {"tipo": "capa", "titulo": "Grafos"},
            {"tipo": "topicos", "titulo": "Ideias", "lead": "O essencial", "itens": ["Vértices", "Arestas"]},
        ]},
    }, ensure_ascii=False), encoding="utf-8")
    codigo, saida = _rodar(capsys, "gerar", "aula", "ALG", "--aula", "01", "--conteudo", str(conteudo))
    assert codigo == 0, saida
    assert not any("logotipos" in aviso for aviso in saida["avisos"])
    assert _rodar(capsys, "aplicar", saida["proposta"]["id"])[0] == 0

    pptx = semestre_neutro / "Algoritmos" / "aulas" / "Aula 01 - Grafos.pptx"
    dados = pptx.read_bytes()
    apresentacao = Presentation(io.BytesIO(dados))
    texto = " ".join(s.text_frame.text for slide in apresentacao.slides for s in slide.shapes if s.has_text_frame)
    assert "FACULDADE X" in texto
    assert not any(marca in texto for marca in MARCAS)
    assert not [s for slide in apresentacao.slides for s in slide.shapes if s.shape_type == 13]
    with zipfile.ZipFile(io.BytesIO(dados)) as pacote:
        xml = b"".join(pacote.read(nome) for nome in pacote.namelist() if nome.endswith(".xml"))
    assert b"015537" not in xml and b"7A1F2B" in xml

    codigo, saida = _rodar(capsys, "cronograma", "consultar", "--raiz",
                           str(semestre_neutro / "Algoritmos" / "aulas"), "--data", "2027-03-01")
    assert codigo == 0
```

Ajustes permitidos ao escrever (confira a forma real antes): o argumento `--aula` de `gerar aula` aceita `01` ou `Aula 01` — use o que os testes de `test_gerar_aula.py`/`test_cli.py` usam; o campo de `validar` que traz os achados (pode ser `dados["achados"]` em vez de `erros`) — confira em `acad/comandos/validar.py` e troque a asserção para "nenhum achado de nível `erro` cujo código comece por `pasta-` ou `nome-`". Não afrouxe as asserções de marca, figura e cor.

- [ ] **Step 2: Rodar e corrigir o que faltar**

Run: `.venv/Scripts/python -m pytest testes/integracao/test_outra_instituicao.py -v`
Expected: PASS. Se falhar por um literal Fasoft que escapou da Tarefa 7, corrija no código (com teste unitário próprio na tarefa afetada) e registre no commit.

- [ ] **Step 3: Commit**

```bash
git add testes/integracao/test_outra_instituicao.py
git commit -m "test: ponta a ponta de professor de outra instituição com perfil próprio"
```

---

### Task 13: Verificação final e critérios de aceite

- [ ] **Step 1: Suíte completa**

Run: `.venv/Scripts/python -m pytest -q` e `.venv/Scripts/python -m pytest -q -m "drive or hosts or rede or latex"`
Expected: verde; número de testes = linha de base + novos. Copie as duas últimas linhas da saída para o relatório.

- [ ] **Step 2: Nenhuma marca no código executável (aceite 3)**

Run: `grep -rnE "UniRV|Rio Verde|RIO VERDE|fasoft|Fasoft" acad --include=*.py`
Expected: só docstrings/comentários históricos e a chave `raiz_fasoft` em `acad/perfil/detectar.py`. Qualquer outro valor: mova para `fasoft.yaml`.

- [ ] **Step 3: Compatibilidade**

Run: `.venv/Scripts/python -m pytest testes/unidade/test_compat_fasoft.py testes/unidade/test_perfil.py -v`
Expected: PASS. Confira com `git diff d944cbe -- testes/esperados/slides-fasoft.json` que a referência não foi alterada desde a Tarefa 1 (`git log --format=%h -- testes/esperados/slides-fasoft.json` mostra um único commit).

- [ ] **Step 4: Manifestos e versão**

Run: `.venv/Scripts/python scripts/validar-manifestos.py`
Expected: sem erro.

- [ ] **Step 5: Spec atualizada** — se algo divergiu da spec durante a execução (nome de campo, mensagem), atualize `docs/superpowers/specs/2026-10-22-librarius-portabilidade-design.md` no mesmo commit.

- [ ] **Step 6: Commit (se houver ajuste)**

```bash
git add -A docs acad testes
git commit -m "chore: verificação final da portabilidade"
```
