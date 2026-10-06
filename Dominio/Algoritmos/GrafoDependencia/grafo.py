class GrafoDependencias:
    def __init__(self):
        """
        Classe responsável por operações de validação no grafo de dependências das tarefas.
        """
        pass

    def possui_ciclo(self, tarefa_destino, nova_dependencia) -> bool:
        """
        Verifica se adicionar 'nova_dependencia' como pré-requisito de 'tarefa_destino' cria um ciclo.
        """
        if tarefa_destino == nova_dependencia:
            return True

        visitados = []

        def dfs(tarefa_atual):
            if tarefa_atual == tarefa_destino:
                return True
            
            visitados.append(tarefa_atual)

            for pre_req in tarefa_atual.get_pre_requisitos():
                if pre_req not in visitados:
                    if dfs(pre_req):
                        return True
                        
            return False

        return dfs(nova_dependencia)