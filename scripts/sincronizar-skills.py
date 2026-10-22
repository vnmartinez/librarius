"""Reescreve (ou só confere, com --verificar) o trecho comum em todas as skills."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from acad.plataformas import skills  # noqa: E402


def main(argv: list[str]) -> int:
    verificar = "--verificar" in argv
    trecho = skills.trecho_comum()
    novo_bloco = f"{skills.INICIO}\n{trecho}\n{skills.FIM}"
    divergentes = []
    for pasta in sorted((RAIZ / "skills").glob("*/")):
        arq = pasta / "SKILL.md"
        texto = arq.read_text(encoding="utf-8")
        if skills.INICIO in texto and skills.FIM in texto:
            antes, resto = texto.split(skills.INICIO, 1)
            depois = resto.split(skills.FIM, 1)[1]
            atualizado = antes + novo_bloco + depois
        else:
            atualizado = texto.rstrip("\n") + "\n\n" + novo_bloco + "\n"
        if atualizado != texto:
            divergentes.append(pasta.name)
            if not verificar:
                arq.write_text(atualizado, encoding="utf-8", newline="\n")
    if verificar and divergentes:
        print("Fora de sincronia: " + ", ".join(divergentes))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
