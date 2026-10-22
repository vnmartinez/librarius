from datetime import date, timedelta

from acad.encontros.carga import em_unidade, minutos_validos, verificar_carga
from acad.encontros.gerar import Encontro


def _encontros(quantidade, status="previsto"):
    return [Encontro(f"E{indice:02d}", date(2026, 8, 3) + timedelta(days=indice),
                     "19:00", "20:40", status, [], "conteudo", "horario")
            for indice in range(1, quantidade + 1)]


def test_cancelados_nao_contam():
    assert minutos_validos(_encontros(3) + _encontros(2, "cancelado")) == 300


def test_unidades():
    assert em_unidade(3600, "hora_relogio", None) == 60
    assert em_unidade(3600, "hora_aula", 50) == 72


def test_36_encontros_de_100_min_fecham_60h():
    assert verificar_carga(_encontros(36), {"valor": 60, "unidade": "hora_relogio", "minutos_hora_aula": None}) == []


def test_falta_carga():
    [achado] = verificar_carga(_encontros(30), {"valor": 60, "unidade": "hora_relogio", "minutos_hora_aula": None})
    assert achado.codigo == "carga-horaria-incompativel" and "faltam 10" in achado.mensagem


def test_hora_aula_50():
    assert verificar_carga(_encontros(36), {"valor": 72, "unidade": "hora_aula", "minutos_hora_aula": 50}) == []


def test_unidade_nula_usa_o_padrao_do_perfil():
    padrao = {"unidade": "hora_aula", "minutos_hora_aula": 50}
    assert verificar_carga(_encontros(36), {"valor": 72, "unidade": None, "minutos_hora_aula": None}, padrao) == []
    [achado] = verificar_carga(_encontros(36), {"valor": 60, "unidade": None, "minutos_hora_aula": None}, padrao)
    assert achado.codigo == "carga-horaria-incompativel" and achado.nivel == "erro"


def test_sem_unidade_em_lugar_nenhum_ainda_avisa():
    [achado] = verificar_carga(_encontros(36), {"valor": 60, "unidade": None, "minutos_hora_aula": None})
    assert achado.codigo == "carga-unidade-nao-confirmada" and achado.nivel == "aviso"
