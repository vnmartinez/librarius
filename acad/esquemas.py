from __future__ import annotations

import datetime as dt
import json
from functools import lru_cache
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from acad.erros import ErroAcad


def _dir_esquemas() -> Path:
    return Path(__file__).resolve().parents[1] / "esquemas"


@lru_cache
def carregar_esquema(nome: str) -> dict:
    return json.loads((_dir_esquemas() / f"{nome}.schema.json").read_text(encoding="utf-8"))


def _datas_para_texto(objeto):
    if isinstance(objeto, dict):
        return {chave: _datas_para_texto(valor) for chave, valor in objeto.items()}
    if isinstance(objeto, list):
        return [_datas_para_texto(valor) for valor in objeto]
    if isinstance(objeto, (dt.date, dt.datetime)):
        return objeto.isoformat()
    return objeto


def carregar_yaml(texto: str) -> dict:
    return _datas_para_texto(yaml.safe_load(texto) or {})


def para_yaml(documento: dict) -> str:
    return yaml.safe_dump(documento, allow_unicode=True, sort_keys=False)


def validar(nome: str, documento: dict) -> list[str]:
    validador = Draft202012Validator(carregar_esquema(nome))
    erros = []
    for erro in sorted(validador.iter_errors(documento), key=lambda item: str(list(item.absolute_path))):
        campo = ".".join(
            str(parte) if not isinstance(parte, int) else f"[{parte}]"
            for parte in erro.absolute_path
        ).replace(".[", "[")
        erros.append(f"campo `{campo or '(raiz)'}`: {erro.message}")
    return erros


def validar_ou_falhar(nome: str, documento: dict) -> None:
    erros = validar(nome, documento)
    if erros:
        raise ErroAcad(
            "esquema-invalido",
            "Um arquivo de planejamento está com informação inválida.",
            "; ".join(erros),
            saida=1,
        )
