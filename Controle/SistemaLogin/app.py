import os
import sys
from flask import Flask, request, jsonify, send_from_directory

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.path.append(os.path.join(BASE_DIR, 'Dominio', 'Equipe'))
sys.path.append(os.path.join(BASE_DIR, 'Dominio', 'Projeto', 'Tarefa'))

from Gerente.gerente import Gerente
from Integrante.integrante import Integrante
from tarefa import Tarefa

app = Flask(__name__)

usuarios = []
tarefas = []

admin = Gerente(nome="Admin", senha="123", email="admin@projeto.com")
usuarios.append(admin)

@app.route('/')
def index():
    caminho_html = os.path.join(BASE_DIR, 'Apresentacao', 'InterfaceGrafica')
    return send_from_directory(caminho_html, 'index.html')

@app.route('/api/login', methods=['POST'])
def login():
    dados = request.json
    email = dados.get('email')
    senha = dados.get('senha')
    
    for u in usuarios:
        if u.get_email() == email and u.validar_senha(senha):
            return jsonify({"sucesso": True, "mensagem": f"Bem-vindo, {u.get_nome()}! (Perfil: {u.get_papel()})"})
    
    return jsonify({"erro": "Email ou senha inválidos."}), 401

@app.route('/api/integrantes', methods=['POST'])
def cadastrar_integrante():
    dados = request.json
    
    for u in usuarios:
        if u.get_email() == dados.get('email'):
            return jsonify({"erro": "Este email já está cadastrado."}), 400
            
    try:
        novo_integrante = Integrante(
            nome=dados.get('nome'),
            senha=dados.get('senha'),
            email=dados.get('email'),
            pontos_de_esforco=dados.get('pontos_de_esforco')
        )
        usuarios.append(novo_integrante)
        return jsonify({"sucesso": True, "mensagem": f"Integrante {novo_integrante.get_nome()} cadastrado com sucesso!"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

@app.route('/api/tarefas', methods=['POST'])
def criar_tarefa():
    dados = request.json
    
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
            
        tarefas.append(nova_tarefa)
        return jsonify({"sucesso": True, "mensagem": f"Tarefa '{nova_tarefa.get_titulo()}' criada com sucesso!"})
        
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


if __name__ == '__main__':
    print("Servidor rodando! Acesse http://127.0.0.1:5000 no seu navegador.")
    app.run(debug=True, port=5000)