class ControladorTarefa:
    """Controlador responsavel por gerenciar operacoes relacionadas a tarefas."""

    def __init__(self, banco):
        self.banco = banco

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

    def atribuir_tarefa(self, id_projeto, id_tarefa, email_integrante=None):
        projeto = self.banco.buscar_projeto(id_projeto)
        tarefa = self.banco.tarefas.get(id_tarefa)

        if not projeto or not tarefa:
            return {"erro": "Projeto ou tarefa não encontrados."}, 404

        if tarefa.get_status() != "Pendente":
            return {"erro": "A tarefa selecionada não está pendente."}, 400

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

    def atualizar_status_tarefa(self, id_tarefa, novo_status, texto_relatorio=None):
        tarefa = self.banco.tarefas.get(id_tarefa)
        if not tarefa:
            return {"erro": "Tarefa não encontrada."}, 404

        if novo_status == "Concluída":
            if not texto_relatorio or len(texto_relatorio.strip()) == 0:
                return {"erro": "Relatório obrigatório. A tarefa não pode ser concluída sem preenchê-lo."}, 400

            from Projeto.Relatorio.relatorio import Relatorio

            novo_relatorio = Relatorio(texto_relatorio)
            tarefa.adicionar_relatorio(novo_relatorio)

            tarefa.atualizar_status("Concluída")

            for t in self.banco.tarefas.values():
                pre_requisitos = t.get_pre_requisitos()
                if id_tarefa in pre_requisitos:
                    # verifica se ainda possui outro pre-requisito pendente
                    outro_pendente = any(
                        self.banco.tarefas.get(pr_id).get_status() != "Concluída"
                        for pr_id in pre_requisitos if self.banco.tarefas.get(pr_id)
                    )

                    if not outro_pendente:
                        t.atualizar_status("Pendente")

            return {"sucesso": True, "mensagem": "Relatório salvo, tarefa concluída e dependências liberadas."}, 200
        else:
            tarefa.atualizar_status(novo_status)
            return {"sucesso": True, "mensagem": "Status atualizado com sucesso."}, 200

    def vincular_dependencias(self, id_tarefa, dependencias_ids):
        tarefa = self.banco.tarefas.get(id_tarefa)
        if not tarefa:
            return {"erro": "Tarefa principal não encontrada."}, 404

        from Algoritmos.GrafoDependencia.verificador_ciclos import VerificadorCiclo

        verificador_ciclos = VerificadorCiclo(self.banco.tarefas)

        for dep_id in dependencias_ids:
            if not self.banco.tarefas.get(dep_id):
                return {"erro": f"A tarefa {dep_id} informada como dependência não existe."}, 404

            if verificador_ciclos.insercao_cria_ciclo(id_tarefa, dep_id):
                return {"erro": f"Ciclo detectado ao tentar vincular a dependência {dep_id}."}

            tarefa.adicionar_pre_requisitos(dep_id)

        return {"sucesso": True, "mensagem": "Dependências vinculadas com sucesso."}, 200
