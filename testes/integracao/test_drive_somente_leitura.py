import builtins
import json
import os
from pathlib import Path

import pytest

from acad.cli import main


DRIVE = Path(r"G:\Meu Drive\Fasoft\2026\Segundo Semestre")


@pytest.mark.drive
def test_validar_drive_real_sem_escrever(capsys, monkeypatch):
    if not DRIVE.exists():
        pytest.skip("Drive ausente")
    real_open = builtins.open

    def open_so_leitura(arquivo, mode="r", *args, **kwargs):
        if str(arquivo).lower().startswith("g:") and any(flag in mode for flag in "wax+"):
            raise AssertionError(f"tentativa de escrita no Drive: {arquivo}")
        return real_open(arquivo, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", open_so_leitura)
    for nome in ("replace", "rename", "remove", "unlink", "mkdir", "makedirs", "rmdir"):
        original = getattr(os, nome)

        def bloquear_destino(*args, _original=original, _nome=nome, **kwargs):
            if any(str(arg).lower().startswith("g:") for arg in args[:2]):
                raise AssertionError(f"tentativa de {_nome} no Drive")
            return _original(*args, **kwargs)

        monkeypatch.setattr(os, nome, bloquear_destino)
    main(["validar", "--raiz", str(DRIVE), "--json"])
    dados = json.loads(capsys.readouterr().out)
    codigos = {(item["codigo"], item["caminho"].split("/")[-1])
               for item in dados["dados"]["achados"]}
    assert ("sufixo-proibido", "Cronograma - Estrutura de Dados 2.xlsx.bak") in codigos
    assert ("pasta-sem-prefixo", "11-Relatórios") in codigos
    assert ("pasta-sem-prefixo", "_ferramentas") in codigos
    assert any(codigo == "readme-desatualizado" for codigo, _ in codigos)
    assert "02 - Alunos" not in json.dumps(dados, ensure_ascii=False)
