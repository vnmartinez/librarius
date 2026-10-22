"""Gera dist/chatgpt/<skill>.zip para enviar ao ChatGPT."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from acad.plataformas import chatgpt  # noqa: E402

if __name__ == "__main__":
    for z in chatgpt.empacotar(RAIZ, RAIZ / "dist" / "chatgpt"):
        print(z.name)
