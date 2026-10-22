from __future__ import annotations

from pathlib import Path

from acad import esquemas
from acad.arquivos.caminhos import sem_acento
from acad.arquivos.privacidade import Workspace
from acad.config import dir_dados
from acad.erros import ErroAcad
from acad.mensagens import msg
from acad.perfil.perfil import Perfil, carregar_perfil
from acad.validacao.nomenclatura import disciplinas


def carregar_configuracao() -> dict | None:
    arquivo = dir_dados() / "configuracao.yaml"
    if not arquivo.exists():
        return None
    documento = esquemas.carregar_yaml(arquivo.read_text(encoding="utf-8"))
    esquemas.validar_ou_falhar("semestre", documento)
    return documento


def gravar_configuracao(documento: dict) -> Path:
    esquemas.validar_ou_falhar("semestre", documento)
    destino = dir_dados() / "configuracao.yaml"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(esquemas.para_yaml(documento), encoding="utf-8")
    return destino


def raiz_semestre(args) -> Path:
    informada = getattr(args, "raiz", None)
    configuracao = carregar_configuracao()
    caminho = informada or (configuracao or {}).get("raiz_workspace")
    if not caminho:
        raise ErroAcad("raiz-nao-encontrada", msg("raiz-nao-encontrada"), saida=3)
    raiz = Path(caminho).resolve()
    if not raiz.is_dir():
        raise ErroAcad("raiz-nao-encontrada", msg("raiz-nao-encontrada"), str(raiz), saida=3)
    return raiz


def workspace(raiz: Path) -> Workspace:
    return Workspace(raiz, perfil().exclusao)


def perfil() -> Perfil:
    configuracao = carregar_configuracao()
    return carregar_perfil((configuracao or {}).get("perfil", "fasoft"))


def raiz_padrao_consulta() -> Path:
    configuracao = carregar_configuracao()
    return Path((configuracao or {}).get("raiz_workspace") or Path.cwd())


def pasta_administracao(semestre: Path) -> Path:
    candidatas = [pasta for pasta in workspace(semestre).listar(semestre)
                  if pasta.is_dir() and pasta.name.startswith("00 - ")]
    if not candidatas:
        raise ErroAcad("pasta-nao-encontrada", "Não encontrei a pasta de administração do semestre.")
    return candidatas[0]


def localizar_disciplina(ws: Workspace, semestre: Path, ident: str) -> Path:
    perfil_atual = perfil()
    identificador = sem_acento(ident)
    candidatas = []
    for pasta in disciplinas(ws, semestre, perfil_atual):
        correspondencia = perfil_atual.disciplina_pasta.match(pasta.name)
        codigo = ""
        arquivo = pasta / "01 - Planejamento" / "disciplina.yaml"
        if ws.existe(arquivo):
            documento = esquemas.carregar_yaml(ws.ler_texto(arquivo))
            codigo = documento.get("disciplina", {}).get("codigo", "")
        if (identificador == sem_acento(correspondencia["num"])
                or identificador == sem_acento(codigo)
                or identificador in sem_acento(correspondencia["nome"])):
            candidatas.append(pasta)
    if len(candidatas) != 1:
        raise ErroAcad("disciplina-nao-encontrada",
                       "Não encontrei uma disciplina única com esse nome ou código.")
    return candidatas[0]
