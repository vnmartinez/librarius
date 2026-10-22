import json

from acad.config import dir_dados


def _arquivo():
    pasta = dir_dados()
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta / "diario.jsonl"


def registrar(entrada: dict) -> None:
    with open(_arquivo(), "a", encoding="utf-8") as diario:
        diario.write(json.dumps(entrada, ensure_ascii=False) + "\n")


def _todas() -> list[dict]:
    arquivo = _arquivo()
    return [json.loads(linha) for linha in arquivo.read_text(encoding="utf-8").splitlines() if linha] if arquivo.exists() else []


def ultima_aplicada() -> dict | None:
    entradas = _todas()
    desfeitas = {entrada["id"] for entrada in entradas if entrada.get("tipo") == "desfeita"}
    for entrada in reversed(entradas):
        if entrada.get("tipo") == "aplicada" and entrada["id"] not in desfeitas:
            return entrada
    return None


def ja_aplicada(id: str) -> bool:
    return any(entrada.get("tipo") == "aplicada" and entrada["id"] == id for entrada in _todas())


def marcar_desfeita(id: str) -> None:
    registrar({"tipo": "desfeita", "id": id})
