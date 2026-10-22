from __future__ import annotations

import hashlib
from collections import defaultdict
from datetime import date, datetime

from acad import __version__, contexto, esquemas
from acad.arquivos.escrita import Operacao, criar_proposta
from acad.cli import registrar
from acad.planejamento.arquivos import caminho, documento_encontros, ler_aulas, ler_avaliacoes, ler_encontros
from acad.planejamento.distribuir import distribuir
from acad.planejamento.replanejar import cancelar, diff, resumo_diff
from acad.saida import Resultado


def _hash(conteudo: bytes) -> str:
    return "sha256:" + hashlib.sha256(conteudo).hexdigest()


@registrar("plano distribuir", "Distribui as aulas nos encontros da turma")
def _distribuir(parser):
    parser.add_argument("disciplina")
    parser.add_argument("--turma", required=True)
    parser.add_argument("--raiz")

    def executar(args) -> Resultado:
        semestre = contexto.raiz_semestre(args)
        ws = contexto.workspace(semestre)
        disciplina = contexto.localizar_disciplina(ws, semestre, args.disciplina)
        aulas = ler_aulas(ws, disciplina)["aulas"]
        anteriores = ler_encontros(ws, disciplina, args.turma)
        encontros, sobra = distribuir(aulas, anteriores)
        origem = caminho(disciplina, f"encontros-{args.turma}.yaml")
        arquivo = semestre / origem
        entradas = {origem: _hash(ws.ler_bytes(arquivo))} if ws.existe(arquivo) else {}
        documento = documento_encontros(encontros, entradas, __version__, datetime.now().astimezone())
        esquemas.validar_ou_falhar("encontro", documento)
        operacao = Operacao("substituir" if ws.existe(arquivo) else "criar", origem,
                            esquemas.para_yaml(documento).encode("utf-8"), "encontros distribuídos")
        proposta = criar_proposta(semestre, [operacao], "Vou distribuir as aulas pelos encontros.")
        datas = defaultdict(list)
        for encontro in encontros:
            for id_aula in encontro.aulas:
                datas[id_aula].append(encontro.data.strftime("%d/%m"))
        descricoes = [f"{id_aula} → {' e '.join(dias)}" for id_aula, dias in datas.items()]
        mensagem = "; ".join(descricoes) if descricoes else "Nenhuma aula foi distribuída."
        avisos = ["Aulas sem encontro: " + ", ".join(sobra) + "."] if sobra else []
        return Resultado(ok=True, mensagem=mensagem, avisos=avisos,
                         dados={"encontros": documento, "sem_encontro": sobra}, proposta=proposta)

    return executar


@registrar("plano replanejar", "Mostra o impacto de cancelar um encontro")
def _replanejar(parser):
    parser.add_argument("disciplina")
    parser.add_argument("--turma", required=True)
    parser.add_argument("--cancelar", required=True)
    parser.add_argument("--motivo", default="aula cancelada")
    parser.add_argument("--raiz")

    def executar(args) -> Resultado:
        semestre = contexto.raiz_semestre(args)
        ws = contexto.workspace(semestre)
        disciplina = contexto.localizar_disciplina(ws, semestre, args.disciplina)
        aulas = ler_aulas(ws, disciplina)["aulas"]
        anteriores = ler_encontros(ws, disciplina, args.turma)
        cancelados = cancelar(anteriores, date.fromisoformat(args.cancelar), args.motivo)
        encontros, sobra = distribuir(aulas, cancelados)
        relatorio = diff(anteriores, encontros, ler_avaliacoes(ws, disciplina))
        for id_aula in sobra:
            if id_aula not in relatorio["sem_encontro"]:
                relatorio["sem_encontro"].append(id_aula)
        origem = caminho(disciplina, f"encontros-{args.turma}.yaml")
        arquivo = semestre / origem
        entradas = {origem: _hash(ws.ler_bytes(arquivo))} if ws.existe(arquivo) else {}
        documento = documento_encontros(encontros, entradas, __version__, datetime.now().astimezone())
        esquemas.validar_ou_falhar("encontro", documento)
        operacao = Operacao("substituir", origem, esquemas.para_yaml(documento).encode("utf-8"),
                            "encontros replanejados")
        proposta = criar_proposta(semestre, [operacao], "Confira o que muda antes de aprovar.")
        return Resultado(ok=True, mensagem=resumo_diff(relatorio),
                         dados={"diff": relatorio, "encontros": documento}, proposta=proposta)

    return executar
