"""
Modulo que define a entidade Integrante, herdando de Usuario.
"""

from usuario import Usuario

class Integrante(Usuario):
    """Representa um usuario com perfil de Integrante na equipe, contendo controle de pontos de esforco."""

    def __init__(self, nome, senha, email, pontos_de_esforco):
        """Inicializa um novo integrante com dados basicos e pontos de esforco iniciais."""
        super().__init__(nome, senha, email)
        self.__pontos_de_esforco = pontos_de_esforco

    def get_pontos_de_esforco(self):
        """Retorna a quantidade atual de pontos de esforco do integrante."""
        return self.__pontos_de_esforco

    def set_pontos_de_esforco(self, novo_limite):
        """Atualiza os pontos de esforco validando se o valor nao e negativo."""
        if novo_limite >= 0:
            self.__pontos_de_esforco = novo_limite
        else:
            raise ValueError("O limite de esforco nao pode ser negativo.")

    def get_papel(self):
        """Retorna a string identificadora do papel deste usuario."""
        return "Integrante"