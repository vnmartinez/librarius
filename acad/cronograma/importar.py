from __future__ import annotations

from collections import Counter

from acad.cronograma.classificar import tipo_linha
from acad.cronograma.planilha import LinhaCronograma
from acad.encontros.gerar import Encontro


def importar_cronograma(linhas: list[LinhaCronograma], turma: dict,
                        disciplina: str) -> tuple[list[Encontro], dict]:
    encontros = []
    aulas_por_id = {}
    contagem = Counter()
    for linha in linhas:
        if linha.data is None:
            continue
        horario = next((item for item in turma["horarios"]
                        if item["dia_semana"] == linha.data.isoweekday()), turma["horarios"][0])
        tipo = tipo_linha(linha.aula, linha.topico)
        aulas = []
        status = "cancelado" if tipo == "sem-aula" else "previsto"
        funcao = "avaliacao" if tipo == "avaliacao" else "conteudo"
        if tipo == "aula" and linha.aula_num:
            id_aula = f"Aula {linha.aula_num}"
            aulas = [id_aula]
            if id_aula not in aulas_por_id:
                aulas_por_id[id_aula] = {
                    "id": id_aula, "tema": linha.topico, "status": "planejada",
                    "objetivos": [], "prerequisitos": [], "encontros_necessarios": 0,
                }
            aulas_por_id[id_aula]["encontros_necessarios"] += 1
        encontros.append(Encontro(
            "", linha.data, horario["inicio"], horario["fim"], status, aulas,
            funcao, "planilha", linha.topico if status == "cancelado" else None,
        ))
        contagem[tipo] += 1
    encontros.sort(key=lambda encontro: (encontro.data, encontro.inicio))
    largura = 3 if len(encontros) > 99 else 2
    for indice, encontro in enumerate(encontros, 1):
        encontro.id = f"E{indice:0{largura}d}"
    documento = {"versao_esquema": 1, "disciplina": disciplina,
                 "aulas": list(aulas_por_id.values())}
    return encontros, documento
