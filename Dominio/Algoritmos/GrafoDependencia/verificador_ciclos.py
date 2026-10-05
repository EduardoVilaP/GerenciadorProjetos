class VerificadorCiclo:
    def __init__(self, dicionario_tarefas):
        self.tarefas = dicionario_tarefas

    # se ao adicionar id_nova_dependencia como pre-requisito de id_tarefa_alvo gerar um ciclo, retorna true
    def insercao_cria_ciclo(self, id_tarefa_alvo, id_nova_dependencia):
        if id_tarefa_alvo == id_nova_dependencia:
            return True

        visitados = set()
        pilha_recursao = set()

        def dfs(id_atual):
            visitados.add(id_atual)
            pilha_recursao.add(id_atual)

            tarefa_atual = self.tarefas.get(id_atual)
            if tarefa_atual:
                vizinhos = list(tarefa_atual.get_pre_requisitos())

                if id_atual == id_tarefa_alvo:
                    vizinhos.append(id_nova_dependencia)

                for pre_req in vizinhos:
                    if pre_req not in visitados:
                        if dfs(pre_req):
                            return True
                    elif pre_req in pilha_recursao:
                        return True

            pilha_recursao.remove(id_atual)
            return False

        return dfs(id_tarefa_alvo)