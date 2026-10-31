from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os
from dotenv import load_dotenv

from werkzeug.security import generate_password_hash, check_password_hash
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

from datetime import datetime, timedelta
import random
import re


load_dotenv()

app = Flask(__name__)

CORS(app)

mongo_uri = os.getenv("MONGO_URI")

client = MongoClient(mongo_uri)

db = client["destrava"]
colecao = db["banco"]


usuarios = db["usuarios"]
# Impede que dois usuários tenham o mesmo e-mail
usuarios.create_index("email", unique=True)


atividades = db["atividades"]

@app.route("/", methods=["GET"])
def listar():
    dados = list(
        colecao.find(
            {},
            {"_id": 0}
        )
    )

    return jsonify(dados)


@app.route("/insert", methods=["POST"])
def inserir():
    dado = request.json

    resultado = colecao.insert_one(dado)

    return jsonify({
        "mensagem": "Dado inserido com sucesso!",
        "id": str(resultado.inserted_id)
    })

@app.route("/salvarCorrida", methods=["POST"])
def salvarCorrida():
    dado = request.get_json()

    if not dado:
        return jsonify({
            "mensagem": "Dados não enviados."
        }), 400

    usuario_id = dado.get("usuario_id")

    if not usuario_id or not ObjectId.is_valid(usuario_id):
        return jsonify({
            "mensagem": "ID de usuário inválido ou não enviado."
        }), 400

    # Converte o ID de texto para ObjectId
    usuario_object_id = ObjectId(usuario_id)

    # Verifica se o usuário existe
    usuario = usuarios.find_one({
        "_id": usuario_object_id
    })

    if not usuario:
        return jsonify({
            "mensagem": "Usuário não encontrado."
        }), 404

    # Prepara a atividade vinculada ao usuário
    atividade = {
        "usuario_id": usuario_object_id,
        "tempo": dado.get("tempo"),
        "distancia": dado.get("distancia"),
        "velocidadeMedia": dado.get("velocidadeMedia"),
        "data": dado.get("data")
    }

    resultado = atividades.insert_one(atividade)

    return jsonify({
        "mensagem": "Corrida salva com sucesso!",
        "id": str(resultado.inserted_id)
    }), 201


from bson import ObjectId

@app.route("/listarCorridas", methods=["GET"])
def listarCorridas():
    usuario_id = request.args.get("usuario_id")

    if not usuario_id or not ObjectId.is_valid(usuario_id):
        return jsonify({
            "mensagem": "ID de usuário inválido."
        }), 400

    dados = list(
        atividades.find(
            {"usuario_id": ObjectId(usuario_id)},
            {"_id": 0, "usuario_id": 0}
        ).sort("data", -1)
    )

    print(
        f"Listando corridas para o usuário_id: {usuario_id}, "
        f"quantidade: {len(dados)}"
    )

    return jsonify(dados), 200

@app.route("/cadastro", methods=["POST"])
def cadastro():
    dado = request.get_json()

    if not dado:
        return jsonify({"mensagem": "Dados não enviados."}), 400

    nome = dado.get("nome", "").strip()
    email = dado.get("email", "").strip().lower()
    senha = dado.get("senha", "")

    if not nome or not email or not senha:
        return jsonify({
            "mensagem": "Nome, e-mail e senha são obrigatórios."
        }), 400

    usuario = {
        "nome": nome,
        "email": email,
        "senha": generate_password_hash(senha)
    }

    try:
        resultado = usuarios.insert_one(usuario)

        return jsonify({
            "mensagem": "Usuário cadastrado com sucesso!",
            "id": str(resultado.inserted_id)
        }), 201

    except DuplicateKeyError:
        return jsonify({
            "mensagem": "Este e-mail já está cadastrado."
        }), 409

@app.route("/login", methods=["POST"])
def login():
    dado = request.get_json()

    if not dado:
        return jsonify({"mensagem": "Dados não enviados."}), 400

    email = dado.get("email", "").strip().lower()
    senha = dado.get("senha", "")

    if not email or not senha:
        return jsonify({
            "mensagem": "E-mail e senha são obrigatórios."
        }), 400

    usuario = usuarios.find_one({
        "email": email
    })

    if usuario and check_password_hash(usuario["senha"], senha):
        return jsonify({
            "sucesso": True,
            "mensagem": "Login realizado com sucesso!",
            "id": str(usuario["_id"]),
            "nome": usuario["nome"],
            "email": usuario["email"]
        }), 200

    return jsonify({
        "sucesso": False,
        "mensagem": "E-mail ou senha incorretos."
    }), 401







@app.route("/buscarUsuarios", methods=["GET"])
def buscar_usuarios():
    try:
        termo = request.args.get("q", "").strip()

        if len(termo) < 2:
            return jsonify({
                "erro": "Digite pelo menos 2 caracteres para pesquisar."
            }), 400

        # Coleção que contém os usuários cadastrados
        colecao_usuarios = db["usuarios"]

        # Pesquisa sem diferenciar letras maiúsculas e minúsculas
        termo_regex = re.escape(termo)

        filtro = {
            "$or": [
                {"nome": {"$regex": termo_regex, "$options": "i"}},
                {"nomeUsuario": {"$regex": termo_regex, "$options": "i"}},
                {"username": {"$regex": termo_regex, "$options": "i"}}
            ]
        }

        # Retorna somente os campos públicos necessários
        projecao = {
            "_id": 1,
            "nome": 1,
            "nomeUsuario": 1,
            "username": 1
        }

        usuarios = colecao_usuarios.find(
            filtro,
            projecao
        ).limit(20)

        resultados = []

        for usuario in usuarios:
            resultados.append({
                "id": str(usuario["_id"]),
                "nome": usuario.get("nome", ""),
                "nomeUsuario": usuario.get(
                    "nomeUsuario",
                    usuario.get("username", "")
                )
            })

        return jsonify(resultados), 200

    except Exception as erro:
        print(f"Erro ao buscar usuários: {erro}")

        return jsonify({
            "erro": "Não foi possível buscar usuários."
        }), 500







@app.route("/gerarAtividadesTeste", methods=["POST"])
def gerar_atividades_teste():
    try:
        print("\n=== INICIANDO GERAÇÃO DE ATIVIDADES ===")
        print("Banco:", db.name)
        print("Coleção:", atividades.name)

        emails = [
            "gabriel@gmail.com",
            "daniel@gmail.com",
            "rafael@gmail.com",
            "joao@gmail.com",
            "guilherme@gmail.com"
        ]

        quantidade_por_usuario = 5
        atividades_teste = []
        usuarios_encontrados = 0

        for email in emails:
            usuario = usuarios.find_one({
                "email": email.strip().lower()
            })

            if not usuario:
                print(f"USUÁRIO NÃO ENCONTRADO: {email}")
                continue

            usuarios_encontrados += 1

            print(
                f"Usuário encontrado: {usuario.get('nome', email)} "
                f"| ID: {usuario['_id']}"
            )

            for _ in range(quantidade_por_usuario):
                # Distância entre 2 e 15 km
                distancia = round(random.uniform(2.0, 15.0), 2)

                # Ritmo entre 4:30 e 7:30 por quilômetro
                ritmo_segundos = random.randint(270, 450)
                duracao_segundos = int(distancia * ritmo_segundos)

                horas = duracao_segundos // 3600
                minutos = (duracao_segundos % 3600) // 60
                segundos = duracao_segundos % 60

                tempo = f"{horas:02}:{minutos:02}:{segundos:02}"

                # Velocidade média em km/h
                velocidade = distancia / (duracao_segundos / 3600)

                # Data aleatória nos últimos 30 dias
                dias_atras = random.randint(0, 29)
                data_atividade = (
                    datetime.now() - timedelta(days=dias_atras)
                ).strftime("%Y-%m-%d")

                atividade = {
                    "usuario_id": usuario["_id"],
                    "distancia": f"{distancia:.2f}",
                    "tempo": tempo,
                    "velocidadeMedia": f"{velocidade:.2f}",
                    "data": data_atividade,
                    "compartilhada": random.choice([True, False]),
                    "dados_teste": True
                }

                atividades_teste.append(atividade)

        if usuarios_encontrados == 0:
            return jsonify({
                "sucesso": False,
                "mensagem": (
                    "Nenhum usuário foi encontrado. "
                    "Confira os e-mails na coleção usuarios."
                ),
                "banco": db.name,
                "colecao_usuarios": usuarios.name
            }), 404

        print("Usuários encontrados:", usuarios_encontrados)
        print("Atividades preparadas:", len(atividades_teste))

        resultado = atividades.insert_many(atividades_teste)

        compartilhadas = sum(
            1 for atividade in atividades_teste
            if atividade["compartilhada"]
        )

        privadas = len(atividades_teste) - compartilhadas

        print("Atividades inseridas:", len(resultado.inserted_ids))
        print("=== GERAÇÃO FINALIZADA ===\n")

        return jsonify({
            "sucesso": True,
            "mensagem": "Atividades de teste geradas com sucesso.",
            "banco": db.name,
            "colecao": atividades.name,
            "usuarios_encontrados": usuarios_encontrados,
            "atividades_por_usuario": quantidade_por_usuario,
            "total_atividades": len(resultado.inserted_ids),
            "atividades_compartilhadas": compartilhadas,
            "atividades_privadas": privadas
        }), 201

    except Exception:
        app.logger.exception("Erro ao gerar atividades de teste")

        return jsonify({
            "sucesso": False,
            "mensagem": "Erro ao gerar atividades. Consulte o terminal do Flask."
        }), 500




app.run(
    host="0.0.0.0",
    port=3000,
    debug=True
)