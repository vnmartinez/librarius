"""Uso: sincronizar-versao.py <nova versão>   |   sincronizar-versao.py --verificar [--raiz PASTA]"""
import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from acad.plataformas import versao  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("nova", nargs="?")
    ap.add_argument("--verificar", action="store_true")
    ap.add_argument("--raiz", default=str(RAIZ))
    a = ap.parse_args()
    raiz = Path(a.raiz)
    if a.nova:
        versao.aplicar(raiz, a.nova)
    atuais = versao.ler_todas(raiz)
    if len(set(atuais.values())) > 1:
        print("Mais de uma versão:")
        for arq, v in atuais.items():
            print(f"  {arq}: {v}")
        return 1
    print(next(iter(atuais.values())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
