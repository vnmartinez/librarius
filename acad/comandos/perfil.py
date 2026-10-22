from __future__ import annotations

import re
from pathlib import Path

from acad import contexto, esquemas
from acad.arquivos.escrita import Operacao, criar_proposta
from acad.cli import registrar
from acad.erros import ErroAcad
from acad.perfil.detectar import detectar
from acad.perfil.perfil import carregar_perfil
from acad.saida import Resultado


@registrar("perfil detectar", "Reconhece a organização das pastas do semestre")
def _detectar(parser):
    parser.add_argument("--raiz", required=True)

    def executar(args) -> Resultado:
        dados = detectar(Path(args.raiz), contexto.perfil())
        if not dados["semestres"]:
            return Resultado(ok=True, mensagem="Não encontrei um semestre nessa pasta.", dados=dados)
        semestre = dados["semestres"][0]
        mensagem = (f"Encontrei o {semestre['periodo']}º semestre de {semestre['ano']} com "
                    f"{len(dados['disciplinas'])} disciplinas: "
                    f"{', '.join(item['nome'] for item in dados['disciplinas'])}. "
                    "Quer que eu use essa organização?")
        return Resultado(ok=True, mensagem=mensagem, dados=dados)

    return executar


@registrar("iniciar", "Escolhe o semestre e guarda a configuração local")
def _iniciar(parser):
    parser.add_argument("semestre")
    parser.add_argument("--raiz", required=True)
    parser.add_argument("--perfil")
    parser.add_argument("--confirmar", action="store_true")

    def executar(args) -> Resultado:
        raiz = Path(args.raiz).resolve()
        if not re.fullmatch(r"\d{4}-[12]", args.semestre):
            raise ErroAcad("semestre-invalido", "Use semestre no formato AAAA-N, por exemplo 2026-2.")
        if not raiz.is_dir():
            raise ErroAcad("raiz-nao-encontrada", "Não encontrei a pasta do semestre.")
        avisos = []
        escolhido = args.perfil or (contexto.carregar_configuracao() or {}).get("perfil")
        if not escolhido:
            escolhido = contexto.PERFIL_PADRAO
            if escolhido == "neutro":
                avisos.append("Usei o perfil neutro, sem marca de instituição. Se quiser, crio o perfil da sua "
                              "instituição a partir da sua pasta.")
        carregar_perfil(escolhido)
        documento = {"versao_esquema": 1, "perfil": escolhido,
                     "raiz_workspace": str(raiz), "semestre_atual": args.semestre}
        esquemas.validar_ou_falhar("semestre", documento)
        if args.confirmar:
            contexto.gravar_configuracao(documento)
        mensagem = (f"Vou usar {raiz} como semestre {args.semestre}. "
                    + ("Configuração guardada." if args.confirmar else "Confirme para guardar essa escolha."))
        return Resultado(ok=True, mensagem=mensagem, dados=documento, avisos=avisos)

    return executar


@registrar("disciplina criar", "Cria o cadastro de uma disciplina")
def _disciplina_criar(parser):
    parser.add_argument("codigo")
    parser.add_argument("--pasta", required=True)
    parser.add_argument("--nome", required=True)
    parser.add_argument("--carga", type=float, required=True)
    parser.add_argument("--unidade", choices=("hora_relogio", "hora_aula"))
    parser.add_argument("--minutos-hora-aula", type=int)
    parser.add_argument("--raiz")

    def executar(args) -> Resultado:
        if args.unidade is None:
            padrao = contexto.perfil()
            args.unidade = padrao.unidade_carga
            args.minutos_hora_aula = args.minutos_hora_aula or padrao.minutos_hora_aula
        if args.unidade == "hora_aula" and not args.minutos_hora_aula:
            raise ErroAcad("minutos-hora-aula-ausentes",
                           "Falta informar os minutos de cada hora-aula.")
        semestre = contexto.raiz_semestre(args)
        ws = contexto.workspace(semestre)
        pasta = semestre / args.pasta
        if not pasta.is_dir() or ws.excluido(pasta):
            raise ErroAcad("disciplina-nao-encontrada", "Não encontrei essa pasta de disciplina.")
        ano, periodo = contexto.perfil().semestre_de(semestre) or (int(semestre.parent.name), 2)
        carga = {"valor": args.carga, "unidade": args.unidade}
        if args.minutos_hora_aula:
            carga["minutos_hora_aula"] = args.minutos_hora_aula
        documento = {"versao_esquema": 1, "disciplina": {
            "codigo": args.codigo.upper(), "nome": args.nome, "pasta": pasta.name,
            "semestre": f"{ano}-{periodo}", "carga_horaria": carga,
            "planejamento": {"status": "rascunho"},
        }}
        esquemas.validar_ou_falhar("disciplina", documento)
        destino = f"{pasta.name}/{contexto.perfil().pasta('planejamento')}/disciplina.yaml"
        tipo = "substituir" if ws.existe(semestre / destino) else "criar"
        proposta = criar_proposta(semestre, [Operacao(tipo, destino, esquemas.para_yaml(documento).encode("utf-8"),
                                                      "cadastro da disciplina")], "Confira os dados da disciplina.")
        return Resultado(ok=True, mensagem=f"Preparei o cadastro de {args.nome}.",
                         dados=documento, proposta=proposta)

    return executar


@registrar("turma criar", "Cria o horário de uma turma")
def _turma_criar(parser):
    parser.add_argument("disciplina")
    parser.add_argument("--turma", required=True)
    parser.add_argument("--horario", action="append", required=True)
    parser.add_argument("--fuso", default="America/Sao_Paulo")
    parser.add_argument("--raiz")

    def executar(args) -> Resultado:
        horarios = []
        for texto in args.horario:
            partes = texto.split(maxsplit=3)
            if len(partes) < 3 or not partes[0].isdigit():
                raise ErroAcad("horario-invalido", "Use dia, início e fim: 2 19:00 20:40.")
            dia = int(partes[0])
            if not 1 <= dia <= 7:
                raise ErroAcad("dia-semana-invalido", "O dia da semana vai de 1 (segunda) a 7 (domingo).")
            horario = {"dia_semana": dia, "inicio": partes[1], "fim": partes[2]}
            if len(partes) == 4:
                horario["sala"] = partes[3]
            horarios.append(horario)
        semestre = contexto.raiz_semestre(args)
        ws = contexto.workspace(semestre)
        disc = contexto.localizar_disciplina(ws, semestre, args.disciplina)
        arquivo_disc = disc / contexto.perfil().pasta("planejamento") / "disciplina.yaml"
        codigo = (esquemas.carregar_yaml(ws.ler_texto(arquivo_disc))["disciplina"]["codigo"]
                  if ws.existe(arquivo_disc) else args.disciplina.upper())
        documento = {"versao_esquema": 1, "turma": {
            "id": args.turma, "disciplina": codigo, "fuso": args.fuso, "horarios": horarios,
        }}
        esquemas.validar_ou_falhar("turma", documento)
        destino = f"{disc.name}/{contexto.perfil().pasta('planejamento')}/turma-{args.turma}.yaml"
        tipo = "substituir" if ws.existe(semestre / destino) else "criar"
        proposta = criar_proposta(semestre, [Operacao(tipo, destino, esquemas.para_yaml(documento).encode("utf-8"),
                                                      "horário da turma")], "Confira o horário da turma.")
        return Resultado(ok=True, mensagem=f"Preparei o horário da turma {args.turma}.",
                         dados=documento, proposta=proposta)

    return executar


@registrar("disciplina estrutura", "Prepara as pastas padrão que faltam")
def _disciplina_estrutura(parser):
    parser.add_argument("disciplina")
    parser.add_argument("--raiz")

    def executar(args) -> Resultado:
        semestre = contexto.raiz_semestre(args)
        ws = contexto.workspace(semestre)
        disc = contexto.localizar_disciplina(ws, semestre, args.disciplina)
        operacoes = [Operacao("criar-pasta", f"{disc.name}/{nome}", resumo=nome)
                     for nome in contexto.perfil().subpastas_disciplina if not (disc / nome).is_dir()]
        proposta = (criar_proposta(semestre, operacoes, "Confira as pastas que faltam.")
                    if operacoes else None)
        mensagem = (f"Preparei {len(operacoes)} pasta(s) para essa disciplina." if operacoes
                    else "As pastas da disciplina já estão completas.")
        return Resultado(ok=True, mensagem=mensagem, proposta=proposta)

    return executar
