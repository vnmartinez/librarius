from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from acad import esquemas
from acad.encontros.gerar import Encontro


def _planejamento(disciplina: Path) -> Path:
    from acad import contexto
    return Path(disciplina) / contexto.perfil().pasta("planejamento")


def caminho(disciplina: Path, nome: str) -> str:
    from acad import contexto
    return f"{Path(disciplina).name}/{contexto.perfil().pasta('planejamento')}/{nome}"


def ler_turma(ws, disciplina: Path, id: str) -> dict:
    documento = esquemas.carregar_yaml(ws.ler_texto(_planejamento(disciplina) / f"turma-{id}.yaml"))
    esquemas.validar_ou_falhar("turma", documento)
    return documento["turma"]


def ler_encontros(ws, disciplina: Path, id: str) -> list[Encontro]:
    arquivo = _planejamento(disciplina) / f"encontros-{id}.yaml"
    if not ws.existe(arquivo):
        return []
    documento = esquemas.carregar_yaml(ws.ler_texto(arquivo))
    esquemas.validar_ou_falhar("encontro", documento)
    return [Encontro(
        item["id"], date.fromisoformat(item["data"]), item["inicio"], item["fim"],
        item["status"], list(item["aulas"]), item["funcao"], item["origem"], item.get("motivo"),
    ) for item in documento["encontros"]]


def documento_encontros(encontros: list[Encontro], entradas: dict[str, str],
                        versao: str, agora: datetime) -> dict:
    registros = []
    for encontro in encontros:
        item = {
            "id": encontro.id, "data": encontro.data.isoformat(),
            "inicio": encontro.inicio, "fim": encontro.fim, "status": encontro.status,
            "aulas": encontro.aulas, "funcao": encontro.funcao, "origem": encontro.origem,
        }
        if encontro.motivo:
            item["motivo"] = encontro.motivo
        registros.append(item)
    return {
        "versao_esquema": 1, "gerado_por": f"acad {versao}",
        "gerado_em": agora.isoformat(), "entradas": entradas, "encontros": registros,
    }


def ler_disciplina(ws, disciplina: Path) -> dict:
    documento = esquemas.carregar_yaml(ws.ler_texto(_planejamento(disciplina) / "disciplina.yaml"))
    esquemas.validar_ou_falhar("disciplina", documento)
    return documento["disciplina"]


def ler_aulas(ws, disciplina: Path) -> dict:
    arquivo = _planejamento(disciplina) / "aulas.yaml"
    if not ws.existe(arquivo):
        codigo = ""
        disciplina_doc = _planejamento(disciplina) / "disciplina.yaml"
        if ws.existe(disciplina_doc):
            codigo = ler_disciplina(ws, disciplina)["codigo"]
        return {"versao_esquema": 1, "disciplina": codigo, "aulas": []}
    documento = esquemas.carregar_yaml(ws.ler_texto(arquivo))
    esquemas.validar_ou_falhar("aula", documento)
    return documento


def ler_avaliacoes(ws, disciplina: Path) -> list[dict]:
    pasta = _planejamento(disciplina) / "avaliacoes"
    if not ws.existe(pasta):
        return []
    saida = []
    for arquivo in ws.listar(pasta):
        if arquivo.suffix.lower() == ".yaml":
            documento = esquemas.carregar_yaml(ws.ler_texto(arquivo))
            esquemas.validar_ou_falhar("avaliacao", documento)
            saida.append(documento["avaliacao"])
    return saida
