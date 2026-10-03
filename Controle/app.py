"""
Modulo principal da aplicacao Flask.
Responsavel por configurar o servidor, gerenciar o mapeamento de diretorios do projeto,
inicializar instancias globais (banco e controladores) e expor as rotas da API REST.
"""

import os
import sys
from flask import Flask, request, jsonify, send_from_directory

# Localiza a raiz do repositorio procurando a pasta 'Dominio'
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = DIRETORIO_ATUAL

while BASE_DIR and not os.path.exists(os.path.join(BASE_DIR, 'Dominio')):
    PAI = os.path.dirname(BASE_DIR)
    if PAI == BASE_DIR:
        break
    BASE_DIR = PAI

# Adiciona diretorios ao sys.path
sys.path.append(os.path.join(BASE_DIR, 'Dominio', 'Equipe'))
sys.path.append(os.path.join(BASE_DIR, 'Dominio'))
sys.path.append(os.path.join(BASE_DIR, 'Dominio', 'Projeto', 'Tarefa'))
sys.path.append(os.path.join(BASE_DIR, 'Persistencia', 'FachadaBD'))
sys.path.append(os.path.join(BASE_DIR, 'Controle'))
sys.path.append(os.path.join(BASE_DIR, 'SistemaLogin'))

# Importacoes das Entidades, Servicos e Controladores
from Gerente.gerente import Gerente
from bancoDeDados import BancoDados
from SistemaLogin.autenticacao import ServicoAutenticacao
from ControladorEquipe.controlador_equipe import ControladorEquipe
from ControladorTarefas.controlador_tarefa import ControladorTarefa
from ControladorProjetos.controlador_projetos import ControladorProjeto

app = Flask(__name__)

# Instancia unica da Persistencia, Autenticacao e Controladores
banco = BancoDados()
servico_autenticacao = ServicoAutenticacao(banco)
controle_equipe = ControladorEquipe(banco)
controle_tarefa = ControladorTarefa(banco)
controle_projeto = ControladorProjeto(banco)

# Configura e registra o Usuario Admin Padrao no sistema
admin = Gerente(nome="Admin", senha="123", email="admin@projeto.com")
banco.registrarUsuario(admin)

@app.route('/')
def index():
    """Serve a pagina inicial (Interface Grafica) da aplicacao."""
    caminho_html = os.path.join(BASE_DIR, 'Apresentacao', 'InterfaceGrafica')
    return send_from_directory(caminho_html, 'index.html')


# ==========================================
# ROTA DE AUTENTICACAO
# ==========================================

@app.route('/api/login', methods=['POST'])
def login():
    """Endpoint POST para autenticar usuarios e validar papeis de acesso."""
    dados = request.json or {}
    resposta, status_code = servico_autenticacao.realizar_login(
        email=dados.get('email'),
        senha=dados.get('senha'),
        papel_selecionado=dados.get('papel')
    )
    return jsonify(resposta), status_code


# ==========================================
# ROTAS DE EQUIPE / USUARIOS
# ==========================================

@app.route('/api/integrantes', methods=['GET'])
def listar_integrantes():
    """Endpoint GET para listar todos os integrantes (Acesso restrito a gerentes)."""
    email_solicitante = request.args.get('usuario_logado')
    resposta, status_code = controle_equipe.listar_integrantes(email_solicitante)
    return jsonify(resposta), status_code


@app.route('/api/integrantes', methods=['POST'])
def cadastrar_integrante():
    """Endpoint POST para cadastrar um novo integrante no sistema."""
    dados = request.json or {}
    resposta, status_code = controle_equipe.cadastrar_integrante(
        email_solicitante=dados.get('usuario_logado'),
        nome=dados.get('nome'),
        email=dados.get('email'),
        senha=dados.get('senha'),
        esforco=dados.get('pontos_de_esforco', 0)
    )
    return jsonify(resposta), status_code


# ==========================================
# ROTAS DE TAREFAS
# ==========================================

@app.route('/api/tarefas', methods=['GET'])
def listar_tarefas():
    """Endpoint GET para listar todas as tarefas cadastradas."""
    resposta, status_code = controle_tarefa.listar_tarefas()
    return jsonify(resposta), status_code


@app.route('/api/tarefas', methods=['POST'])
def criar_tarefa():
    """Endpoint POST para criar uma nova tarefa (Acesso restrito a gerentes)."""
    dados = request.json or {}
    resposta, status_code = controle_tarefa.criar_tarefa(
        email_solicitante=dados.get('usuario_logado'),
        titulo=dados.get('titulo'),
        carga=dados.get('carga', 0),
        estimativa=dados.get('estimativa', ''),
        status=dados.get('status', 'Pendente'),
        pre_requisitos=dados.get('pre_requisitos', [])
    )
    return jsonify(resposta), status_code

# ==========================================
# ROTAS DE PROJETOS
# ==========================================

@app.route('/api/projetos', methods=['GET'])
def listar_projetos():
    """Endpoint GET para listar os projetos do gerente logado."""

    email_gerente = request.args.get('usuario_logado')

    gerente = banco.buscar_usuario(email_gerente)

    if gerente is None:
        return jsonify({"erro": "Gerente não encontrado"}), 404

    projetos = controle_projeto.visualizarProjeto(gerente)

    resposta = []

    for projeto in projetos:
        resposta.append({
            "nome": projeto.get_nome()
        })

    return jsonify(resposta), 200


@app.route('/api/projetos', methods=['POST'])
def criar_projeto():
    """Endpoint POST para criar um novo projeto."""

    dados = request.json or {}

    email_gerente = dados.get('usuario_logado')
    nome_projeto = dados.get('nome')

    gerente = banco.buscar_usuario(email_gerente)

    if gerente is None:
        return jsonify({"erro": "Gerente não encontrado"}), 404

    resultado = controle_projeto.criarProjeto(
        nomeProjeto=nome_projeto,
        gerente=gerente
    )

    if resultado:
        return jsonify({
            "mensagem": "Projeto criado com sucesso"
        }), 201

    return jsonify({
        "erro": "Já existe um projeto com esse nome"
    }), 400

if __name__ == '__main__':
    print("Servidor rodando! Acesse http://127.0.0.1:5000 no seu navegador.")
    app.run(debug=True, port=5000)