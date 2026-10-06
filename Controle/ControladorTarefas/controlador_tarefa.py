class ControladorTarefa:
    """Controlador responsavel por gerenciar operacoes relacionadas a tarefas."""

    def __init__(self, banco, grafo):
        self.banco = banco
        self.grafo = grafo

    def listar_tarefas(self):
        """Retorna uma lista com todas as tarefas cadastradas no sistema, lidando dinamicamente com getters ou atributos."""
        lista_tarefas = []
        for id_tar, t in self.banco.tarefas.items():
            # Funcao utilitaria para capturar dados via Getter ou Atributo
            def extrair_valor(obj, nome_atributo):
                nome_getter = f"get_{nome_atributo}"
                if hasattr(obj, nome_getter) and callable(getattr(obj, nome_getter)):
                    return getattr(obj, nome_getter)()
                return getattr(obj, nome_atributo, getattr(obj, f"_{nome_atributo}", 'N/A'))

            lista_tarefas.append({
                "id": id_tar,
                "titulo": extrair_valor(t, "titulo"),
                "carga": extrair_valor(t, "carga"),
                "estimativa": extrair_valor(t, "estimativa"),
                "status": extrair_valor(t, "status"),
                "pre_requisitos": extrair_valor(t, "pre_requisitos")
            })
        return lista_tarefas, 200

    def criar_tarefa(self, email_solicitante, titulo, carga, estimativa, status, pre_requisitos):
        """Cria e registra uma nova tarefa. Acesso restrito a usuarios com o papel 'Gerente'."""
        from tarefa import Tarefa

        usuario_gerente = self.banco.buscar_usuario(email_solicitante)

        if not usuario_gerente or usuario_gerente.get_papel() != "Gerente":
            return {"erro": "Apenas gerentes podem criar tarefas."}, 403

        if not titulo:
            return {"erro": "O título da tarefa é obrigatório."}, 400

        nova_tarefa = Tarefa(
            titulo=titulo,
            carga=carga,
            estimativa=estimativa
        )
        
        # Aplica setters caso existam na classe
        if hasattr(nova_tarefa, 'set_status') and callable(getattr(nova_tarefa, 'set_status')):
            nova_tarefa.set_status(status)
        else:
            setattr(nova_tarefa, 'status', status)

        if hasattr(nova_tarefa, 'set_pre_requisitos') and callable(getattr(nova_tarefa, 'set_pre_requisitos')):
            nova_tarefa.set_pre_requisitos(pre_requisitos)
        else:
            setattr(nova_tarefa, 'pre_requisitos', pre_requisitos)

        id_tarefa = len(self.banco.tarefas) + 1
        self.banco.tarefas[id_tarefa] = nova_tarefa

        return {"sucesso": True, "mensagem": "Tarefa criada com sucesso!"}, 201

    def vincular_dependencias(self, tarefa_destino, novas_dependencias):
        """
        Vincula uma lista de pré-requisitos (Objetos Tarefa) a uma tarefa de destino (Objeto Tarefa).
        """
        if not tarefa_destino:
            return {"sucesso": False, "mensagem": "A tarefa de destino não pode ser nula."}, 400
            
        if not novas_dependencias:
            return {"sucesso": False, "mensagem": "A lista de dependências está vazia."}, 400

        # 1. Validação de ciclos ANTES de salvar qualquer coisa
        for dep in novas_dependencias:
            if self.grafo.possui_ciclo(tarefa_destino, dep):
                return {
                    "sucesso": False, 
                    "mensagem": f"A inclusão de '{dep.get_titulo()}' cria um ciclo. Operação abortada."
                }, 400

        # 2. Se passou no teste do grafo, vincula as dependências
        ha_dependencia_pendente = False
        for dep in novas_dependencias:
            
            # CORREÇÃO: Só adiciona se já não estiver na lista!
            if dep not in tarefa_destino.get_pre_requisitos():
                tarefa_destino.adicionar_pre_requisitos(dep)
            
            if dep.get_status() != "Concluída":
                ha_dependencia_pendente = True

        # 3. Atualização do status com base nas dependências
        if ha_dependencia_pendente:
            tarefa_destino.atualizar_status("Bloqueada")
        else:
            tarefa_destino.atualizar_status("Pendente")

        return {"sucesso": True, "mensagem": "Dependências vinculadas com sucesso."}, 200

    def atribuir_tarefa(self, projeto, tarefa, email_gerente, email_integrante=None):
        if projeto.get_gerente().get_email() != email_gerente:
            return {"erro": "Acesso negado."}, 403

        if tarefa.get_status() != "Pendente":
            return {"erro": "A tarefa não está pendente."}, 400

        # Verifica pré-requisitos usando os objetos
        for pre_req in tarefa.get_pre_requisitos():
            if pre_req.get_status() != "Concluída":
                return {"erro": "Pré-requisitos não concluídos."}, 400

        integrantes_projeto = []
        for email in projeto.get_integrantes():
            integrantes_projeto.append(self.banco.buscar_usuario(email))

        if email_integrante:
            integrante_selecionado = self.banco.buscar_usuario(email_integrante)
            if not integrante_selecionado or integrante_selecionado not in integrantes_projeto:
                return {"erro": "Integrante não encontrado no projeto."}, 404

            carga_disponivel = integrante_selecionado.get_pontos_de_esforco()
            carga_tarefa = tarefa.get_carga()

            if carga_disponivel >= carga_tarefa:
                integrante_selecionado.set_pontos_de_esforco(carga_disponivel-carga_tarefa)
                tarefa.set_realizador(integrante_selecionado.get_email())
                tarefa.atualizar_status("Em Andamento")

                return {"sucesso": True, "mensagem": f"Tarefa atribuída manualmente a {integrante_selecionado.get_nome()}."}, 200
            else:
                return {"erro": "O integrante selecionado não possui pontos de esforço suficientes."}, 400
        else:
            from Algoritmos.BalanceadorGrafos.balanceador_carga import BalanceadorCarga

            resultado_atribuicoes, falhas = BalanceadorCarga.executar_autodelegacao([tarefa], integrantes_projeto)

            if resultado_atribuicoes:
                nome = resultado_atribuicoes[0]["integrante_nome"]
                return {"sucesso": True, "mensagem": f"Autodelegação realizada com sucesso. Tarefa atribuída a {nome}."}, 200
            else:
                return {"erro": "Nenhum integrante possui capacidade disponível para assumir a tarefa."}, 400

    def atualizar_status_tarefa(self, tarefa, novo_status, relatorio=None):
        if novo_status == "Concluída":
            if not relatorio:
                return {"erro": "Relatório obrigatório para concluir a tarefa."}, 400

            from Projeto.Relatorio.relatorio import Relatorio

            tarefa.adicionar_relatorio(relatorio)
            tarefa.atualizar_status("Concluída")

            for t in self.banco.tarefas.values():
                if tarefa in t.get_pre_requisitos():
                    # Se todos os pré-requisitos de 't' estiverem concluídos
                    outro_pendente = any(pr.get_status() != "Concluída" for pr in t.get_pre_requisitos())
                    if not outro_pendente:
                        t.atualizar_status("Pendente")

            u = self.banco.buscar_usuario(tarefa.get_realizador())
            u.set_pontos_de_esforco(u.get_pontos_de_esforco()+tarefa.get_carga())
            return {"sucesso": True, "mensagem": "Relatório salvo, tarefa concluída e dependências liberadas."}, 200
        
        tarefa.atualizar_status(novo_status)
        return {"sucesso": True, "mensagem": "Status atualizado com sucesso."}, 200