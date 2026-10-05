class BalanceadorCarga:
    @staticmethod
    def executar_autodelegacao(tarefas_pendentes, integrantes):
        resultado_atribuicoes = []
        tarefas_nao_atribuidas = []

        # ordena da maior carga para a menor
        tarefas_ordenadas = sorted(tarefas_pendentes, key=lambda t: t.get_carga(), reverse=True)

        for tarefa in tarefas_ordenadas:
            carga_necessaria = tarefa.get_carga()

            integrante_escolhido = None
            maior_capacidade = -1

            for integrante in integrantes:
                capacidade_atual = integrante.get_pontos_de_esforco()
                if capacidade_atual >= carga_necessaria and capacidade_atual > maior_capacidade:
                    maior_capacidade = capacidade_atual
                    integrante_escolhido = integrante

            if integrante_escolhido:
                novo_limite = integrante_escolhido.get_pontos_de_esforco() - carga_necessaria
                integrante_escolhido.set_pontos_de_esforco(novo_limite)

                tarefa.set_realizador(integrante_escolhido.get_email())
                tarefa.atualizar_status("Em Andamento")

                resultado_atribuicoes.append({"tarefa_titulo": tarefa.get_titulo(),"integrante_nome": integrante_escolhido.get_nome()})
            else:
                tarefas_nao_atribuidas.append(tarefa.get_titulo())

        return resultado_atribuicoes, tarefas_nao_atribuidas