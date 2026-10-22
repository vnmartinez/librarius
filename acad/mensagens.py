"""Catálogo de mensagens ao professor, em português simples."""

import re

TERMOS_PROIBIDOS = (
    "yaml", "json", "hash", "sha", "schema", "stack", "exception",
    "traceback", "path", "stdout",
)

MENSAGENS: dict[str, str] = {
    "tudo-certo": "Tudo certo.",
    "raiz-nao-encontrada": "Não encontrei a pasta dos seus materiais. Me diga onde ela fica.",
    "propostas-arquivos": "Vou mexer em {n} arquivo(s). Posso continuar?",
    "proposta-aplicada": "Pronto, as alterações foram feitas.",
    "nada-para-desfazer": "Não há alteração recente para desfazer.",
    "desfeito": "Desfiz a última alteração.",
    "pastas-protegidas": "{n} pasta(s) com dados de alunos foram protegidas e não foram lidas.",
    "decisao-pendente": "Essa parte ainda depende de uma decisão sua: {assunto}.",
    "python-ausente": "Falta um programa (Python) para eu trabalhar com seus arquivos. Posso instalar para você?",
    "erro-inesperado": "Algo deu errado do meu lado. Anotei os detalhes para o suporte.",
}


def msg(codigo: str, **kw) -> str:
    return MENSAGENS[codigo].format(**kw)


def contem_termo_tecnico(texto: str) -> bool:
    baixo = texto.lower()
    return any(re.search(rf"\b{termo}\b", baixo) for termo in TERMOS_PROIBIDOS)
