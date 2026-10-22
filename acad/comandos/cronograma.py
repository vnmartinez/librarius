from __future__ import annotations

import hashlib
from collections import Counter
from datetime import datetime

from acad import __version__, contexto, esquemas
from acad.arquivos.escrita import Operacao, criar_proposta
from acad.cli import registrar
from acad.cronograma.classificar import tipo_linha
from acad.cronograma.exportar_planilha import exportar_planilha
from acad.cronograma.importar import importar_cronograma
from acad.cronograma.planilha import ler_cronograma
from acad.erros import ErroAcad
from acad.planejamento.arquivos import caminho, documento_encontros, ler_aulas, ler_encontros, ler_turma
from acad.saida import Resultado


def _hash(conteudo: bytes) -> str:
    return "sha256:" + hashlib.sha256(conteudo).hexdigest()


@registrar("cronograma importar", "Traz a planilha do cronograma para o planejamento")
def _importar(parser):
    parser.add_argument("disciplina")
    parser.add_argument("--turma", required=True)
    parser.add_argument("--raiz")

    def executar(args) -> Resultado:
        semestre = contexto.raiz_semestre(args)
        ws = contexto.workspace(semestre)
        disciplina = contexto.localizar_disciplina(ws, semestre, args.disciplina)
        planejamento = disciplina / contexto.perfil().pasta("planejamento")
        planilhas = [arquivo for arquivo in ws.listar(planejamento)
                     if "Cronograma" in arquivo.name and arquivo.suffix.lower() == ".xlsx"]
        if len(planilhas) != 1:
            raise ErroAcad("cronograma-nao-encontrado", "Não encontrei uma planilha única de cronograma nessa disciplina.")
        arquivo_turma = planejamento / f"turma-{args.turma}.yaml"
        turma = ler_turma(ws, disciplina, args.turma)
        conteudo = ws.ler_bytes(planilhas[0])
        linhas = ler_cronograma(conteudo, datetime.now().year)
        encontros, aulas = importar_cronograma(linhas, turma, turma["disciplina"])
        entradas = {
            planilhas[0].relative_to(semestre).as_posix(): _hash(conteudo),
            arquivo_turma.relative_to(semestre).as_posix(): _hash(ws.ler_bytes(arquivo_turma)),
        }
        documento = documento_encontros(encontros, entradas, __version__, datetime.now().astimezone())
        esquemas.validar_ou_falhar("encontro", documento)
        esquemas.validar_ou_falhar("aula", aulas)
        operacoes = []
        for nome, dados in ((f"encontros-{args.turma}.yaml", documento), ("aulas.yaml", aulas)):
            destino = caminho(disciplina, nome)
            tipo = "substituir" if ws.existe(semestre / destino) else "criar"
            operacoes.append(Operacao(tipo, destino, esquemas.para_yaml(dados).encode("utf-8"), nome))
        proposta = criar_proposta(semestre, operacoes, "Vou importar o planejamento da planilha.")
        contagem = Counter(tipo_linha(linha.aula, linha.topico) for linha in linhas if linha.data)
        mensagem = (f"Li {sum(contagem.values())} linhas: {contagem['aula']} aulas, "
                    f"{contagem['avaliacao']} avaliações, {contagem['sem-aula']} dias sem aula.")
        dias_cadastrados = {horario["dia_semana"] for horario in turma["horarios"]}
        fora_do_horario = sum(1 for linha in linhas if linha.data and linha.data.isoweekday() not in dias_cadastrados)
        avisos = ([f"{fora_do_horario} encontro(s) fora do horário da turma; usei o primeiro horário cadastrado."]
                  if fora_do_horario else [])
        return Resultado(ok=True, mensagem=mensagem, dados={"encontros": documento, "aulas": aulas},
                         proposta=proposta, avisos=avisos)
    return executar


@registrar("cronograma exportar-planilha", "Regenera a planilha do cronograma")
def _exportar_planilha(parser):
    parser.add_argument("disciplina")
    parser.add_argument("--turma", required=True)
    parser.add_argument("--raiz")

    def executar(args) -> Resultado:
        semestre = contexto.raiz_semestre(args)
        ws = contexto.workspace(semestre)
        disc = contexto.localizar_disciplina(ws, semestre, args.disciplina)
        nome = disc.name.split(" - ", 1)[1]
        if nome.endswith("Período"):
            nome = nome.rsplit(" - ", 1)[0]
        encontros = ler_encontros(ws, disc, args.turma)
        aulas = {item["id"]: item for item in ler_aulas(ws, disc)["aulas"]}
        conteudo = exportar_planilha(nome, encontros, aulas)
        destino = caminho(disc, f"Cronograma - {nome}.xlsx")
        if not ws.existe(semestre / destino):
            raise ErroAcad("cronograma-nao-encontrado",
                           "Não encontrei a planilha original para atualizar.")
        proposta = criar_proposta(semestre, [Operacao("substituir", destino, conteudo,
                                                      "cronograma atualizado")],
                                 "Confira a planilha atualizada; a anterior irá para o arquivo.")
        return Resultado(ok=True, mensagem=f"Preparei a planilha do cronograma de {nome}.",
                         proposta=proposta)

    return executar
