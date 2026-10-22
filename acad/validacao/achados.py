from dataclasses import asdict, dataclass
from typing import Literal


@dataclass(frozen=True)
class Achado:
    codigo: str
    nivel: Literal["erro", "aviso", "info"]
    mensagem: str
    caminho: str = ""

    def para_dict(self) -> dict:
        return asdict(self)
