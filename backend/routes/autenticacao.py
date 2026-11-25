from flask import Blueprint, request, jsonify
from database import usuarios

from bson import ObjectId
from bson.errors import InvalidId


from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from pymongo.errors import DuplicateKeyError

from database import usuarios

autenticacao_bp = Blueprint(
    "autenticacao",
    __name__
)

@autenticacao_bp.route("/cadastro", methods=["POST"])
def cadastro():
    dado = request.get_json()

    if not dado:
        return jsonify({
            "mensagem": "Dados não enviados."
        }), 400

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
        "senha": generate_password_hash(senha),
        "tipo": "atleta"
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


@autenticacao_bp.route("/login", methods=["POST"])
def login():
    dado = request.get_json()

    if not dado:
        return jsonify({
            "mensagem": "Dados não enviados."
        }), 400

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
            "email": usuario["email"],
            "tipo": usuario.get("tipo", "atleta")
        }), 200

    return jsonify({
        "sucesso": False,
        "mensagem": "E-mail ou senha incorretos."
    }), 401


@autenticacao_bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    lista_usuarios = []

    for usuario in usuarios.find(
        {"tipo": {"$ne": "admin"}},
        {"senha": 0}
    ):
        lista_usuarios.append({
            "id": str(usuario["_id"]),
            "nome": usuario["nome"],
            "email": usuario["email"]
        })

    return jsonify(lista_usuarios), 200

@autenticacao_bp.route("/usuarios/<id>", methods=["DELETE"])
def excluir_usuario(id):
    try:
        usuario_id = ObjectId(id)
    except InvalidId:
        return jsonify({
            "mensagem": "ID de usuário inválido."
        }), 400

    resultado = usuarios.delete_one({
        "_id": usuario_id
    })

    if resultado.deleted_count == 0:
        return jsonify({
            "mensagem": "Usuário não encontrado."
        }), 404

    return jsonify({
        "mensagem": "Usuário removido com sucesso!"
    }), 200