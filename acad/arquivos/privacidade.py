from __future__ import annotations

import fnmatch
import os
from pathlib import Path
from typing import Iterable, Iterator

from acad.arquivos.caminhos import nfc, relativo_posix
from acad.erros import ErroAcad


class Workspace:
    """Única porta de leitura e listagem do workspace do professor."""

    def __init__(self, raiz: Path, exclusao: Iterable[str]):
        self.raiz = Path(raiz).resolve()
        self._padroes = tuple(nfc(padrao).lower() for padrao in exclusao)
        self.protegidas: set[str] = set()

    def _rel(self, caminho: Path) -> str | None:
        try:
            return relativo_posix(Path(caminho).absolute(), self.raiz)
        except ValueError:
            return None

    def excluido(self, caminho: Path) -> bool:
        caminho = Path(caminho)
        rel = self._rel(caminho)
        if rel is None or not caminho.resolve().is_relative_to(self.raiz):
            return True
        if rel == ".":
            return False
        partes = rel.lower().split("/")
        for indice in range(1, len(partes) + 1):
            prefixo, nome = "/".join(partes[:indice]), partes[indice - 1]
            for padrao in self._padroes:
                alvo = prefixo if "/" in padrao else nome
                if fnmatch.fnmatchcase(alvo, padrao):
                    return True
        return False

    def _primeiro_protegido(self, caminho: Path) -> str:
        partes = self._rel(caminho).split("/")
        for indice in range(1, len(partes) + 1):
            if self.excluido(self.raiz.joinpath(*partes[:indice])):
                return "/".join(partes[:indice])
        return "/".join(partes)

    def listar(self, pasta: Path) -> list[Path]:
        pasta = Path(pasta)
        if self.excluido(pasta):
            raise ErroAcad("caminho-protegido", "Essa pasta guarda dados protegidos e não é lida.", str(pasta))
        itens = []
        with os.scandir(pasta) as entradas:
            for entrada in entradas:
                caminho = pasta / entrada.name
                if entrada.name.startswith("~$"):
                    continue
                if self.excluido(caminho):
                    if entrada.is_dir(follow_symlinks=False):
                        self.protegidas.add(self._primeiro_protegido(caminho))
                    continue
                itens.append(caminho)
        return sorted(itens, key=lambda caminho: nfc(caminho.name))

    def percorrer(self, pasta: Path) -> Iterator[Path]:
        for caminho in self.listar(pasta):
            yield caminho
            if caminho.is_dir():
                yield from self.percorrer(caminho)

    def _checar(self, caminho: Path) -> Path:
        if self.excluido(caminho):
            raise ErroAcad("caminho-protegido", "Esse arquivo guarda dados protegidos e não é lido.", str(caminho))
        return Path(caminho)

    def ler_bytes(self, caminho: Path) -> bytes:
        with open(self._checar(caminho), "rb") as arquivo:
            return arquivo.read()

    def ler_texto(self, caminho: Path) -> str:
        return self.ler_bytes(caminho).decode("utf-8")

    def existe(self, caminho: Path) -> bool:
        return not self.excluido(caminho) and Path(caminho).exists()
