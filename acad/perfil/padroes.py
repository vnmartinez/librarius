"""Valores que o MVP usava fixos no codigo para perfis sem estrutura."""

ESTRUTURA_V1 = {
    "semestre": r"^(?P<ano>\d{4})/(?P<periodo>Primeiro|Segundo) Semestre$",
    "periodos": {"Primeiro": 1, "Segundo": 2},
    "administracao": r"^00 - ",
    "papeis": {
        "planejamento": "01 - Planejamento",
        "aulas": "02 - Aulas",
        "atividades": "03 - Atividades e Listas",
        "projetos": "04 - Projetos e Entregáveis",
        "referencias": "05 - Materiais de Referência",
        "codigo": "06 - Código e Exemplos",
        "arquivo": "99 - Arquivo",
    },
}
