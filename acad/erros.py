class ErroAcad(Exception):
    """Erro com mensagem simples ao professor."""

    def __init__(
        self, codigo: str, mensagem: str, detalhe_tecnico: str = "", saida: int = 2
    ):
        super().__init__(mensagem)
        self.codigo = codigo
        self.mensagem = mensagem
        self.detalhe_tecnico = detalhe_tecnico
        self.saida = saida
