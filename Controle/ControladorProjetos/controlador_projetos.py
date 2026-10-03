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