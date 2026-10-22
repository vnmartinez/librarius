from __future__ import annotations

import hashlib
from collections import Counter
from datetime import datetime

from acad import __version__, contexto, esquemas
from acad.arquivos.escrita import Operacao, criar_proposta
from acad.calendario.modelo import de_documento
from acad.cli import registrar
from acad.encontros.gerar import gerar_encontros
from acad.erros import ErroAcad
from acad.planejamento.arquivos import caminho, documento_encontros, ler_encontros, ler_turma
from acad.saida import Resultado


def _hash(conteudo: bytes) -> str:
    return "sha256:" + hashlib.sha256(conteudo).hexdigest()


@registrar("encontros gerar", "Organiza os encontros de uma turma")
def _gerar(parser):
    parser.add_argument("disciplina")
    parser.add_argument("--turma", required=True)
    parser.add_argument("--raiz")

    def executar(args) -> Resultado:
        semestre = contexto.raiz_semestre(args)
        ws = contexto.workspace(semestre)
        arquivo_calendario = contexto.pasta_administracao(semestre) / "calendario.yaml"
        bytes_calendario = ws.ler_bytes(arquivo_calendario)
        calendario = de_documento(esquemas.carregar_yaml(bytes_calendario.decode("utf-8")))
        if calendario.status != "confirmado":
            raise ErroAcad("calendario-nao-confirmado", "O calendário ainda não foi conferido por você.", saida=1)
        disciplina = contexto.localizar_disciplina(ws, semestre, args.disciplina)
        arquivo_turma = disciplina / contexto.perfil().pasta("planejamento") / f"turma-{args.turma}.yaml"
        turma = ler_turma(ws, disciplina, args.turma)
        anteriores = ler_encontros(ws, disciplina, args.turma)
        encontros = gerar_encontros(calendario, turma, anteriores)
        entradas = {
            f"{arquivo_calendario.relative_to(semestre).as_posix()}": _hash(bytes_calendario),
            caminho(disciplina, f"turma-{args.turma}.yaml"): _hash(ws.ler_bytes(arquivo_turma)),
        }
        documento = documento_encontros(encontros, entradas, __version__, datetime.now().astimezone())
        esquemas.validar_ou_falhar("encontro", documento)
        destino = caminho(disciplina, f"encontros-{args.turma}.yaml")
        tipo = "substituir" if anteriores else "criar"
        proposta = criar_proposta(semestre, [Operacao(tipo, destino,
                                                      esquemas.para_yaml(documento).encode("utf-8"),
                                                      "encontros da turma")],
                                 "Vou organizar os encontros da turma.")
        contagem = Counter(encontro.status for encontro in encontros)
        mensagem = (f"{contagem['previsto']} encontros previstos, "
                    f"{contagem['cancelado']} cancelados por feriado, recesso ou outro motivo. Confira as datas.")
        return Resultado(ok=True, mensagem=mensagem, dados=documento, proposta=proposta)
    return executar
