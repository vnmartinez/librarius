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
    documento = esquemas.carregar_yaml(texto)
    esquemas.validar_ou_falhar("perfil", documento)
    perfil = documento["perfil"]
    nomes = perfil["nomenclatura"]
    return Perfil(
        id=perfil["id"], instituicao=perfil["instituicao"],
        disciplina_pasta=re.compile(perfil["disciplina_pasta"]),
        subpastas_disciplina=tuple(perfil["subpastas_disciplina"]),
        pasta_arquivo=perfil["pasta_arquivo"],
        pasta_avaliacoes=re.compile(perfil["pasta_avaliacoes"]),
        pasta_modelos=re.compile(perfil["pasta_modelos"]),
        etapas_avaliacao=tuple(perfil["etapas_avaliacao"]),
        re_aula=re.compile(nomes["aula"]), re_lista=re.compile(nomes["lista"]),
        re_pasta=re.compile(nomes["pasta"]),
        sufixos_proibidos=tuple(re.compile(regra) for regra in nomes["sufixos_proibidos"]),
        unidade_carga=perfil["carga_horaria"]["unidade"],
        minutos_hora_aula=perfil["carga_horaria"]["minutos_hora_aula"],
        exclusao=tuple(perfil["exclusao"]),
    )
