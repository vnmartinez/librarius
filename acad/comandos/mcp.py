from __future__ import annotations

from acad.cli import registrar
from acad.saida import Resultado


@registrar("mcp", "Inicia o servidor MCP local (usado pelos programas de IA)")
def _mcp(parser):
    def executar(args) -> Resultado:
        from acad import mcp

        mcp.servir()
        raise SystemExit(0)

    return executar
