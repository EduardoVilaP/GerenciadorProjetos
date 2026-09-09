"""
Modulo que define a classe abstrata Usuario, base para os perfis do sistema.
"""

from abc import ABC, abstractmethod

class Usuario(ABC):
    """Classe base abstrata que define os atributos e metodos comuns a todos os usuarios."""

    def __init__(self, nome, senha, email):
        """Inicializa os atributos privados de identificacao e credenciais do usuario."""
        self.__nome = nome
        self.__senha = senha
        self.__email = email

    def get_nome(self):
        """Retorna o nome cadastrado do usuario."""
        return self.__nome
        
    def get_email(self):
        """Retorna o endereco de email do usuario."""
        return self.__email

    def validar_senha(self, senha_teste):
        """Compara a senha fornecida com a senha armazenada, retornando True se forem iguais."""
        return self.__senha == senha_teste

    @abstractmethod
    def get_papel(self):
        """Metodo abstrato que devera ser implementado pelas classes filhas para retornar o papel do usuario."""
        pass