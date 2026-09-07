

#Criando um singleton para servir como banco de dados enquannto o programa esta rodando
class BancoDados:

    instancia = None

    #Metodo responsavel pela unica instanciacao dessa classe
    def __new__(cls):
        #Se a instancia nao existir devemos cria-la
        if cls.instancia is None:
            #Crianndo a unica instancia dessa classe
            cls.instancia = super().__new__(cls)
            #Criando dicionarios para guardar os usuarios totais, os integrantes e os gerentes
            cls.instancia.usuarios = {}
            cls.instancia.integrantes = {}
            cls.instancia.gerentes = {}
        return cls.instancia

    #Metodo para cadastrar usuarios
    def registrarUsuario(self, nome, senha, email):
        self.usuarios[email] = {"nome": nome, "senha": senha}
        return

    #Metodo para cadastrar gerentes
    def registrarGerente(self, nome, senha, email):
        self.gerente[email] = {"nome": nome, "senha": senha}
        return

    #Metodo para cadastrar integrantes
    def registrarIntegrante(self, nome, senha, email, pontos_de_esforco):
        self.integrante[email] = {"nome": nome, "senha": senha, "pontos de esforço" : pontos_de_esforco}
        return