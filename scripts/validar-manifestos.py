"""Valida os manifestos de todos os hosts. Sai com 1 se houver problema."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from acad.plataformas import manifestos  # noqa: E402


def main() -> int:
    ruim = False
    for host, problemas in manifestos.validar_todos(RAIZ).items():
        if problemas:
            ruim = True
            print(f"{host}:")
            for p in problemas:
                print(f"  - {p}")
        else:
            print(f"{host}: ok")
    return 1 if ruim else 0


if __name__ == "__main__":
    sys.exit(main())
