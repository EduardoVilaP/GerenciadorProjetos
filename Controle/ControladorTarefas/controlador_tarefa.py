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