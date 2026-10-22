from __future__ import annotations

from acad import contexto
from acad.cli import registrar
from acad.saida import Resultado
from acad.validacao.validar import resumo_validacao, validar_semestre


@registrar("validar", "Confere a organização e o planejamento do semestre")
def _validar(parser):
    parser.add_argument("disciplina", nargs="?")
    parser.add_argument("--raiz")

    def executar(args) -> Resultado:
        semestre = contexto.raiz_semestre(args)
        ws = contexto.workspace(semestre)
        disciplina = (contexto.localizar_disciplina(ws, semestre, args.disciplina)
                      if args.disciplina else None)
        achados = validar_semestre(ws, semestre, contexto.perfil(), disciplina)
        return Resultado(ok=not any(a.nivel == "erro" for a in achados),
                         mensagem=resumo_validacao(achados, len(ws.protegidas)),
                         dados={"achados": [a.para_dict() for a in achados],
                                "pastas_protegidas": len(ws.protegidas)})

    return executar
