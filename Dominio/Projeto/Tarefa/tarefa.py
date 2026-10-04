class Tarefa:

    def __init__(self, titulo, carga, estimativa, pre_requisitos = None, realizador = None):
        self.__titulo = titulo
        self.__carga = carga
        self.__estimativa = estimativa

        # Toda tarefa nasce "Pendente"
        self.__status = "Pendente"

        # Se nao tiver pre-requisitos, comeca com uma lista vazia
        self.__pre_requisitos = pre_requisitos if pre_requisitos is not None else []

        self.__realizador = realizador;

    def get_titulo(self):
        return self.__titulo

    def get_carga(self):
        return self.__carga

    def get_estimativa(self):
        return self.__estimativa

    def get_status(self):
        return self.__status
        
    def get_pre_requisitos(self):
        return self.__pre_requisitos

    def get_realizador(self):
        return self.__realizador

    def set_realizador(self, e_mail_integrante):
        self.__realizador = e_mail_integrante

    def atualizar_status(self, novo_status):
        status_validos = ["Pendente", "Em Andamento", "Concluída"]
        if novo_status in status_validos:
            self.__status = novo_status
        else:
            raise ValueError("Status Invalido")

    def adicionar_pre_requisitos(self, tarefa_dependencia):
        if tarefa_dependencia not in self.__pre_requisitos:
            self.__pre_requisitos.append(tarefa_dependencia)
        else:
            raise ValueError("Dependencia ja cadastrada")