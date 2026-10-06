class Tarefa:
    def __init__(self, titulo, carga, estimativa, pre_requisitos=None, realizador=None):
        self.__titulo = titulo
        self.__carga = carga
        self.__estimativa = estimativa
        self.__status = "Pendente"
        # Agora guarda os OBJETOS das tarefas que são pré-requisitos
        self.__pre_requisitos = pre_requisitos if pre_requisitos is not None else []
        self.__realizador = realizador # String (e-mail)
        self.__relatorios = []

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
        status_validos = ["Pendente", "Em Andamento", "Concluída", "Bloqueada"]
        if novo_status in status_validos:
            self.__status = novo_status
        else:
            raise ValueError("Status Invalido")

    def adicionar_pre_requisitos(self, tarefa_dependencia_obj):
        if tarefa_dependencia_obj not in self.__pre_requisitos:
            self.__pre_requisitos.append(tarefa_dependencia_obj)
        else:
            raise ValueError("Dependência já cadastrada")

    def adicionar_relatorio(self, relatorio_obj):
        if relatorio_obj not in self.__relatorios:
            self.__relatorios.append(relatorio_obj)