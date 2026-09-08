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

            # Dicionario para salvar as tarefas
            cls.instancia.tarefas = {}
            # ID de cada tarefa
            cls.instancia.id_tarefa_seq = 1

        return cls.instancia

    #Metodo para cadastrar usuarios
    def registrarUsuario(self, usuario_objeto):
        email = usuario_objeto.get_email()
        self.usuarios[email] = usuario_objeto
        return

    # Retorna o objeto instanciado com todos os metodos dele
    def buscar_usuario(self, email):
        return self.usuarios.get(email)

    # Registra nova tarefa e retorna seu ID
    def registrar_tarefa(self, tarefa_objeto):
        id_atual = self.id_tarefa_seq
        self.tarefas[id_atual] = tarefa_objeto
        self.id_tarefa_seq += 1
        return id_atual