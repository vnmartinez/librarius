from __future__ import annotations

import hashlib
import json
from pathlib import Path

from acad import esquemas
from acad.arquivos.caminhos import nfc, relativo_posix
from acad.arquivos.privacidade import Workspace


def hash_bytes(conteudo: bytes) -> str:
    return "sha256:" + hashlib.sha256(conteudo).hexdigest()


def hash_item(obj: dict, ignorar: tuple[str, ...] = ("manifesto",)) -> str:
    filtrado = {chave: valor for chave, valor in obj.items() if chave not in ignorar}
    canonico = json.dumps(filtrado, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hash_bytes(canonico.encode("utf-8"))


def hash_pasta(ws: Workspace, pasta: Path) -> str:
    registros = []

    def visitar(atual: Path) -> None:
        for caminho in ws.listar(atual):
            if caminho.name.startswith("~$") or caminho.name.lower() in {"node_modules", ".git"}:
                continue
            if caminho.is_dir():
                visitar(caminho)
            elif caminho.is_file():
                registros.append([relativo_posix(caminho, pasta), hash_bytes(ws.ler_bytes(caminho))])

    visitar(Path(pasta))
    registros.sort(key=lambda item: nfc(item[0]))
    canonico = json.dumps(registros, ensure_ascii=False, separators=(",", ":"))
    return hash_bytes(canonico.encode("utf-8"))


def hash_entrada(ws: Workspace, semestre: Path, chave: str,
                 itens: dict[str, dict] | None = None) -> str | None:
    caminho, separador, id_item = chave.partition("#")
    arquivo = Path(semestre) / caminho
    if not ws.existe(arquivo):
        return None
    if separador:
        if itens is not None and id_item in itens:
            return hash_item(itens[id_item])
        documento = esquemas.carregar_yaml(ws.ler_texto(arquivo))
        for item in documento.get("aulas", []):
            if item.get("id") == id_item:
                return hash_item(item)
        return None
    if arquivo.is_dir():
        return hash_pasta(ws, arquivo)
    return hash_bytes(ws.ler_bytes(arquivo))
