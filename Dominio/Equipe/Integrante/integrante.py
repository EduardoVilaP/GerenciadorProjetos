from usuario import Usuario

#Classe referente a gerente, um tipo de usuario
class Integrante(Usuario):

    #Metodo construtor do gerente
    def __init__(self, nome, senha, email, pontos_de_esforco):
        super().__init__(nome, senha, email)
        self.pontos_de_esforco = pontos_de_esforco

    def get_pontos_de_esforco(self):
        return self.__pontos_de_esforco

    def set_pontos_de_esforco(self, novo_limite):
        if novo_limite >= 0:
            self.__pontos_de_esforco = novo_limite
        else:
            raise ValueError("O limite de esforco nao pode ser negativo.")

    def get_papel(self):
        return "Integrante"