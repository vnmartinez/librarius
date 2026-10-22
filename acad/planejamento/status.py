from __future__ import annotations

from copy import deepcopy
from datetime import datetime

from acad.erros import ErroAcad


TRANSICOES = {
    "planejada": {"rascunho"},
    "rascunho": {"revisada", "planejada"},
    "revisada": {"aprovada", "rascunho"},
    "aprovada": {"ministrada"},
    "ministrada": set(),
}


def mudar_status(aula: dict, novo: str, agora: datetime,
                 encontro: str | None = None) -> dict:
    atual = aula.get("status", "")
    if novo not in TRANSICOES.get(atual, set()):
        if atual == "rascunho" and novo == "aprovada":
            mensagem = "Uma aula em rascunho precisa ser revisada antes de ser aprovada."
        else:
            mensagem = f"Não posso mudar uma aula em {atual} diretamente para {novo}."
        raise ErroAcad("transicao-invalida", mensagem)
    if novo == "ministrada" and not encontro:
        raise ErroAcad("encontro-obrigatorio", "Informe em qual encontro a aula foi ministrada.")
    alterada = deepcopy(aula)
    alterada["status"] = novo
    if novo == "aprovada":
        if not alterada.get("manifesto"):
            raise ErroAcad("manifesto-ausente", "Falta gerar os materiais da aula antes de aprová-la.")
        alterada["manifesto"]["aprovado"] = True
        alterada["manifesto"]["aprovado_em"] = agora.isoformat()
    if novo == "ministrada":
        registros = alterada.setdefault("ministrada_em", [])
        if encontro not in registros:
            registros.append(encontro)
    return alterada
