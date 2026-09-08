import os
import sys
from flask import Flask, request, jsonify, send_from_directory

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.path.append(os.path.join(BASE_DIR, 'Dominio', 'Equipe'))
sys.path.append(os.path.join(BASE_DIR, 'Dominio', 'Projeto', 'Tarefa'))

sys.path.append(os.path.join(BASE_DIR, 'Persistencia', 'FachadaBD'))

from Gerente.gerente import Gerente
from Integrante.integrante import Integrante
from tarefa import Tarefa
from bancoDeDados import BancoDados

app = Flask(__name__)

banco = BancoDados()

admin = Gerente(nome="Admin", senha="123", email="admin@projeto.com")
banco.registrarUsuario(admin)

@app.route('/')
def index():
    caminho_html = os.path.join(BASE_DIR, 'Apresentacao', 'InterfaceGrafica')
    return send_from_directory(caminho_html, 'index.html')

@app.route('/api/login', methods=['POST'])
def login():
    dados = request.json
    email = dados.get('email')
    senha = dados.get('senha')
    
    usuario = banco.buscar_usuario(email)
    
    if usuario and usuario.validar_senha(senha):
        return jsonify({"sucesso": True, "mensagem": f"Bem-vindo, {usuario.get_nome()}! (Perfil: {usuario.get_papel()})"})
    
    return jsonify({"erro": "Email ou senha inválidos."}), 401

@app.route('/api/integrantes', methods=['POST'])
def cadastrar_integrante():
    dados = request.json

    email_solicitante = dados.get('usuario_logado')
    usuario_requisitante = banco.buscar_usuario(email_solicitante)

    if not usuario_requisitante or usuario_requisitante.get_papel() != "Gerente":
        return jsonify({"erro": "Acesso negado: Apenas gerentes podem cadastrar integrantes."}), 403
    
    if banco.buscar_usuario(dados.get('email')):
        return jsonify({"erro": "Este email já está cadastrado."}), 409

    
    try:
        novo_integrante = Integrante(
            nome=dados.get('nome'),
            senha=dados.get('senha'),
            email=dados.get('email'),
            pontos_de_esforco=dados.get('pontos_de_esforco')
        )
        banco.registrarUsuario(novo_integrante)
        return jsonify({"sucesso": True, "mensagem": f"Integrante {novo_integrante.get_nome()} cadastrado com sucesso!"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

@app.route('/api/tarefas', methods=['POST'])
def criar_tarefa():
    dados = request.json

    email_solicitante = dados.get('usuario_logado')
    usuario_requisitante = banco.buscar_usuario(email_solicitante)

    if not usuario_requisitante or usuario_requisitante.get_papel() != "Gerente":
        return jsonify({"erro": "Apenas gerentes podem criar tarefas."}), 403
    
    try:
        nova_tarefa = Tarefa(
            titulo=dados.get('titulo'),
            carga=dados.get('carga'),
            estimativa=dados.get('estimativa'),
            pre_requisitos=dados.get('pre_requisitos', [])
        )
        
        status_enviado = dados.get('status')
        if status_enviado and status_enviado != "Pendente":
            nova_tarefa.atualizar_status(status_enviado)
            
        id_gerado = banco.registrar_tarefa(nova_tarefa)
        return jsonify({"sucesso": True, "mensagem": f"Tarefa '{nova_tarefa.get_titulo()}' (ID: {id_gerado}) criada com sucesso por {usuario_requisitante.get_nome()}!"})
        
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


if __name__ == '__main__':
    print("Servidor rodando! Acesse http://127.0.0.1:5000 no seu navegador.")
    app.run(debug=True, port=5000)