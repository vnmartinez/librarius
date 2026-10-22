from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from acad import contexto
from acad.arquivos.escrita import criar_proposta
from acad.cli import registrar
from acad.erros import ErroAcad
from acad.geracao.aula import planejar_aula
from acad.geracao.slides import obter_gerador
from acad.saida import Resultado


@registrar("gerar aula", "Prepara o roteiro e os materiais de uma aula")
def _gerar_aula(parser):
    parser.add_argument("disciplina")
    parser.add_argument("--aula", required=True)
    parser.add_argument("--conteudo", required=True)
    parser.add_argument("--revisar", action="store_true")
    parser.add_argument("--raiz")

    def executar(args) -> Resultado:
        semestre = contexto.raiz_semestre(args)
        ws = contexto.workspace(semestre)
        disc = contexto.localizar_disciplina(ws, semestre, args.disciplina)
        try:
            conteudo = json.loads(Path(args.conteudo).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as erro:
            raise ErroAcad("conteudo-invalido", "Não consegui ler o arquivo com o conteúdo da aula.", str(erro)) from erro
        operacoes, avisos = planejar_aula(ws, semestre, disc, args.aula, conteudo,
                                          obter_gerador(), datetime.now().astimezone(), args.revisar)
        proposta = criar_proposta(semestre, operacoes, "Confira os materiais da aula antes de aplicar.")
        quantidade = len(operacoes) - 1
        return Resultado(ok=True,
                         mensagem=f"Vou criar {quantidade} arquivos para a aula e atualizar o plano da disciplina.",
                         avisos=avisos, proposta=proposta)

    return executar
