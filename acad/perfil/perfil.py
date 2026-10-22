from __future__ import annotations

import re
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

from acad import esquemas
from acad.perfil.padroes import ESTRUTURA_V1


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
    re_semestre: re.Pattern
    periodos: dict[str, int]
    re_administracao: re.Pattern
    papeis: dict[str, str]
    modelo_slides: str | None
    modelo_prova: str | None

    def pasta(self, papel: str) -> str:
        return self.papeis[papel]

    def semestre_de(self, pasta: Path) -> tuple[int, int] | None:
        pasta = Path(pasta)
        alvo = f"{pasta.parent.name}/{pasta.name}" if "/" in self.re_semestre.pattern else pasta.name
        correspondencia = self.re_semestre.fullmatch(alvo)
        if not correspondencia:
            return None
        texto = correspondencia["periodo"]
        periodo = self.periodos.get(texto) if self.periodos else int(texto)
        return (int(correspondencia["ano"]), periodo) if periodo in (1, 2) else None

    def base_semestre(self, pasta: Path) -> Path:
        pasta = Path(pasta)
        return pasta.parent.parent if "/" in self.re_semestre.pattern else pasta.parent

    def partes_disciplina(self, nome: str) -> dict | None:
        correspondencia = self.disciplina_pasta.fullmatch(nome)
        if not correspondencia:
            return None
        grupos = correspondencia.groupdict()
        return {chave: grupos.get(chave) for chave in ("num", "nome", "periodo")}


def perfil_de_documento(documento: dict) -> Perfil:
    perfil = documento["perfil"]
    nomes = perfil["nomenclatura"]
    estrutura_v2 = perfil.get("estrutura", {})
    estrutura = {**ESTRUTURA_V1, **estrutura_v2}
    papeis = {**ESTRUTURA_V1["papeis"], "arquivo": perfil.get("pasta_arquivo", ESTRUTURA_V1["papeis"]["arquivo"]),
              **estrutura_v2.get("papeis", {})}
    modelos = perfil.get("modelos", {})
    return Perfil(
        id=perfil["id"], instituicao=perfil["instituicao"],
        disciplina_pasta=re.compile(perfil["disciplina_pasta"]),
        subpastas_disciplina=tuple(perfil["subpastas_disciplina"]),
        pasta_arquivo=perfil.get("pasta_arquivo", papeis["arquivo"]),
        pasta_avaliacoes=re.compile(perfil["pasta_avaliacoes"]),
        pasta_modelos=re.compile(perfil["pasta_modelos"]),
        etapas_avaliacao=tuple(perfil["etapas_avaliacao"]),
        re_aula=re.compile(nomes["aula"]), re_lista=re.compile(nomes["lista"]),
        re_pasta=re.compile(nomes["pasta"]),
        sufixos_proibidos=tuple(re.compile(regra) for regra in nomes["sufixos_proibidos"]),
        unidade_carga=perfil["carga_horaria"]["unidade"],
        minutos_hora_aula=perfil["carga_horaria"]["minutos_hora_aula"],
        exclusao=tuple(perfil["exclusao"]),
        re_semestre=re.compile(estrutura["semestre"]),
        periodos=dict(estrutura_v2.get("periodos", ESTRUTURA_V1["periodos"] if "estrutura" not in perfil else {})),
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
