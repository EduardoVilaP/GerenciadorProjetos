"""
Modulo que define a entidade Gerente, herdando de Usuario.
"""

from usuario import Usuario

class Gerente(Usuario):
    """Representa um usuario com perfil de Gerente no sistema."""

    def __init__(self, nome, senha, email):
        """Inicializa um novo gerente chamando o construtor da classe pai (Usuario)."""
        super().__init__(nome, senha, email)

    def get_papel(self):
        """Retorna a string identificadora do papel deste usuario."""
        return "Gerente"