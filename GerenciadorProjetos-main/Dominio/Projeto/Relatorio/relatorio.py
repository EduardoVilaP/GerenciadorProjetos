from datetime import datetime

class Relatorio:
    def __init__(self, texto):
        self.__texto = texto
        self.__data_envio = datetime.now()

    def get_texto(self):
        return self.__texto