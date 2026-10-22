"""Servidor MCP local (stdio) que expõe o núcleo `acad` como ferramentas."""
from __future__ import annotations

import contextlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

from mcp.server import MCPServer

from acad import cli, mensagens
from acad.saida import Resultado

AVISO = " Esta ferramenta só prepara uma proposta; nada é gravado até chamar `aplicar`."


def _rodar(argv: list[str]) -> str:
    """Executa um subcomando e devolve o envelope de resultado como texto JSON."""
    try:
        with contextlib.redirect_stdout(sys.stderr):
            _, resultado = cli.executar([*argv, "--json"])
    except SystemExit:
        mensagem = "Não entendi o pedido: faltou alguma informação."
        resultado = Resultado(ok=False, mensagem=mensagem,
                              erros=[{"codigo": "argumentos-invalidos", "mensagem": mensagem, "detalhe_tecnico": ""}])
    return resultado.para_json()


def _com_raiz(argv: list[str], raiz: str | None) -> list[str]:
    return [*argv, "--raiz", raiz] if raiz else argv


def _com_arquivo(conteudo: dict, argv_fn) -> str:
    pasta = Path(tempfile.mkdtemp(prefix="librarius-"))
    try:
        arquivo = pasta / "conteudo.json"
        arquivo.write_text(json.dumps(conteudo, ensure_ascii=False), encoding="utf-8")
        return _rodar(argv_fn(str(arquivo)))
    finally:
        shutil.rmtree(pasta, ignore_errors=True)


def criar_servidor() -> MCPServer:
    servidor = MCPServer("librarius")

    @servidor.tool(name="ambiente-verificar", description="Confere se o computador está pronto para o Librarius.")
    def ambiente_verificar() -> str:
        return _rodar(["ambiente", "verificar"])

    @servidor.tool(name="cronograma-consultar",
                   description="Diz qual é a aula de hoje ou de uma data (formato dia/mês/ano ou ano-mês-dia), com o estado dos materiais.")
    def cronograma_consultar(data: str | None = None, raiz: str | None = None) -> str:
        argv = ["cronograma", "consultar"] + (["--data", data] if data else [])
        return _rodar(_com_raiz(argv, raiz))

    @servidor.tool(name="validar",
                   description="Confere carga horária, feriados, nomes e materiais do semestre ou de uma disciplina. Não altera nada.")
    def validar(disciplina: str | None = None, raiz: str | None = None) -> str:
        return _rodar(_com_raiz(["validar"] + ([disciplina] if disciplina else []), raiz))

    @servidor.tool(name="encontros-gerar",
                   description="Gera os encontros de uma turma a partir do calendário e dos horários." + AVISO)
    def encontros_gerar(disciplina: str, turma: str, raiz: str | None = None) -> str:
        return _rodar(_com_raiz(["encontros", "gerar", disciplina, "--turma", turma], raiz))

    @servidor.tool(name="plano-distribuir",
                   description="Distribui as aulas do programa pelos encontros da turma." + AVISO)
    def plano_distribuir(disciplina: str, turma: str, raiz: str | None = None) -> str:
        return _rodar(_com_raiz(["plano", "distribuir", disciplina, "--turma", turma], raiz))

    @servidor.tool(name="plano-replanejar",
                   description="Refaz o plano quando um encontro é cancelado e mostra o que muda." + AVISO)
    def plano_replanejar(disciplina: str, turma: str, cancelar: str, motivo: str | None = None,
                         raiz: str | None = None) -> str:
        argv = ["plano", "replanejar", disciplina, "--turma", turma, "--cancelar", cancelar]
        if motivo:
            argv += ["--motivo", motivo]
        return _rodar(_com_raiz(argv, raiz))

    @servidor.tool(name="gerar-aula",
                   description="Prepara o material de uma aula (roteiro, código, lista) a partir do conteúdo informado." + AVISO)
    def gerar_aula(disciplina: str, aula: str, conteudo: dict, revisar: bool = False, raiz: str | None = None) -> str:
        def montar(arquivo: str) -> list[str]:
            argv = ["gerar", "aula", disciplina, "--aula", aula, "--conteudo", arquivo] + (["--revisar"] if revisar else [])
            return _com_raiz(argv, raiz)
        return _com_arquivo(conteudo, montar)

    @servidor.tool(name="gerar-avaliacao",
                   description="Monta uma prova com gabarito a partir das questões informadas." + AVISO)
    def gerar_avaliacao(disciplina: str, etapa: str, turma: str, data: str, conteudo: dict,
                        descricao: str | None = None, versoes: int | None = None, semente: int | None = None,
                        raiz: str | None = None) -> str:
        def montar(arquivo: str) -> list[str]:
            argv = ["gerar", "avaliacao", disciplina, "--etapa", etapa, "--turma", turma, "--data", data,
                    "--conteudo", arquivo]
            if descricao:
                argv += ["--descricao", descricao]
            if versoes is not None:
                argv += ["--versoes", str(versoes)]
            if semente is not None:
                argv += ["--semente", str(semente)]
            return _com_raiz(argv, raiz)
        return _com_arquivo(conteudo, montar)

    @servidor.tool(name="aplicar",
                   description="Grava uma proposta já mostrada ao professor. Só chamar depois de um \"sim\" claro.")
    def aplicar(id: str) -> str:
        return _rodar(["aplicar", id])

    @servidor.tool(name="desfazer", description="Desfaz a última gravação feita pelo Librarius.")
    def desfazer() -> str:
        return _rodar(["desfazer"])

    return servidor


def servir() -> None:
    criar_servidor().run("stdio")
