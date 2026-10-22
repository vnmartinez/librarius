import builtins
import os

import pytest

from acad.arquivos.privacidade import Workspace
from acad.erros import ErroAcad
from acad.perfil.perfil import carregar_perfil


@pytest.fixture
def ws(semestre_sintetico):
    return Workspace(semestre_sintetico, carregar_perfil().exclusao)


def test_excluidos_reconhecidos(ws, semestre_sintetico):
    semestre = semestre_sintetico
    assert ws.excluido(semestre / "2026 - Notas N1.gsheet")
    assert ws.excluido(semestre / "07 - TFC 1" / "02 - Alunos" / "Fulano" / "tcc.docx")
    assert ws.excluido(semestre / "11-Relatórios" / "rel.docx")
    assert ws.excluido(semestre / "01 - Disc A - 3º Período" / "04 - Projetos e Entregáveis" / "entrega-aluno.txt")
    assert not ws.excluido(semestre / "01 - Disc A - 3º Período" / "02 - Aulas")


def test_percorrer_nao_entra_em_excluidos(ws, semestre_sintetico, monkeypatch):
    tocados = []
    real_scandir = os.scandir

    def espiao(p="."):
        tocados.append(str(p))
        return real_scandir(p)

    monkeypatch.setattr(os, "scandir", espiao)
    nomes = {caminho.name for caminho in ws.percorrer(semestre_sintetico)}
    assert "Fulano" not in nomes and "tcc.docx" not in nomes and "rel.docx" not in nomes
    assert not any("02 - Alunos" in item or "Relatórios" in item or "Projetos e Entregáveis" in item for item in tocados)


def test_ler_excluido_falha_sem_abrir(ws, semestre_sintetico, monkeypatch):
    abertos = []
    real_open = builtins.open

    def espiao(arquivo, *args, **kwargs):
        abertos.append(str(arquivo))
        return real_open(arquivo, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", espiao)
    with pytest.raises(ErroAcad) as erro:
        ws.ler_bytes(semestre_sintetico / "2026 - Notas N1.gsheet")
    assert erro.value.codigo == "caminho-protegido"
    assert not any("Notas" in item for item in abertos)


def test_protegidas_contabilizadas(ws, semestre_sintetico):
    list(ws.percorrer(semestre_sintetico))
    assert "07 - TFC 1/02 - Alunos" in ws.protegidas
    assert not any("Fulano" in item for item in ws.protegidas)


def test_ignora_bloqueio_do_office(ws, semestre_sintetico):
    pasta = semestre_sintetico / "01 - Disc A - 3º Período" / "02 - Aulas"
    (pasta / "~$Aula 01 - X.pptx").write_text("")
    assert ws.listar(pasta) == []


def test_nao_le_fora_da_raiz(ws, semestre_sintetico):
    fora = semestre_sintetico.parent / "segredo.txt"
    fora.write_text("privado")
    with pytest.raises(ErroAcad):
        ws.ler_texto(fora)
