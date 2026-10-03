class Projeto:

    def __init__(self, nome, gerente):
        self.__nome = nome
        self.__gerente = gerente
        self.__integrantes = []
        self.__tarefas = []

    def get_nome(self):
        return self.__nome

    def get_gerente(self):
        return self.__gerente

    def get_integrantes(self):
        return self.__integrantes

    def get_tarefas(self):
        return self.__tarefas

    def adicionar_integrante(self, email):
        if email not in self.__integrantes:
            self.__integrantes.append(email)

    def adicionar_tarefa(self, id_tarefa):
        if id_tarefa not in self.__tarefas:
            self.__tarefas.append(id_tarefa)