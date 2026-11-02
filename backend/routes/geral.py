from flask import Blueprint, Flask, app, request, jsonify
from database import usuarios, atividades, amizades

from database import colecao

atividades_bp = Blueprint("atividades", __name__)

@atividades_bp.route("/", methods=["GET"])

def listar():
    dados = list(
        colecao.find(
            {},
            {"_id": 0}
        )
    )

    return jsonify(dados)


@atividades_bp.route("/insert", methods=["POST"])
def inserir():
    dado = request.json
    resultado = colecao.insert_one(dado)

    return jsonify({
        "mensagem": "Dado inserido com sucesso!",
        "id": str(resultado.inserted_id)
    })