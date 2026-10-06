class ControladorEquipe:
    """Controlador responsavel por gerenciar operacoes de equipe, autenticacao e controle de acesso."""

    def __init__(self, banco):
        self.banco = banco

    def realizar_login(self, email, senha, papel_selecionado):
        """Realiza a autenticacao do usuario validando credenciais e o papel selecionado."""
        usuario = self.banco.buscar_usuario(email)
        
        if not usuario or not usuario.validar_senha(senha):
            return {"erro": "Email ou senha inválidos."}, 401
            
        if papel_selecionado and usuario.get_papel() != papel_selecionado:
            return {"erro": f"Este usuário não é um {papel_selecionado}."}, 403
            
        return {
            "sucesso": True, 
            "papel": usuario.get_papel(),
            "mensagem": f"Bem-vindo, {usuario.get_nome()}!"
        }, 200

    def listar_integrantes(self, email_solicitante):
        """Lista todos os integrantes cadastrados. Acesso restrito a usuarios com o papel 'Gerente'."""
        usuario = self.banco.buscar_usuario(email_solicitante)
        
        if not usuario or usuario.get_papel() != "Gerente":
            return {"erro": "Acesso negado."}, 403
            
        lista_integrantes = []
        for u in self.banco.usuarios.values():
            if u.get_papel() == "Integrante":
                # Suporta o método get_pontos_de_esforco() ou o atributo direto
                esforco = (u.get_pontos_de_esforco() if hasattr(u, 'get_pontos_de_esforco') 
                           else getattr(u, 'pontos_de_esforco', 'N/A'))
                
                lista_integrantes.append({
                    "nome": u.get_nome(),
                    "email": u.get_email(),
                    "pontos_de_esforco": esforco
                })
        return lista_integrantes, 200

    def cadastrar_integrante(self, email_solicitante, nome, email, senha, esforco):
        """Cadastra um novo integrante no sistema. Acesso restrito a gerentes."""
        from Integrante.integrante import Integrante

        usuario_gerente = self.banco.buscar_usuario(email_solicitante)

        if not usuario_gerente or usuario_gerente.get_papel() != "Gerente":
            return {"erro": "Apenas gerentes podem cadastrar novos integrantes."}, 403

        if not nome or not email or not senha:
            return {"erro": "Preencha todos os campos obrigatórios."}, 400

        if self.banco.buscar_usuario(email):
            return {"erro": "Este e-mail já está cadastrado."}, 400

        novo_integrante = Integrante(
            nome=nome, 
            senha=senha, 
            email=email, 
            pontos_de_esforco=esforco
        )
        
        self.banco.registrarUsuario(novo_integrante)
        return {"sucesso": True, "mensagem": f"Integrante {nome} cadastrado com sucesso!"}, 201