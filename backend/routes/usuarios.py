from flask import Blueprint, request, jsonify
from bson import ObjectId
import re

from database import db

usuarios_bp = Blueprint("usuarios", __name__)

@usuarios_bp.route("/buscarUsuarios", methods=["GET"])
def buscar_usuarios():

    try:
        termo = request.args.get("q", "").strip()
        usuario_id = request.args.get("usuario_id", "").strip()

        if len(termo) < 2:
            return jsonify({
                "erro": "Digite pelo menos 2 caracteres para pesquisar."
            }), 400

        if not ObjectId.is_valid(usuario_id):
            return jsonify({
                "erro": "ID do usuário inválido."
            }), 400

        colecao_usuarios = db["usuarios"]

        termo_regex = re.escape(termo)

        filtro = {
            "$and": [
                {
                    "$or": [
                        {"nome": {"$regex": termo_regex, "$options": "i"}},
                        {"nomeUsuario": {"$regex": termo_regex, "$options": "i"}},
                        {"username": {"$regex": termo_regex, "$options": "i"}}
                    ]
                },
                {
                    "_id": {"$ne": ObjectId(usuario_id)}
                }
            ]
        }

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