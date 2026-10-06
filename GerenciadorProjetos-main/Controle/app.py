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
from Integrante.integrante import Integrante
from bancoDeDados import BancoDados
from SistemaLogin.autenticacao import ServicoAutenticacao
from ControladorEquipe.controlador_equipe import ControladorEquipe
from ControladorTarefas.controlador_tarefa import ControladorTarefa
from ControladorProjetos.controlador_projetos import ControladorProjeto
from Algoritmos.GrafoDependencia.grafo import GrafoDependencias
from Projeto.Relatorio.relatorio import Relatorio

app = Flask(__name__)

# Instancia unica da Persistencia, Autenticacao e Controladores
banco = BancoDados()
grafo = GrafoDependencias()
servico_autenticacao = ServicoAutenticacao(banco)
controle_equipe = ControladorEquipe(banco)
controle_tarefa = ControladorTarefa(banco, grafo)
controle_projeto = ControladorProjeto(banco)

# Configura e registra um Gerente Padrao inicial no sistema (Opcional)
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
# ROTAS DE EQUIPE / USUARIOS (AUTOCADASTRO E LISTAGEM)
# ==========================================

@app.route('/api/cadastrar/integrante', methods=['POST'])
def cadastrar_integrante():
    """
    Endpoint POST para autocadastro publico de um novo integrante na plataforma.
    """
    dados = request.json or {}
    email = dados.get('email')
    nome = dados.get('nome')
    senha = dados.get('senha')
    esforco = dados.get('pontos_de_esforco', 0)

    if not email or not nome or not senha:
        return jsonify({"erro": "Todos os campos são obrigatórios."}), 400

    if banco.buscar_usuario(email):
        return jsonify({"erro": "Este e-mail já está cadastrado no sistema."}), 400

    novo_integrante = Integrante(nome=nome, email=email, senha=senha, pontos_de_esforco=int(esforco))
    banco.registrarUsuario(novo_integrante)

    return jsonify({"mensagem": "Integrante cadastrado com sucesso! Faça login para continuar."}), 201


@app.route('/api/cadastrar/gerente', methods=['POST'])
def cadastrar_gerente():
    """
    Endpoint POST para autocadastro publico de um novo gerente na plataforma.
    """
    dados = request.json or {}
    email = dados.get('email')
    nome = dados.get('nome')
    senha = dados.get('senha')

    if not email or not nome or not senha:
        return jsonify({"erro": "Todos os campos são obrigatórios."}), 400

    if banco.buscar_usuario(email):
        return jsonify({"erro": "Este e-mail já está cadastrado no sistema."}), 400

    novo_gerente = Gerente(nome=nome, email=email, senha=senha)
    banco.registrarUsuario(novo_gerente)

    return jsonify({"mensagem": "Gerente cadastrado com sucesso! Faça login para continuar."}), 201


@app.route('/api/integrantes/disponiveis', methods=['GET'])
def listar_integrantes_disponiveis():
    """
    Endpoint GET para retornar todos os integrantes cadastrados na plataforma.
    Usado pelos Gerentes para popular a lista de inclusao em um projeto.
    """
    integrantes = []
    # Itera sobre os usuarios cadastrados no banco
    for usuario in banco.usuarios.values():
        if usuario.get_papel() == "Integrante":
            integrantes.append({
                "nome": usuario.get_nome(),
                "email": usuario.get_email()
            })
    return jsonify(integrantes), 200


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
    """Endpoint POST para criar uma nova tarefa e vinculá-la ao projeto."""
    dados = request.json or {}
    email_solicitante = dados.get('usuario_logado')
    id_projeto = dados.get('id_projeto')

    # Cria a tarefa via ControladorTarefa
    resposta, status_code = controle_tarefa.criar_tarefa(
        email_solicitante=email_solicitante,
        titulo=dados.get('titulo'),
        carga=dados.get('carga', 0),
        estimativa=dados.get('estimativa', ''),
        status=dados.get('status', 'Pendente'),
        pre_requisitos=dados.get('pre_requisitos', [])
    )

    # Se a tarefa foi criada com sucesso, vincula a chave dela ao projeto
    if status_code in (200, 201) and id_projeto is not None:
        projeto = banco.buscar_projeto(int(id_projeto))
        if projeto:
            # Recupera a chave da tarefa criada
            id_tarefa = resposta.get('id') if isinstance(resposta, dict) else None
            if id_tarefa is None and banco.tarefas:
                # Pega a chave da última tarefa inserida no dicionário do banco
                id_tarefa = list(banco.tarefas.keys())[-1]

            if id_tarefa is not None and id_tarefa not in projeto.get_tarefas():
                projeto.get_tarefas().append(id_tarefa)

        return jsonify({"mensagem": "Tarefa criada e vinculada ao projeto com sucesso!"}), 201

    return jsonify(resposta), status_code


@app.route('/api/tarefas/<int:id_tarefa>/dependencias', methods=['POST'])
def vincular_dependencias_tarefa(id_tarefa):
    """
    Endpoint POST para vincular novas dependências/pré-requisitos a uma tarefa existente.
    """
    dados = request.json or {}
    email_solicitante = dados.get('usuario_logado')

    # Validação do usuário solicitante
    if not email_solicitante or not banco.buscar_usuario(email_solicitante):
        return jsonify({"erro": "Usuário não encontrado ou não autenticado."}), 401

    # Busca a tarefa de destino no banco de dados
    tarefa_destino = banco.tarefas.get(id_tarefa)
    if not tarefa_destino:
        return jsonify({"erro": "Tarefa de destino não encontrada."}), 404

    # Recupera a lista de IDs de pré-requisitos enviada pela interface
    ids_dependencias = dados.get('dependencias_ids', [])
    if not ids_dependencias:
        return jsonify({"erro": "A lista de dependências está vazia."}), 400

    # Mapeia os IDs recebidos para os objetos Tarefa correspondentes cadastrados no banco
    novas_dependencias = []
    for dep_id in ids_dependencias:
        tarefa_dep = banco.tarefas.get(int(dep_id))
        if tarefa_dep:
            novas_dependencias.append(tarefa_dep)
        else:
            return jsonify({"erro": f"Dependência com ID {dep_id} não foi encontrada."}), 404

    # Invoca o método no ControladorTarefa repassando os objetos Tarefa
    resultado, status_code = controle_tarefa.vincular_dependencias(tarefa_destino, novas_dependencias)

    if resultado.get("sucesso"):
        return jsonify({"mensagem": resultado.get("mensagem")}), status_code
        
    # Se falhou, retorna o erro
    return jsonify({"erro": resultado.get("erro") or resultado.get("mensagem")}), status_code


# ==========================================
# ROTAS DE PROJETOS
# ==========================================

@app.route('/api/projetos', methods=['GET'])
def listar_projetos():
    """Endpoint GET para listar os projetos associados ao usuario logado (Gerente ou Integrante)."""
    email_usuario = request.args.get('usuario_logado')

    usuario = banco.buscar_usuario(email_usuario)

    if usuario is None:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    resposta = []

    if usuario.get_papel() == "Gerente":
        projetos = controle_projeto.visualizarProjeto(usuario)
        for p in projetos:
            id_proj = next((k for k, v in banco.projetos.items() if v == p), None)
            resposta.append({
                "id": id_proj,
                "nome": p.get_nome()
            })
    else:
        projetos = controle_projeto.retornarProjetosIntegrante(usuario)
        for p in projetos:
            id_proj = next((k for k, v in banco.projetos.items() if v == p), None)
            resposta.append({
                "id": id_proj,
                "nome": p.get_nome()
            })

    return jsonify(resposta), 200


@app.route('/api/projetos/<int:id_projeto>', methods=['GET'])
def obter_detalhes_projeto(id_projeto):
    """Endpoint GET para carregar as informacoes detalhadas de um projeto especifico."""
    email_usuario = request.args.get('usuario_logado')

    usuario = banco.buscar_usuario(email_usuario)

    if usuario is None:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    detalhes = controle_projeto.obterDetalhesProjeto(id_projeto, usuario)

    if detalhes is None:
        return jsonify({"erro": "Projeto não encontrado"}), 404

    return jsonify(detalhes), 200


@app.route('/api/projetos', methods=['POST'])
def criar_projeto():
    """Endpoint POST para criar um novo projeto (Acesso restrito a Gerente)."""
    dados = request.json or {}

    email_gerente = dados.get('usuario_logado')
    nome_projeto = dados.get('nome')

    gerente = banco.buscar_usuario(email_gerente)

    if gerente is None or gerente.get_papel() != "Gerente":
        return jsonify({"erro": "Apenas gerentes podem criar projetos"}), 403

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


@app.route('/api/projetos/<int:id_projeto>/integrantes', methods=['POST'])
def vincular_integrante_projeto(id_projeto):
    """Endpoint POST para vincular um integrante existente a um projeto."""
    dados = request.json or {}
    email_gerente = dados.get('usuario_logado')
    email_integrante = dados.get('email_integrante')

    gerente = banco.buscar_usuario(email_gerente)
    if gerente is None or gerente.get_papel() != "Gerente":
        return jsonify({"erro": "Apenas gerentes podem vincular integrantes a projetos"}), 403

    # Executa a vinculacao no controlador
    resultado = controle_projeto.adicionarIntegrante(
        id_projeto=id_projeto,
        email_integrante=email_integrante,
        gerente=gerente
    )

    # Trata caso o método retorne uma tupla (sucesso, mensagem) ou apenas um booleano
    if isinstance(resultado, tuple):
        sucesso, mensagem = resultado
    else:
        sucesso = bool(resultado)
        mensagem = "Integrante vinculado ao projeto com sucesso!" if sucesso else "Erro ao vincular integrante ao projeto."

    if sucesso:
        return jsonify({"mensagem": mensagem}), 200
    return jsonify({"erro": mensagem}), 400

@app.route('/api/projetos/<int:id_projeto>/tarefas/<int:id_tarefa>/atribuir', methods=['POST'])
def rota_atribuir_tarefa(id_projeto, id_tarefa):
    dados = request.json or {}
    email_gerente = dados.get('usuario_logado')
    email_integrante = dados.get('email_integrante')

    # A API faz o resgate dos OBJETOS pelo ID
    projeto_obj = banco.buscar_projeto(id_projeto)
    tarefa_obj = banco.tarefas.get(id_tarefa)

    if not projeto_obj or not tarefa_obj:
        return jsonify({"erro": "Projeto ou tarefa não encontrados."}), 404

    # Repassa os objetos para o Controlador (respeitando o diagrama de classes)
    resposta, status_code = controle_tarefa.atribuir_tarefa(
        projeto=projeto_obj, 
        tarefa=tarefa_obj, 
        email_gerente=email_gerente, 
        email_integrante=email_integrante
    )
    return jsonify(resposta), status_code

@app.route('/api/tarefas/<int:id_tarefa>/status', methods=['POST'])
def rota_atualizar_status(id_tarefa):
    dados = request.json or {}
    novo_status = dados.get('novo_status')
    texto_relatorio = dados.get('texto_relatorio')

    tarefa_obj = banco.tarefas.get(id_tarefa)
    
    # Se houver texto, a API já cria o objeto Relatório!
    relatorio_obj = Relatorio(texto_relatorio) if texto_relatorio else None

    # Repassa os objetos para o Controlador
    resposta, status_code = controle_tarefa.atualizar_status_tarefa(
        tarefa=tarefa_obj,
        novo_status=novo_status,
        relatorio=relatorio_obj
    )
    return jsonify(resposta), status_code

if __name__ == '__main__':
    print("Servidor rodando! Acesse http://127.0.0.1:5000 no seu navegador.")
    app.run(debug=True, port=5000)