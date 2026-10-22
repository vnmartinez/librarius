import asyncio, json, os, sys
from pathlib import Path

from mcp import Client
from mcp.client.stdio import StdioServerParameters

RAIZ = Path(__file__).resolve().parents[2]
AMOSTRA = RAIZ / "testes" / "amostras" / "fasoft"


async def _sessao(ferramenta: str, argumentos: dict, dados: Path) -> tuple[list[str], str]:
    params = StdioServerParameters(
        command=sys.executable, args=["-m", "acad", "mcp"],
        env={**os.environ, "PYTHONPATH": str(RAIZ), "PYTHONUTF8": "1", "ACAD_DADOS": str(dados)},
    )
    async with Client(params) as cliente:
        nomes = [t.name for t in (await cliente.list_tools()).tools]
        r = await cliente.call_tool(ferramenta, argumentos)
        return nomes, r.content[0].text


def _sessao_mcp(ferramenta, argumentos, dados):
    return asyncio.run(_sessao(ferramenta, argumentos, dados))


def test_lista_e_chama_ferramentas(tmp_path):
    nomes, resposta = _sessao_mcp("cronograma-consultar", {"data": "2026-07-28", "raiz": str(AMOSTRA)}, tmp_path)
    assert {"ambiente-verificar", "cronograma-consultar", "validar", "encontros-gerar", "plano-distribuir",
            "plano-replanejar", "gerar-aula", "gerar-avaliacao", "aplicar", "desfazer"} <= set(nomes)
    assert json.loads(resposta)["dados"]["quantidade_aulas"] == 1


def test_ferramenta_de_validacao_nao_grava(tmp_path, semestre_sintetico):
    _, resposta = _sessao_mcp("validar", {"raiz": str(semestre_sintetico)}, tmp_path)
    assert json.loads(resposta)["proposta"] is None


def test_erro_vira_envelope_e_nao_derruba_o_servidor(tmp_path):
    _, resposta = _sessao_mcp("aplicar", {"id": "inexistente"}, tmp_path)
    assert json.loads(resposta)["ok"] is False


def test_descricoes_em_portugues_com_aviso_de_gravacao(tmp_path):
    async def listar():
        params = StdioServerParameters(command=sys.executable, args=["-m", "acad", "mcp"],
                                       env={**os.environ, "PYTHONPATH": str(RAIZ), "ACAD_DADOS": str(tmp_path)})
        async with Client(params) as c:
            return {t.name: t.description for t in (await c.list_tools()).tools}
    d = asyncio.run(listar())
    assert "aplicar" in d["gerar-aula"] and "aplicar" in d["encontros-gerar"]
