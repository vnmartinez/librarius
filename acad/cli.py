from __future__ import annotations

import argparse
import sys
import traceback
from datetime import date, datetime
from typing import Callable

from acad import __version__, config, mensagens
from acad.erros import ErroAcad
from acad.saida import Resultado

_COMANDOS: dict[str, tuple[str, Callable]] = {}


def registrar(nome: str, ajuda: str):
    def decorador(declarar: Callable[[argparse.ArgumentParser], Callable]):
        _COMANDOS[nome] = (ajuda, declarar)
        return declarar
    return decorador


def ler_data(texto: str | None) -> date:
    if not texto:
        return date.today()
    for formato in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            pass
    raise ErroAcad("data-invalida", "Não entendi a data. Use dia/mês/ano, por exemplo 28/10/2026.", texto)


def _montar() -> argparse.ArgumentParser:
    raiz = argparse.ArgumentParser(prog="acad", description="Núcleo do Librarius")
    raiz.add_argument("--versao", action="version", version=__version__)
    subcomandos = raiz.add_subparsers(dest="_cmd", required=True)
    grupos: dict[str, argparse._SubParsersAction] = {}
    for nome, (ajuda, declarar) in sorted(_COMANDOS.items()):
        partes = nome.split()
        if len(partes) == 1:
            parser = subcomandos.add_parser(partes[0], help=ajuda)
        else:
            if partes[0] not in grupos:
                grupos[partes[0]] = subcomandos.add_parser(partes[0]).add_subparsers(dest="_sub", required=True)
            parser = grupos[partes[0]].add_parser(partes[1], help=ajuda)
        parser.add_argument("--json", action="store_true")
        parser.set_defaults(_executar=declarar(parser))
    return raiz


def main(argv: list[str] | None = None) -> int:
    from acad import comandos  # noqa: F401

    args = _montar().parse_args(argv)
    try:
        resultado: Resultado = args._executar(args)
        codigo = 0 if resultado.ok else 1
    except ErroAcad as erro:
        config.registrar_detalhe(f"{erro.codigo}: {erro.detalhe_tecnico}")
        resultado = Resultado(ok=False, mensagem=erro.mensagem,
                              erros=[{"codigo": erro.codigo, "mensagem": erro.mensagem, "detalhe_tecnico": ""}])
        codigo = erro.saida
    except Exception:
        config.registrar_detalhe(traceback.format_exc())
        mensagem = mensagens.msg("erro-inesperado")
        resultado = Resultado(ok=False, mensagem=mensagem,
                              erros=[{"codigo": "erro-inesperado", "mensagem": mensagem, "detalhe_tecnico": ""}])
        codigo = 2
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(resultado.para_json() if getattr(args, "json", False) else resultado.para_texto())
    return codigo
