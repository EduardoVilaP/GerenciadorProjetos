from usuario import Usuario

#Classe referente a gerente, um tipo de usuario
class Integrante(Usuario):

    #Metodo construtor do gerente
    def __init__(self, nome, senha, email, pontos_de_esforco):
        super().__init__(nome, senha, email)
        self.pontos_de_esforco = pontos_de_esforco

    def cadastrar(self):
        self.db.registrarUsuario(self.nome, self.senha, self.email)
        self.db.registrarIntegrante(self.nome, self.senha, self.email, self.pontos_de_esforco)