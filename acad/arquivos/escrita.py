from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from secrets import token_hex
from typing import Literal

from acad.arquivos import diario
from acad.config import dir_dados
from acad.erros import ErroAcad


@dataclass
class Operacao:
    tipo: Literal["criar", "substituir", "arquivar", "criar-pasta"]
    destino: str
    conteudo: bytes | None = None
    resumo: str = ""


def _alvo(raiz: Path, destino: str) -> Path:
    relativo = PurePosixPath(destino)
    if (not destino or "\\" in destino or re.match(r"^[A-Za-z]:", destino)
            or relativo.is_absolute() or ".." in relativo.parts or "." in relativo.parts):
        raise ErroAcad("destino-invalido", "O destino do arquivo está fora da pasta escolhida.")
    alvo = raiz.joinpath(*relativo.parts).resolve()
    if not alvo.is_relative_to(raiz.resolve()) or alvo == raiz.resolve():
        raise ErroAcad("destino-invalido", "O destino do arquivo está fora da pasta escolhida.")
    return alvo


def _bloqueio(raiz: Path) -> None:
    atual = str(raiz.resolve()).lower().replace("\\", "/")
    for prefixo in os.environ.get("ACAD_BLOQUEAR_ESCRITA", "").split(";"):
        normal = prefixo.strip().lower().replace("\\", "/")
        if normal and atual.startswith(normal):
            raise ErroAcad("escrita-bloqueada", "Essa pasta está protegida contra alterações.")


def _hash(conteudo: bytes) -> str:
    return "sha256:" + hashlib.sha256(conteudo).hexdigest()


def _pasta_proposta(id: str) -> Path:
    if not re.fullmatch(r"\d{8}-\d{6}-[0-9a-f]{4}", id):
        raise ErroAcad("proposta-invalida", "Não encontrei essa proposta.")
    return dir_dados() / "propostas" / id


def criar_proposta(raiz: Path, operacoes: list[Operacao], resumo: str) -> dict:
    raiz = Path(raiz).resolve()
    itens = []
    destinos = set()
    for operacao in operacoes:
        destino = _alvo(raiz, operacao.destino)
        if destino in destinos:
            raise ErroAcad("destino-duplicado", "A proposta repete o mesmo destino.")
        destinos.add(destino)
        if operacao.tipo not in ("criar", "substituir", "arquivar", "criar-pasta"):
            raise ErroAcad("operacao-invalida", "Não reconheci a alteração proposta.")
        if operacao.tipo in ("criar", "criar-pasta") and destino.exists():
            raise ErroAcad("arquivo-existente", "Já existe um arquivo ou pasta com esse nome.")
        if operacao.tipo in ("substituir", "arquivar") and not destino.exists():
            raise ErroAcad("arquivo-ausente", "Não encontrei o arquivo que seria alterado.")
        if operacao.tipo in ("criar", "substituir") and operacao.conteudo is None:
            raise ErroAcad("conteudo-ausente", "Falta o conteúdo do novo arquivo.")
        itens.append({
            "tipo": operacao.tipo, "destino": operacao.destino,
            "resumo": operacao.resumo,
            "sha256": _hash(operacao.conteudo) if operacao.conteudo is not None else None,
        })

    id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + token_hex(2)
    pasta = _pasta_proposta(id)
    (pasta / "arquivos").mkdir(parents=True)
    for indice, operacao in enumerate(operacoes):
        if operacao.conteudo is not None:
            (pasta / "arquivos" / str(indice)).write_bytes(operacao.conteudo)
    documento = {
        "id": id, "raiz": str(raiz), "resumo": resumo,
        "criada_em": datetime.now().isoformat(timespec="seconds"), "itens": itens,
    }
    (pasta / "proposta.json").write_text(json.dumps(documento, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"id": id, "resumo": resumo,
            "itens": [{chave: item[chave] for chave in ("tipo", "destino", "resumo")} for item in itens]}


def pasta_arquivo_para(raiz: Path, destino: Path, perfil) -> Path:
    raiz = Path(raiz).resolve()
    destino = Path(destino).resolve()
    if not destino.is_relative_to(raiz):
        raise ErroAcad("destino-invalido", "O destino do arquivo está fora da pasta escolhida.")
    atual = destino.parent
    while atual.is_relative_to(raiz):
        candidato = atual / perfil.pasta_arquivo
        if candidato.is_dir():
            return candidato
        if atual == raiz:
            break
        atual = atual.parent
    partes = destino.relative_to(raiz).parts
    return raiz / partes[0] / perfil.pasta_arquivo if len(partes) > 1 else raiz / perfil.pasta_arquivo


def _arquivar(raiz: Path, destino: Path, perfil) -> Path:
    pasta = pasta_arquivo_para(raiz, destino, perfil)
    pasta.mkdir(parents=True, exist_ok=True)
    alvo = pasta / destino.name
    if alvo.exists():
        data = datetime.now().strftime("%Y-%m-%d")
        alvo = pasta / f"{destino.stem} - anterior {data}{destino.suffix}"
        numero = 2
        while alvo.exists():
            alvo = pasta / f"{destino.stem} - anterior {data} ({numero}){destino.suffix}"
            numero += 1
    os.rename(destino, alvo)
    return alvo


def aplicar(id: str, perfil) -> list[str]:
    pasta = _pasta_proposta(id)
    arquivo = pasta / "proposta.json"
    if not arquivo.exists():
        raise ErroAcad("proposta-invalida", "Não encontrei essa proposta.")
    if diario.ja_aplicada(id):
        raise ErroAcad("proposta-aplicada", "Essa alteração já foi feita.")
    documento = json.loads(arquivo.read_text(encoding="utf-8"))
    raiz = Path(documento["raiz"]).resolve()
    _bloqueio(raiz)
    historico = []
    resultados = []
    preparados = []
    for indice, item in enumerate(documento["itens"]):
        destino = _alvo(raiz, item["destino"])
        tipo = item["tipo"]
        if tipo not in ("criar", "substituir", "arquivar", "criar-pasta"):
            raise ErroAcad("proposta-invalida", "Não reconheci essa proposta.")
        if tipo in ("criar", "criar-pasta") and destino.exists():
            raise ErroAcad("arquivo-existente", "Já existe um arquivo ou pasta com esse nome.")
        if tipo in ("substituir", "arquivar") and not destino.exists():
            raise ErroAcad("arquivo-ausente", "Não encontrei o arquivo que seria alterado.")
        conteudo = None
        if tipo in ("criar", "substituir"):
            conteudo = (pasta / "arquivos" / str(indice)).read_bytes()
            if _hash(conteudo) != item["sha256"]:
                raise ErroAcad("proposta-invalida", "O arquivo da proposta mudou. Faça uma nova proposta.")
        preparados.append((item, destino, conteudo))

    for item, destino, conteudo in preparados:
        tipo = item["tipo"]
        if tipo in ("substituir", "arquivar"):
            morto = _arquivar(raiz, destino, perfil)
            historico.append({"acao": "arquivado", "destino": item["destino"],
                              "arquivo_morto": str(morto)})
        if tipo in ("criar", "substituir"):
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(conteudo)
            historico.append({"acao": "criado", "destino": item["destino"], "sha256": item["sha256"]})
        if tipo == "criar-pasta":
            if destino.exists():
                raise ErroAcad("arquivo-existente", "Já existe um arquivo ou pasta com esse nome.")
            destino.mkdir(parents=True)
            historico.append({"acao": "pasta-criada", "destino": item["destino"]})
        resultados.append(item["destino"])
    diario.registrar({"tipo": "aplicada", "id": id, "raiz": str(raiz), "itens": historico})
    return resultados


def desfazer(perfil) -> list[str]:
    entrada = diario.ultima_aplicada()
    if entrada is None:
        return []
    raiz = Path(entrada["raiz"]).resolve()
    _bloqueio(raiz)
    resultados = []
    for item in reversed(entrada["itens"]):
        destino = _alvo(raiz, item["destino"])
        if item["acao"] == "criado" and destino.exists():
            if _hash(destino.read_bytes()) == item["sha256"]:
                destino.unlink()
            else:
                _arquivar(raiz, destino, perfil)
        elif item["acao"] == "arquivado":
            morto = Path(item["arquivo_morto"])
            if destino.exists():
                _arquivar(raiz, destino, perfil)
            if morto.exists():
                destino.parent.mkdir(parents=True, exist_ok=True)
                os.rename(morto, destino)
        elif item["acao"] == "pasta-criada" and destino.is_dir():
            try:
                destino.rmdir()
            except OSError:
                pass
        resultados.append(item["destino"])
    diario.marcar_desfeita(entrada["id"])
    return resultados
