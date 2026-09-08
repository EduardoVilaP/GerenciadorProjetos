from usuario import Usuario

#Classe referente a gerente, um tipo de usuario
class Gerente(Usuario):

    #Metodo construtor do gerente
    def __init__(self, nome, senha, email):
        super().__init__(nome, senha, email)

    def get_papel(self):
        return "Gerente"