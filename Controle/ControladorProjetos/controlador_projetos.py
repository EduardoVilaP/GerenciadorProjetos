class ControladorProjeto:
    """Controlador responsavel por gerenciar operacoes sobre projetos."""

    def __init__(self, banco):
        self.banco = banco

    def visualizarProjeto(self, gerente):

        v = self.retornarProjetos(gerente)

        return v

    def retornarProjetos(self, gerente):

        projetosGerente = []

        for projeto in self.banco.projetos.values():

            if projeto.get_gerente() == gerente:
                projetosGerente.append(projeto)

        return projetosGerente

    def criarProjeto(self, nomeProjeto, gerente):
        """Cria e registra um novo projeto. Acesso restrito ao cargo de Gerente"""
        from Projeto.projeto import Projeto

        v = self.retornarProjetos(gerente)

        for p in v:

            n = p.get_nome()

            if nomeProjeto == n:
                return False

        project = Projeto(nomeProjeto, gerente)

        self.banco.registrar_projeto(project)

        return True

    def adicionarIntegrante(self, id_projeto, email_integrante, gerente):
        """Associa um integrante ja cadastrado no sistema a um projeto especifico."""
        projeto = self.banco.buscar_projeto(id_projeto)
        if not projeto:
            return False, "Projeto não encontrado."

        # Valida se quem esta tentando adicionar e o gerente dono do projeto
        if projeto.get_gerente().get_email() != gerente.get_email():
            return False, "Apenas o gerente responsável pelo projeto pode adicionar integrantes."

        # Verifica se o integrante existe no banco
        integrante = self.banco.buscar_usuario(email_integrante)
        if not integrante or integrante.get_papel() != "Integrante":
            return False, "Integrante não encontrado no sistema."

        # Verifica se o e-mail ja esta cadastrado no projeto
        if email_integrante in projeto.get_integrantes():
            return False, "Integrante já está associado a este projeto."

        # Adiciona o e-mail do integrante na lista de integrantes do projeto
        projeto.get_integrantes().append(email_integrante)
        return True, "Integrante vinculado ao projeto com sucesso!"

    def retornarProjetosIntegrante(self, integrante):
        """Retorna os projetos em que o integrante esta cadastrado."""
        projetosIntegrante = []
        email = integrante.get_email()

        for projeto in self.banco.projetos.values():
            if email in projeto.get_integrantes():
                projetosIntegrante.append(projeto)

        return projetosIntegrante

    def obterDetalhesProjeto(self, id_projeto, usuario):
        """
        Carrega os dados de um projeto específico dependendo do perfil do usuário:
        - Gerente: visualiza todas as tarefas e integrantes do projeto.
        - Integrante: visualiza apenas as tarefas que foram atribuídas a ele.
        """
        projeto = self.banco.buscar_projeto(id_projeto)
        if not projeto:
            return None

        papel = usuario.get_papel()
        email_usuario = usuario.get_email()

        # Resgata todas as tarefas associadas ao projeto
        ids_tarefas_proj = projeto.get_tarefas()

        tarefas_filtradas = []
        for id_t in ids_tarefas_proj:
            t = self.banco.tarefas.get(id_t)
            if not t:
                continue

            # Se for Integrante, exibe apenas tarefas cujo realizador seja ele
            realizador = t.get_realizador()
            if papel == "Integrante":
                if realizador != email_usuario:
                    continue

            tarefas_filtradas.append({
                "id": id_t,
                "titulo": t.get_titulo(),
                "carga": t.get_carga(),
                "estimativa": t.get_estimativa(),
                "status": t.get_status(),
                "realizador": realizador
            })

        # Mapeia os integrantes caso o usuário logado seja o Gerente
        integrantes_detalhados = []
        if papel == "Gerente":
            for email_int in projeto.get_integrantes():
                u_int = self.banco.buscar_usuario(email_int)
                if u_int:

                    tarefas_do_integrante = [tar["titulo"] for tar in tarefas_filtradas if tar.get("realizador") == email_int]

                    integrantes_detalhados.append({
                        "nome": u_int.get_nome(),
                        "email": u_int.get_email(),
                        "pontos_de_esforco": u_int.get_pontos_de_esforco() if hasattr(u_int, 'get_pontos_de_esforco') else 0,
                        "tarefas_atribuidas": tarefas_do_integrante
                    })
        
        carga_disponivel = None
        if papel == "Integrante" and hasattr(usuario, 'get_pontos_de_esforco'):
            carga_disponivel = usuario.get_pontos_de_esforco()

        return {
            "id": id_projeto,
            "nome": projeto.get_nome(),
            "papel_usuario": papel,
            "carga_disponivel": carga_disponivel,
            "tarefas": tarefas_filtradas,
            "integrantes": integrantes_detalhados
        }