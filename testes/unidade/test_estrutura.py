from acad.arquivos.privacidade import Workspace
from acad.perfil.perfil import carregar_perfil
from acad.validacao.estrutura import pastas_do_readme, validar_estrutura

README = """# Organização
## Estrutura principal
```text
Segundo Semestre/
├── 00 - Administração Acadêmica/
├── 06 - TFC 1/
└── 08 - Modelos/
```
## Estrutura padrão das disciplinas
```text
[Disciplina]/
├── 01 - Planejamento/
```
"""


def test_le_so_estrutura_principal():
    assert pastas_do_readme(README) == ["00 - Administração Acadêmica", "06 - TFC 1", "08 - Modelos"]


def test_readme_desatualizado(semestre_sintetico):
    (semestre_sintetico / "README.md").write_text(README, encoding="utf-8")
    perfil = carregar_perfil("fasoft")
    workspace = Workspace(semestre_sintetico, perfil.exclusao)
    achados = [achado for achado in validar_estrutura(workspace, semestre_sintetico, perfil)
               if achado.codigo == "readme-desatualizado"]
    assert len(achados) == 1
    assert "09 - Modelos" in achados[0].mensagem and "08 - Modelos" in achados[0].mensagem


def test_subpasta_ausente(semestre_sintetico):
    (semestre_sintetico / "01 - Disc A - 3º Período" / "05 - Materiais de Referência").rmdir()
    perfil = carregar_perfil("fasoft")
    workspace = Workspace(semestre_sintetico, perfil.exclusao)
    achados = validar_estrutura(workspace, semestre_sintetico, perfil)
    assert any(achado.codigo == "subpasta-padrao-ausente" and "05 - Materiais de Referência" in achado.mensagem
               for achado in achados)


def test_pasta_protegida_conta_como_existente(semestre_sintetico):
    perfil = carregar_perfil("fasoft")
    workspace = Workspace(semestre_sintetico, perfil.exclusao)
    achados = validar_estrutura(workspace, semestre_sintetico, perfil)
    mensagem = next(achado.mensagem for achado in achados if achado.codigo == "readme-desatualizado")
    assert "11-Relatórios" in mensagem


def test_subpasta_protegida_existente_nao_e_ausente(semestre_sintetico):
    perfil = carregar_perfil("fasoft")
    workspace = Workspace(semestre_sintetico, perfil.exclusao)
    achados = validar_estrutura(workspace, semestre_sintetico, perfil)
    assert not any(
        achado.codigo == "subpasta-padrao-ausente" and "04 - Projetos e Entregáveis" in achado.mensagem
        for achado in achados
    )
