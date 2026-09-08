from abc import ABC, abstractmethod

#Classe abstrata usuario
class Usuario(ABC):

    # Metodo construtor que sera chamado por integrante e gerente
    def __init__(self, nome, senha, email):
        self.__nome = nome
        self.__senha = senha
        self.__email = email

    def get_nome(self):
        return self.__nome
        
    def get_email(self):
        return self.__email

    def validar_senha(self, senha_teste):
        return self.__senha == senha_teste

    @abstractmethod
    def get_papel(self):
        # Classes filhas retornam seu papel
        pass