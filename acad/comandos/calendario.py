from __future__ import annotations

from collections import Counter
from pathlib import Path
from datetime import datetime

from acad import contexto, esquemas
from acad.arquivos.escrita import Operacao, criar_proposta
from acad.calendario.importar_ics import importar_ics
from acad.calendario.importar_xlsx import importar_xlsx
from acad.calendario.modelo import confirmar, de_documento, para_documento
from acad.cli import ler_data, registrar
from acad.erros import ErroAcad
from acad.saida import Resultado


@registrar("calendario importar", "Lê o calendário da instituição")
def _importar(parser):
    parser.add_argument("arquivo")
    parser.add_argument("--inicio", required=True)
    parser.add_argument("--fim", required=True)
    parser.add_argument("--semestre", required=True)
    parser.add_argument("--raiz")

    def executar(args) -> Resultado:
        semestre = contexto.raiz_semestre(args)
        caminho = Path(args.arquivo)
        if caminho.suffix.lower() not in (".ics", ".xlsx"):
            raise ErroAcad("formato-invalido", "Escolha um calendário em formato de agenda ou planilha.")
        importador = importar_ics if caminho.suffix.lower() == ".ics" else importar_xlsx
        if caminho.resolve().is_relative_to(semestre):
            conteudo = contexto.workspace(semestre).ler_bytes(caminho)
        else:
            conteudo = caminho.read_bytes()
        calendario = importador(conteudo, args.semestre, ler_data(args.inicio), ler_data(args.fim))
        calendario.fonte["arquivo"] = caminho.name
        destino = f"{contexto.pasta_administracao(semestre).name}/calendario.yaml"
        tipo = "substituir" if (semestre / destino).exists() else "criar"
        documento = esquemas.para_yaml(para_documento(calendario)).encode("utf-8")
        proposta = criar_proposta(semestre, [Operacao(tipo, destino, documento, "calendário do semestre")],
                                 "Vou guardar o calendário do semestre na pasta de administração.")
        contagem = Counter(dia.tipo for dia in calendario.dias)
        mensagem = (f"Li o calendário: {contagem['feriado']} feriado(s), "
                    f"{contagem['recesso']} dia(s) de recesso, "
                    f"{contagem['sabado-letivo']} sábado(s) letivo(s). Confira antes de eu usar.")
        return Resultado(ok=True, mensagem=mensagem, dados=para_documento(calendario), proposta=proposta)
    return executar


@registrar("calendario confirmar", "Confirma o calendário do semestre")
def _confirmar(parser):
    parser.add_argument("--raiz")

    def executar(args) -> Resultado:
        semestre = contexto.raiz_semestre(args)
        destino = f"{contexto.pasta_administracao(semestre).name}/calendario.yaml"
        documento = esquemas.carregar_yaml(contexto.workspace(semestre).ler_texto(semestre / destino))
        calendario = confirmar(de_documento(documento), datetime.now().astimezone())
        proposta = criar_proposta(semestre, [Operacao("substituir", destino,
                                                    esquemas.para_yaml(para_documento(calendario)).encode("utf-8"),
                                                    "calendário confirmado")],
                                 "Vou confirmar o calendário do semestre.")
        return Resultado(ok=True, mensagem="O calendário está pronto para confirmação.",
                         dados=para_documento(calendario), proposta=proposta)
    return executar
