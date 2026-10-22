import json
from pathlib import Path

from acad.cli import main


SEM = Path(__file__).resolve().parents[1] / "amostras/fasoft/2026/Segundo Semestre"


def test_validar_amostra(capsys, perfil_fasoft):
    code = main(["validar", "--raiz", str(SEM), "--json"])
    dados = json.loads(capsys.readouterr().out)
    codigos = {achado["codigo"] for achado in dados["dados"]["achados"]}
    assert code == 1
    assert {"sufixo-proibido", "pasta-sem-prefixo", "nome-lista-sem-prefixo",
            "readme-desatualizado", "numero-aula-repetido"} <= codigos


def test_validar_uma_disciplina(capsys, perfil_fasoft):
    main(["validar", "04", "--raiz", str(SEM), "--json"])
    dados = json.loads(capsys.readouterr().out)
    assert all("Recepção" not in achado["caminho"] for achado in dados["dados"]["achados"])


def test_yaml_invalido_nao_derruba(capsys, semestre_sintetico):
    arquivo = semestre_sintetico / "01 - Disc A - 3º Período" / "01 - Planejamento" / "aulas.yaml"
    arquivo.write_text("aulas: 3\n", encoding="utf-8")
    main(["validar", "--raiz", str(semestre_sintetico), "--json"])
    dados = json.loads(capsys.readouterr().out)
    codigos = {achado["codigo"] for achado in dados["dados"]["achados"]}
    assert "esquema-invalido" in codigos
    assert "pasta-sem-prefixo" in codigos
