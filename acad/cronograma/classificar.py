def tipo_linha(aula: str, topico: str) -> str:
    aula_alta, topico_alto = aula.upper(), topico.upper()
    if any(palavra in aula_alta or palavra in topico_alto
           for palavra in ("FERIADO", "RECESSO", "SETECH", "SEM AULA")):
        return "sem-aula"
    if "AVALIA" in aula_alta or "AVALIA" in topico_alto or "PROVA" in topico_alto:
        return "avaliacao"
    return "aula"
