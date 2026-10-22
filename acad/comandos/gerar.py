from __future__ import annotations

import json
import tempfile
from datetime import datetime
from pathlib import Path

from acad import __version__, contexto, esquemas
from acad.arquivos.escrita import Operacao, criar_proposta
from acad.cli import ler_data, registrar
from acad.erros import ErroAcad
from acad.geracao.aula import planejar_aula
from acad.geracao.avaliacao import nome_arquivo, renderizar, versoes
from acad.geracao.latex import compilar, compilador
from acad.geracao.slides import obter_gerador
from acad.manifestos.hashes import hash_bytes
from acad.manifestos.manifesto import montar_manifesto
from acad.planejamento.arquivos import ler_aulas, ler_encontros
from acad.saida import Resultado
from acad.validacao.regras import regra_avaliacao_nao_ministrada


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


@registrar("gerar avaliacao", "Prepara uma avaliação e seu gabarito")
def _gerar_avaliacao(parser):
    parser.add_argument("disciplina")
    parser.add_argument("--etapa", required=True)
    parser.add_argument("--turma", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--conteudo", required=True)
    parser.add_argument("--descricao", default="Avaliação")
    parser.add_argument("--versoes", type=int, default=1)
    parser.add_argument("--semente", type=int, default=1234)
    parser.add_argument("--raiz")

    def executar(args) -> Resultado:
        if not 1 <= args.versoes <= 26:
            raise ErroAcad("versoes-invalidas", "Escolha de 1 a 26 versões da prova.")
        semestre = contexto.raiz_semestre(args)
        ws = contexto.workspace(semestre)
        disc = contexto.localizar_disciplina(ws, semestre, args.disciplina)
        data = ler_data(args.data)
        try:
            conteudo_bytes = Path(args.conteudo).read_bytes()
            conteudo = json.loads(conteudo_bytes.decode("utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as erro:
            raise ErroAcad("conteudo-invalido", "Não consegui ler as questões da avaliação.", str(erro)) from erro
        esquemas.validar_ou_falhar("conteudo-avaliacao", conteudo)
        aulas = ler_aulas(ws, disc)["aulas"]
        encontros = ler_encontros(ws, disc, args.turma)
        avaliacao_base = {"etapa": args.etapa, "data": data.isoformat(),
                          "aulas_cobertas": conteudo["aulas_cobertas"]}
        achados = regra_avaliacao_nao_ministrada(avaliacao_base, aulas, encontros)
        if achados:
            id_aula = achados[0].mensagem.split(" cobre ", 1)[1].split(",", 1)[0]
            futura = next((e.data for e in encontros if id_aula in e.aulas and e.data >= data), None)
            mensagem = (f"A prova cobre {id_aula}, que só acontece em {futura:%d/%m} — depois da prova."
                        if futura else achados[0].mensagem)
            raise ErroAcad("avaliacao-sobre-nao-ministrada", mensagem, saida=1)
        nome_disciplina = disc.name.split(" - ", 1)[1]
        nome_disciplina = nome_disciplina.rsplit(" - ", 1)[0] if nome_disciplina.endswith("Período") else nome_disciplina
        avaliacoes_dir = next((p for p in ws.listar(semestre)
                               if p.is_dir() and contexto.perfil().pasta_avaliacoes.match(p.name)), None)
        if avaliacoes_dir is None:
            raise ErroAcad("pasta-avaliacoes-ausente", "Não encontrei a pasta de avaliações do semestre.")
        base_destino = f"{avaliacoes_dir.name}/{args.etapa}"
        pasta_modelos = next((p for p in ws.listar(semestre)
                              if p.is_dir() and contexto.perfil().pasta_modelos.match(p.name)), None)
        modelo_institucional = (pasta_modelos / "Modelo LaTeX" / "modelo-prova.tex"
                               if pasta_modelos else None)
        if modelo_institucional and ws.existe(modelo_institucional):
            modelo = ws.ler_texto(modelo_institucional)
            pasta_apoio = modelo_institucional.parent
            entrada_modelo = modelo_institucional.relative_to(semestre).as_posix()
        else:
            modelo = (Path(__file__).resolve().parents[2] / "modelos" / "prova.tex").read_text(encoding="utf-8")
            pasta_apoio = None
            entrada_modelo = None
        entradas = {"questoes.json": hash_bytes(conteudo_bytes)}
        if entrada_modelo:
            entradas[entrada_modelo] = hash_bytes(modelo.encode("utf-8"))
        operacoes = []
        artefatos = []
        avisos = []
        caminhos_provas = []
        caminho_gabarito = ""
        dados = {"titulo": args.descricao.upper(), "disciplina": nome_disciplina,
                 "professor": "", "data": data.isoformat()}
        with tempfile.TemporaryDirectory(prefix="acad-prova-") as temporaria:
            temporaria = Path(temporaria)
            if pasta_apoio:
                for arquivo in ws.listar(pasta_apoio):
                    if arquivo.is_file() and arquivo.suffix.lower() in {".sty", ".jpg", ".jpeg", ".png", ".cls"}:
                        (temporaria / arquivo.name).write_bytes(ws.ler_bytes(arquivo))
            for indice, questoes in enumerate(versoes(conteudo["questoes"], args.semente, args.versoes)):
                letra = chr(ord("A") + indice) if args.versoes > 1 else None
                for gabarito in (False, True):
                    nome = nome_arquivo(nome_disciplina, args.etapa, args.descricao, args.turma,
                                        letra, gabarito, "tex")
                    destino = f"{base_destino}/{nome}"
                    tex = temporaria / nome
                    texto_tex = renderizar(modelo, dados, questoes, gabarito)
                    tex.write_text(texto_tex, encoding="utf-8")
                    operacoes.append(Operacao("substituir" if ws.existe(semestre / destino) else "criar",
                                              destino, texto_tex.encode("utf-8"),
                                              "gabarito" if gabarito else "prova"))
                    artefatos.append(destino)
                    if gabarito:
                        caminho_gabarito = destino
                    else:
                        caminhos_provas.append(destino)
                    pdf = compilar(tex) if compilador() else None
                    if pdf:
                        destino_pdf = str(Path(destino).with_suffix(".pdf")).replace("\\", "/")
                        operacoes.append(Operacao("substituir" if ws.existe(semestre / destino_pdf) else "criar",
                                                  destino_pdf, pdf.read_bytes(), "PDF da avaliação"))
                        artefatos.append(destino_pdf)
                    elif compilador():
                        avisos.append(f"Não consegui compilar {nome}; o arquivo de texto da prova foi preparado.")
        if not compilador():
            avisos.append("O PDF fica para depois; não encontrei um compilador de provas.")
        avaliacao = {"etapa": args.etapa, "turmas": [args.turma], "data": data.isoformat(),
                     "aulas_cobertas": conteudo["aulas_cobertas"],
                     "objetivos": conteudo.get("objetivos", []), "questoes": conteudo["questoes"],
                     "semente": args.semente,
                     "arquivos": {"prova": caminhos_provas[0], "gabarito": caminho_gabarito},
                     "manifesto": montar_manifesto(artefatos, entradas, __version__, datetime.now().astimezone())}
        documento = {"versao_esquema": 1, "avaliacao": avaliacao}
        esquemas.validar_ou_falhar("avaliacao", documento)
        destino_yaml = f"{disc.name}/01 - Planejamento/avaliacoes/{args.etapa}-{args.turma}.yaml"
        operacoes.append(Operacao("substituir" if ws.existe(semestre / destino_yaml) else "criar",
                                  destino_yaml, esquemas.para_yaml(documento).encode("utf-8"),
                                  "plano da avaliação"))
        proposta = criar_proposta(semestre, operacoes, "Confira a avaliação e o gabarito.")
        return Resultado(ok=True, mensagem=f"Preparei {args.versoes} versão(ões) da avaliação {args.etapa}.",
                         avisos=avisos, dados=documento, proposta=proposta)

    return executar
