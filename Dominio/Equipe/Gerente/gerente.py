from usuario import Usuario

#Classe referente a gerente, um tipo de usuario
class Gerente(Usuario):

    #Metodo construtor do gerente
    def __init__(self, nome, senha, email):
        super().__init__(nome, senha, email)

    def cadastrar(self):
        self.db.registrarUsuario(self.nome, self.senha, self.email)
        self.db.registrarGerente(self.nome, self.senha, self.email)