"""
Modulo que define a classe BancoDados utilizando o padrao Singleton
para gerenciar o armazenamento em memoria de usuarios e tarefas durante a execucao.
"""

class BancoDados:
    """Implementa um repositorio centralizado em memoria utilizando o padrao Singleton."""

    instancia = None

    def __new__(cls):
        """Controla a criacao da instancia unica da classe e inicializa as estruturas de dados."""
        if cls.instancia is None:
            cls.instancia = super().__new__(cls)

            #Criando dicionarios para guardar os usuarios totais, os integrantes e os gerentes
            cls.instancia.usuarios = {}

            # Dicionario para salvar as tarefas
            cls.instancia.tarefas = {}

            # Dicionário para salvar os projetos
            cls.instancia.projetos = {}

            # ID de cada tarefa
            cls.instancia.id_tarefa_seq = 1

            # ID de cada projeto
            cls.instancia.id_projeto_seq = 1

        return cls.instancia

    def registrarUsuario(self, usuario_objeto):
        """Armazena um objeto de usuario no dicionario interno utilizando o email como chave."""
        email = usuario_objeto.get_email()
        self.usuarios[email] = usuario_objeto
        return

    def buscar_usuario(self, email):
        """Busca e retorna o objeto de usuario correspondente ao email fornecido, ou None se nao existir."""
        return self.usuarios.get(email)

    def registrar_tarefa(self, tarefa_objeto):
        """Registra uma nova tarefa no dicionario utilizando um ID sequencial e incrementa o contador."""
        id_atual = self.id_tarefa_seq
        self.tarefas[id_atual] = tarefa_objeto
        self.id_tarefa_seq += 1
        return id_atual

    def registrar_projeto(self, projeto):
        id_projeto = self.id_projeto_seq
        self.projetos[id_projeto] = projeto
        self.id_projeto_seq +=1
        return id_projeto

    def buscar_projeto(self, id_projeto):
        return self.projetos.get(id_projeto)

    def buscar_projetos_por_usuario(self, usuario):
        """Retorna todos os projetos onde o usuário é Gerente ou Integrante."""
        projetos_usuario = []
        email = usuario.get_email()
        papel = usuario.get_papel()

        for id_proj, projeto in self.projetos.items():
            if papel == "Gerente" and projeto.get_gerente().get_email() == email:
                projetos_usuario.append({"id": id_proj, "objeto": projeto})
            elif papel == "Integrante" and email in projeto.get_integrantes():
                projetos_usuario.append({"id": id_proj, "objeto": projeto})

        return projetos_usuario