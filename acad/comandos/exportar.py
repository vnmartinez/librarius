from __future__ import annotations

from acad import contexto
from acad.arquivos.escrita import Operacao, criar_proposta
from acad.cli import registrar
from acad.exportadores.ics import exportar_ics
from acad.planejamento.arquivos import caminho, ler_aulas, ler_encontros, ler_turma
from acad.saida import Resultado


@registrar("exportar ics", "Prepara o cronograma para uma agenda")
def _ics(parser):
    parser.add_argument("disciplina")
    parser.add_argument("--turma", required=True)
    parser.add_argument("--raiz")

    def executar(args) -> Resultado:
        semestre = contexto.raiz_semestre(args)
        ws = contexto.workspace(semestre)
        disc = contexto.localizar_disciplina(ws, semestre, args.disciplina)
        nome = disc.name.split(" - ", 1)[1]
        if nome.endswith("Período"):
            nome = nome.rsplit(" - ", 1)[0]
        turma = ler_turma(ws, disc, args.turma)
        encontros = ler_encontros(ws, disc, args.turma)
        aulas = {aula["id"]: aula["tema"] for aula in ler_aulas(ws, disc)["aulas"]}
        conteudo = exportar_ics(encontros, nome, args.turma, turma["fuso"], aulas)
        destino = caminho(disc, f"Cronograma - {nome} - {args.turma}.ics")
        tipo = "substituir" if ws.existe(semestre / destino) else "criar"
        proposta = criar_proposta(semestre, [Operacao(tipo, destino, conteudo, "agenda da turma")],
                                 "Confira o arquivo de agenda.")
        return Resultado(ok=True, mensagem=f"Preparei a agenda da turma {args.turma}.", proposta=proposta)

    return executar
