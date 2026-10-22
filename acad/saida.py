from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field


@dataclass
class Resultado:
    ok: bool
    mensagem: str
    dados: dict = field(default_factory=dict)
    avisos: list[str] = field(default_factory=list)
    erros: list[dict] = field(default_factory=list)
    proposta: dict | None = None

    def para_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2, default=str)

    def para_texto(self) -> str:
        linhas = [self.mensagem]
        linhas += [f"• {aviso}" for aviso in self.avisos]
        linhas += [f"✗ {erro['mensagem']}" for erro in self.erros]
        if self.proposta:
            linhas.append(self.proposta.get("resumo", ""))
        return "\n".join(linha for linha in linhas if linha)
