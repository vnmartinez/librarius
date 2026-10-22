from __future__ import annotations

from datetime import datetime

from acad import contexto, esquemas
from acad.arquivos.escrita import Operacao, criar_proposta
from acad.cli import registrar
from acad.erros import ErroAcad
from acad.planejamento.arquivos import caminho, ler_aulas
from acad.planejamento.status import mudar_status
from acad.saida import Resultado


@registrar("aula status", "Atualiza a etapa de preparo de uma aula")
def _status(parser):
    parser.add_argument("disciplina")
    parser.add_argument("--aula", required=True)
    parser.add_argument("novo")
    parser.add_argument("--encontro")
    parser.add_argument("--raiz")

    def executar(args) -> Resultado:
        semestre = contexto.raiz_semestre(args)
        ws = contexto.workspace(semestre)
        disc = contexto.localizar_disciplina(ws, semestre, args.disciplina)
        documento = ler_aulas(ws, disc)
        id_aula = f"Aula {int(args.aula):02d}"
        indice = next((i for i, aula in enumerate(documento["aulas"]) if aula["id"] == id_aula), None)
        if indice is None:
            raise ErroAcad("aula-nao-encontrada", f"Não encontrei {id_aula} no plano.")
        documento["aulas"][indice] = mudar_status(documento["aulas"][indice], args.novo,
                                                   datetime.now().astimezone(), args.encontro)
        esquemas.validar_ou_falhar("aula", documento)
        destino = caminho(disc, "aulas.yaml")
        operacoes = [Operacao("substituir", destino,
                              esquemas.para_yaml(documento).encode("utf-8"), "estado da aula")]
        if args.novo == "ministrada":
            encontrados = []
            planejamento = disc / "01 - Planejamento"
            for arquivo in ws.listar(planejamento):
                if not arquivo.name.startswith("encontros-") or arquivo.suffix.lower() != ".yaml":
                    continue
                encontros_doc = esquemas.carregar_yaml(ws.ler_texto(arquivo))
                esquemas.validar_ou_falhar("encontro", encontros_doc)
                for encontro in encontros_doc["encontros"]:
                    if encontro["id"] == args.encontro and id_aula in encontro["aulas"]:
                        encontro["status"] = "realizado"
                        encontrados.append((arquivo, encontros_doc))
            if len(encontrados) != 1:
                raise ErroAcad("encontro-nao-encontrado",
                               "Não encontrei um encontro único dessa aula com esse número.")
            arquivo, encontros_doc = encontrados[0]
            relativo = arquivo.relative_to(semestre).as_posix()
            operacoes.append(Operacao("substituir", relativo,
                                      esquemas.para_yaml(encontros_doc).encode("utf-8"),
                                      "encontro realizado"))
        proposta = criar_proposta(semestre, operacoes, "Confira a mudança de estado da aula.")
        return Resultado(ok=True, mensagem=f"{id_aula} passará para {args.novo}.",
                         dados={"aula": documento["aulas"][indice]}, proposta=proposta)

    return executar
