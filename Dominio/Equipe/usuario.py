from abc import ABC, abstractmethod
from Persistencia.FachadaBD.bancoDeDados import BancoDados

#Classe abstrata usuario
class Usuario(ABC):

    #Metodo construtor que sera chamado por integrante e gerente
    def __init__(self, nome, senha, email):
        self.nome = nome
        self.senha = senha
        self.email = email
        self.db = BancoDados()

    @abstractmethod
    def cadastrar(self):
        #Metodo abstrato que deve ser implementado por integrantes e gerentes em si
        pass