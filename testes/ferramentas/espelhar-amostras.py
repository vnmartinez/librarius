"""Espelha nomes para testes; lê conteúdo apenas do cronograma permitido."""

import sys
from pathlib import Path

from acad.arquivos.privacidade import Workspace
from acad.perfil.perfil import carregar_perfil

SEMESTRE = Path("2026") / "Segundo Semestre"
PASTAS = (
    "00 - Administração Acadêmica",
    "04 - Estrutura de Dados 2 - 5º Período",
    "09 - Modelos",
)
NAO_DESCER = {"node_modules", "assets", "referencia", ".git"}
COM_CONTEUDO = {"Cronograma - Estrutura de Dados 2.xlsx"}
IGNORAR_EXT = {".png", ".jpg", ".jpeg", ".svg", ".webp", ".ico"}


def espelhar(origem_fasoft: Path, destino_fasoft: Path) -> None:
    origem_fasoft = Path(origem_fasoft).resolve()
    destino_fasoft = Path(destino_fasoft).resolve()
    if destino_fasoft.is_relative_to(origem_fasoft):
        raise ValueError("Destino dentro da origem: operação recusada.")
    if destino_fasoft.exists() and any(destino_fasoft.iterdir()):
        raise ValueError("Destino já contém arquivos: operação recusada.")

    workspace = Workspace(origem_fasoft / SEMESTRE, carregar_perfil().exclusao)
    (destino_fasoft / SEMESTRE).mkdir(parents=True, exist_ok=True)
    (destino_fasoft / "AGENTS.md").write_bytes((origem_fasoft / "AGENTS.md").read_bytes())
    (destino_fasoft / SEMESTRE / "README.md").write_bytes(
        workspace.ler_bytes(origem_fasoft / SEMESTRE / "README.md")
    )

    def copiar(pasta: Path) -> None:
        for caminho in workspace.listar(pasta):
            alvo = destino_fasoft / caminho.relative_to(origem_fasoft)
            if caminho.is_dir():
                alvo.mkdir(parents=True, exist_ok=True)
                if caminho.name.lower() not in NAO_DESCER:
                    copiar(caminho)
            elif caminho.suffix.lower() not in IGNORAR_EXT:
                alvo.parent.mkdir(parents=True, exist_ok=True)
                alvo.write_bytes(workspace.ler_bytes(caminho) if caminho.name in COM_CONTEUDO else b"")

    for nome in PASTAS:
        (destino_fasoft / SEMESTRE / nome).mkdir(parents=True, exist_ok=True)
        copiar(origem_fasoft / SEMESTRE / nome)


if __name__ == "__main__":
    espelhar(Path(sys.argv[1]), Path(__file__).resolve().parents[1] / "amostras" / "fasoft")
