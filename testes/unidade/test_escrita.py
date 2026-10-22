from pathlib import Path

import pytest

from acad.arquivos.escrita import Operacao, aplicar, criar_proposta, desfazer, pasta_arquivo_para
from acad.erros import ErroAcad
from acad.perfil.perfil import carregar_perfil

PERFIL = carregar_perfil()
DISCIPLINA = "01 - Disc A - 3º Período"


def test_proposta_nao_grava_nada(semestre_sintetico):
    alvo = semestre_sintetico / DISCIPLINA / "02 - Aulas" / "Aula 01 - Intro.md"
    criar_proposta(semestre_sintetico, [Operacao("criar", f"{DISCIPLINA}/02 - Aulas/Aula 01 - Intro.md", b"oi", "roteiro")], "1 arquivo")
    assert not alvo.exists()


def test_aplicar_cria(semestre_sintetico):
    proposta = criar_proposta(semestre_sintetico, [Operacao("criar", f"{DISCIPLINA}/02 - Aulas/Aula 01 - Intro.md", b"oi")], "x")
    aplicar(proposta["id"], PERFIL)
    assert (semestre_sintetico / DISCIPLINA / "02 - Aulas" / "Aula 01 - Intro.md").read_bytes() == b"oi"


def test_substituir_arquiva_anterior(semestre_sintetico):
    arquivo = semestre_sintetico / DISCIPLINA / "02 - Aulas" / "Aula 01 - Intro.md"
    arquivo.write_bytes(b"v1")
    proposta = criar_proposta(semestre_sintetico, [Operacao("substituir", f"{DISCIPLINA}/02 - Aulas/Aula 01 - Intro.md", b"v2")], "x")
    aplicar(proposta["id"], PERFIL)
    assert arquivo.read_bytes() == b"v2"
    assert (semestre_sintetico / DISCIPLINA / "99 - Arquivo" / "Aula 01 - Intro.md").read_bytes() == b"v1"


def test_colisao_no_arquivo_morto(semestre_sintetico):
    arquivo = semestre_sintetico / DISCIPLINA / "02 - Aulas" / "Aula 01 - Intro.md"
    arquivo.write_bytes(b"v1")
    (semestre_sintetico / DISCIPLINA / "99 - Arquivo" / "Aula 01 - Intro.md").write_bytes(b"v0")
    proposta = criar_proposta(semestre_sintetico, [Operacao("substituir", f"{DISCIPLINA}/02 - Aulas/Aula 01 - Intro.md", b"v2")], "x")
    aplicar(proposta["id"], PERFIL)
    arquivados = sorted(arquivo.name for arquivo in (semestre_sintetico / DISCIPLINA / "99 - Arquivo").iterdir())
    assert len(arquivados) == 2 and any(" - anterior " in nome for nome in arquivados)


def test_desfazer_restaura(semestre_sintetico):
    arquivo = semestre_sintetico / DISCIPLINA / "02 - Aulas" / "Aula 01 - Intro.md"
    arquivo.write_bytes(b"v1")
    proposta = criar_proposta(semestre_sintetico, [
        Operacao("substituir", f"{DISCIPLINA}/02 - Aulas/Aula 01 - Intro.md", b"v2"),
        Operacao("criar", f"{DISCIPLINA}/02 - Aulas/Aula 02 - B.md", b"b"),
    ], "x")
    aplicar(proposta["id"], PERFIL)
    desfazer(PERFIL)
    assert arquivo.read_bytes() == b"v1"
    assert not (semestre_sintetico / DISCIPLINA / "02 - Aulas" / "Aula 02 - B.md").exists()
    assert not (semestre_sintetico / DISCIPLINA / "99 - Arquivo" / "Aula 01 - Intro.md").exists()


def test_desfazer_nao_apaga_arquivo_editado_depois(semestre_sintetico):
    proposta = criar_proposta(semestre_sintetico, [Operacao("criar", f"{DISCIPLINA}/02 - Aulas/Aula 02 - B.md", b"b")], "x")
    aplicar(proposta["id"], PERFIL)
    (semestre_sintetico / DISCIPLINA / "02 - Aulas" / "Aula 02 - B.md").write_bytes(b"editado pelo professor")
    desfazer(PERFIL)
    assert any(arquivo.read_bytes() == b"editado pelo professor"
               for arquivo in (semestre_sintetico / DISCIPLINA / "99 - Arquivo").iterdir())


@pytest.mark.parametrize("destino", ["../fora.txt", "C:/fora.txt"])
def test_destino_fora_da_raiz(semestre_sintetico, destino):
    with pytest.raises(ErroAcad):
        criar_proposta(semestre_sintetico, [Operacao("criar", destino, b"x")], "x")


def test_criar_sobre_existente_recusa(semestre_sintetico):
    with pytest.raises(ErroAcad):
        criar_proposta(semestre_sintetico, [Operacao("criar", "README.md", b"y")], "x")


def test_escrita_no_drive_bloqueada(monkeypatch, tmp_path):
    monkeypatch.setenv("ACAD_BLOQUEAR_ESCRITA", str(tmp_path))
    (tmp_path / "s").mkdir()
    proposta = criar_proposta(tmp_path / "s", [Operacao("criar", "a.txt", b"x")], "x")
    with pytest.raises(ErroAcad) as erro:
        aplicar(proposta["id"], PERFIL)
    assert erro.value.codigo == "escrita-bloqueada" and not (tmp_path / "s" / "a.txt").exists()


def test_pasta_arquivo_sem_99_usa_primeiro_nivel(semestre_sintetico):
    destino = semestre_sintetico / "08 - Avaliações" / "N1" / "x.tex"
    assert pasta_arquivo_para(semestre_sintetico, destino, PERFIL) == semestre_sintetico / "08 - Avaliações" / "99 - Arquivo"


def test_proposta_aplicada_duas_vezes(semestre_sintetico):
    proposta = criar_proposta(semestre_sintetico, [Operacao("criar", "a.txt", b"x")], "x")
    aplicar(proposta["id"], PERFIL)
    with pytest.raises(ErroAcad):
        aplicar(proposta["id"], PERFIL)


def test_conteudo_alterado_na_proposta_nao_move_original(semestre_sintetico):
    from acad.config import dir_dados

    arquivo = semestre_sintetico / DISCIPLINA / "02 - Aulas" / "Aula 01 - Intro.md"
    arquivo.write_bytes(b"original")
    proposta = criar_proposta(semestre_sintetico, [Operacao("substituir", f"{DISCIPLINA}/02 - Aulas/Aula 01 - Intro.md", b"novo")], "x")
    (dir_dados() / "propostas" / proposta["id"] / "arquivos" / "0").write_bytes(b"alterado")
    with pytest.raises(ErroAcad):
        aplicar(proposta["id"], PERFIL)
    assert arquivo.read_bytes() == b"original"


def test_proposta_com_destinos_duplicados_e_recusada(semestre_sintetico):
    with pytest.raises(ErroAcad):
        criar_proposta(semestre_sintetico, [
            Operacao("criar", "novo.txt", b"a"),
            Operacao("criar", "novo.txt", b"b"),
        ], "x")
