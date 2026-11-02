from flask import Blueprint, request, jsonify
from database import usuarios

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
            "email": usuario["email"]
        }), 200

    return jsonify({
        "sucesso": False,
        "mensagem": "E-mail ou senha incorretos."
    }), 401