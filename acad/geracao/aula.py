from __future__ import annotations

from datetime import datetime
from pathlib import Path
from string import Template

from acad import __version__, esquemas
from acad.arquivos.escrita import Operacao
from acad.erros import ErroAcad
from acad.geracao.nomes import arquivos_da_aula
from acad.geracao.slides import GeradorSlides
from acad.manifestos.hashes import hash_bytes, hash_item, hash_pasta
from acad.manifestos.manifesto import montar_manifesto
from acad.planejamento.arquivos import ler_aulas, ler_encontros


_MODELOS = Path(__file__).resolve().parents[2] / "modelos"


def _operacao(ws, semestre: Path, destino: str, conteudo: bytes, resumo: str) -> Operacao:
    return Operacao("substituir" if ws.existe(semestre / destino) else "criar",
                    destino, conteudo, resumo)


def _roteiro(conteudo: dict) -> str:
    blocos = []
    for bloco in conteudo["roteiro"]["blocos"]:
        blocos.append(f"## {bloco['titulo']} ({bloco['minutos']} min)\n\n{bloco['texto']}")
    duracao = sum(bloco["minutos"] for bloco in conteudo["roteiro"]["blocos"])
    modelo = Template((_MODELOS / "roteiro-aula.md").read_text(encoding="utf-8"))
    return modelo.substitute(tema=conteudo["tema"], objetivo=conteudo["roteiro"]["objetivo"],
                           blocos="\n\n".join(blocos), duracao_total=duracao)


def _lista(conteudo: dict) -> str:
    questoes = []
    for numero, questao in enumerate(conteudo["lista"]["questoes"], 1):
        linha = f"{numero}. {questao['enunciado']}"
        if questao.get("resposta"):
            linha += f"\n\n   Resposta: {questao['resposta']}"
        questoes.append(linha)
    modelo = Template((_MODELOS / "lista.md").read_text(encoding="utf-8"))
    return modelo.substitute(tema=conteudo["tema"], questoes="\n\n".join(questoes))


def _duracao_encontros(ws, disc: Path, id_aula: str) -> int:
    planejamento = disc / "01 - Planejamento"
    total = 0
    for arquivo in ws.listar(planejamento):
        if arquivo.name.startswith("encontros-") and arquivo.suffix.lower() == ".yaml":
            turma = arquivo.stem.removeprefix("encontros-")
            total += sum(encontro.minutos for encontro in ler_encontros(ws, disc, turma)
                         if encontro.status != "cancelado" and id_aula in encontro.aulas)
    return total


def planejar_aula(ws, semestre: Path, disc: Path, num: str, conteudo: dict,
                  gerador: GeradorSlides, agora: datetime,
                  revisar: bool = False) -> tuple[list[Operacao], list[str]]:
    esquemas.validar_ou_falhar("conteudo-aula", conteudo)
    id_aula = f"Aula {int(num):02d}"
    documento = ler_aulas(ws, disc)
    aula = next((item for item in documento["aulas"] if item["id"] == id_aula), None)
    if aula is None:
        raise ErroAcad("aula-nao-encontrada", f"Não encontrei {id_aula} no plano da disciplina.")
    if aula["status"] in {"aprovada", "ministrada"} and not revisar:
        raise ErroAcad("aula-aprovada",
                       "Essa aula já foi aprovada por você. Para mudar, peça para revisar a aula.", saida=1)

    nomes = arquivos_da_aula(num, conteudo["tema"])
    prefixo = disc.relative_to(semestre).as_posix()
    operacoes = []
    avisos = []
    artefatos = []

    def adicionar(relativo: str, dados: bytes, resumo: str) -> None:
        destino = f"{prefixo}/{relativo}"
        operacoes.append(_operacao(ws, semestre, destino, dados, resumo))
        artefatos.append(destino)

    adicionar(nomes["roteiro"], _roteiro(conteudo).encode("utf-8"), "roteiro da aula")
    aula["roteiro"] = f"{prefixo}/{nomes['roteiro']}"
    duracao = sum(bloco["minutos"] for bloco in conteudo["roteiro"]["blocos"])
    aula["duracao_estimada_min"] = duracao
    minutos_disponiveis = _duracao_encontros(ws, disc, id_aula)
    if minutos_disponiveis and abs(duracao - minutos_disponiveis) / minutos_disponiveis > 0.15:
        avisos.append(f"O roteiro tem {duracao} min, mas a aula tem {minutos_disponiveis} min.")

    if "codigo" in conteudo:
        caminhos = []
        for nome, texto in conteudo["codigo"]["arquivos"].items():
            if Path(nome).name != nome or nome in {"", ".", ".."} or "\\" in nome:
                raise ErroAcad("nome-arquivo-invalido", "O nome do arquivo de código deve ser simples.")
            relativo = f"{nomes['codigo']}/{nome}"
            adicionar(relativo, texto.encode("utf-8"), "exemplo de código")
            caminhos.append(f"{prefixo}/{relativo}")
        aula["codigo"] = caminhos
    if "lista" in conteudo:
        adicionar(nomes["lista"], _lista(conteudo).encode("utf-8"), "lista de atividades")
        aula["lista"] = f"{prefixo}/{nomes['lista']}"
    if "slides" in conteudo:
        try:
            dados_slides = gerador.gerar(conteudo, None)
            adicionar(nomes["slides"], dados_slides, "slides da aula")
            aula["slides"] = f"{prefixo}/{nomes['slides']}"
        except ErroAcad as erro:
            if erro.codigo != "decisao-pendente-d4":
                raise
            avisos.append("Os slides ficam para depois: ainda falta escolher o modelo.")

    aula["tema"] = conteudo["tema"]
    aula["status"] = "rascunho"
    entradas = {f"{prefixo}/01 - Planejamento/aulas.yaml#{id_aula}": hash_item(aula)}
    pasta_modelos = next((p for p in ws.listar(semestre)
                          if p.is_dir() and "Modelos" in p.name), None)
    if pasta_modelos and "slides" in aula:
        entradas[pasta_modelos.relative_to(semestre).as_posix()] = hash_pasta(ws, pasta_modelos)
    referencia = disc / "05 - Materiais de Referência"
    if ws.existe(referencia):
        for arquivo in ws.listar(referencia):
            if arquivo.is_file() and arquivo.suffix.lower() == ".pdf" and "programa" in arquivo.name.lower():
                entradas[arquivo.relative_to(semestre).as_posix()] = hash_bytes(ws.ler_bytes(arquivo))
    aula["manifesto"] = montar_manifesto(artefatos, entradas, __version__, agora)
    esquemas.validar_ou_falhar("aula", documento)
    arquivo_aulas = f"{prefixo}/01 - Planejamento/aulas.yaml"
    operacoes.append(_operacao(ws, semestre, arquivo_aulas,
                               esquemas.para_yaml(documento).encode("utf-8"), "plano da disciplina"))
    return operacoes, avisos
