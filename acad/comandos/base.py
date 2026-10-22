from __future__ import annotations

import importlib
import sys
from pathlib import Path

from acad import contexto, mensagens
from acad.arquivos.escrita import aplicar, desfazer
from acad.cli import ler_data, registrar
import acad.cronograma.consulta as consulta
from acad.erros import ErroAcad
from acad.saida import Resultado


@registrar("ambiente verificar", "Confere se o assistente pode trabalhar")
def _ambiente(parser):
    def executar(args) -> Resultado:
        faltando = []
        for nome in ("yaml", "jsonschema", "openpyxl"):
            try:
                importlib.import_module(nome)
            except ImportError:
                faltando.append(nome)
        if sys.version_info < (3, 11):
            faltando.append("Python 3.11")
        configuracao = contexto.carregar_configuracao()
        raiz = (configuracao or {}).get("raiz_workspace")
        if raiz and not Path(raiz).is_dir():
            faltando.append("pasta dos materiais")
        return Resultado(ok=not faltando,
                         mensagem="O assistente está pronto para trabalhar." if not faltando
                         else "Falta preparar alguns itens para começar.",
                         dados={"python": sys.version.split()[0], "faltando": faltando})
    return executar


@registrar("cronograma consultar", "Mostra as aulas de um dia e o que já está pronto")
def _consultar(parser):
    parser.add_argument("--data")
    parser.add_argument("--raiz")

    def executar(args) -> Resultado:
        alvo = ler_data(args.data)
        raiz = consulta.encontrar_raiz(Path(args.raiz) if args.raiz else contexto.raiz_padrao_consulta())
        if raiz is None:
            raise ErroAcad("raiz-nao-encontrada", mensagens.msg("raiz-nao-encontrada"), saida=3)
        resultado = consulta.consultar(raiz, alvo, contexto.perfil().exclusao)
        return Resultado(ok=True, mensagem=consulta.resumo_texto(resultado), dados=resultado)
    return executar


@registrar("aplicar", "Aplica uma proposta aprovada")
def _aplicar(parser):
    parser.add_argument("id")

    def executar(args) -> Resultado:
        arquivos = aplicar(args.id, contexto.perfil())
        return Resultado(ok=True, mensagem=mensagens.msg("proposta-aplicada"), dados={"arquivos": arquivos})
    return executar


@registrar("desfazer", "Desfaz a última alteração")
def _desfazer(parser):
    def executar(args) -> Resultado:
        arquivos = desfazer(contexto.perfil())
        return Resultado(ok=True, mensagem=mensagens.msg("desfeito") if arquivos
                         else mensagens.msg("nada-para-desfazer"), dados={"arquivos": arquivos})
    return executar
