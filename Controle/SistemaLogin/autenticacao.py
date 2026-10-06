#Classe responsável por testar se o login é válido
class ServicoAutenticacao:
    def __init__(self, banco):
        self.banco = banco

    def realizar_login(self, email, senha, papel_selecionado=None):
        if not email or not senha:
            return {"erro": "E-mail e senha são obrigatórios."}, 400

        usuario = self.banco.buscar_usuario(email)

        if not usuario or not usuario.validar_senha(senha):
            return {"erro": "E-mail ou senha inválidos."}, 401

        if papel_selecionado and usuario.get_papel() != papel_selecionado:
            return {"erro": f"Este usuário não é um {papel_selecionado}."}, 403

        return {
            "sucesso": True,
            "papel": usuario.get_papel(),
            "nome": usuario.get_nome(),
            "email": usuario.get_email(),
            "mensagem": f"Bem-vindo(a), {usuario.get_nome()}!"
        }, 200