
from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime

from database import db

amizades_bp = Blueprint("amizades", __name__)

amizades = db["amizades"]
usuarios = db["usuarios"]


@amizades_bp.route("/amizades/solicitacoes", methods=["GET"])
def listar_solicitacoes():
    usuario_id = request.args.get("usuario_id")

    if not usuario_id or not ObjectId.is_valid(usuario_id):
        return jsonify({"erro": "ID do usuário inválido."}), 400

    solicitacoes = amizades.find({
        "destinatario_id": ObjectId(usuario_id),
        "status": "pendente"
    }).sort("data", -1)

    resultado = []

    for solicitacao in solicitacoes:
        usuario = usuarios.find_one({
            "_id": solicitacao["solicitante_id"]
        })

        if usuario:
            resultado.append({
                "id": str(solicitacao["_id"]),
                "solicitante_id": str(usuario["_id"]),
                "nome": usuario.get("nome", usuario.get("nomeUsuario", "Usuário")),
                "status": solicitacao["status"],
                "data": str(solicitacao.get("data", ""))
            })

    return jsonify(resultado), 200


@amizades_bp.route("/amizades/<amizade_id>/aceitar", methods=["PUT"])
def aceitar_solicitacao(amizade_id):
    usuario_id = request.args.get("usuario_id")

    if not ObjectId.is_valid(amizade_id):
        return jsonify({"erro": "ID da solicitação inválido."}), 400

    if not usuario_id or not ObjectId.is_valid(usuario_id):
        return jsonify({"erro": "ID do usuário inválido."}), 400

    resultado = amizades.update_one(
        {
            "_id": ObjectId(amizade_id),
            "destinatario_id": ObjectId(usuario_id),
            "status": "pendente"
        },
        {
            "$set": {
                "status": "aceita",
                "data_resposta": datetime.now()
            }
        }
    )

    if resultado.matched_count == 0:
        return jsonify({"erro": "Solicitação não encontrada."}), 404

    return jsonify({"mensagem": "Solicitação aceita!"}), 200


# EXCLUIR SOLICITAÇÃO
@amizades_bp.route("/amizades/<amizade_id>", methods=["DELETE"])
def excluir_solicitacao(amizade_id):
    usuario_id = request.args.get("usuario_id")

    if not ObjectId.is_valid(amizade_id):
        return jsonify({"erro": "ID da solicitação inválido."}), 400

    if not usuario_id or not ObjectId.is_valid(usuario_id):
        return jsonify({"erro": "ID do usuário inválido."}), 400

    resultado = amizades.delete_one({
        "_id": ObjectId(amizade_id),
        "destinatario_id": ObjectId(usuario_id),
        "status": "pendente"
    })

    if resultado.deleted_count == 0:
        return jsonify({"erro": "Solicitação não encontrada."}), 404

    return jsonify({"mensagem": "Solicitação excluída!"}), 200


@amizades_bp.route("/amizades/solicitar", methods=["POST"])
def solicitar_amizade():
    dados = request.get_json()

    solicitante_id = dados.get("solicitante_id")
    destinatario_id = dados.get("destinatario_id")

    if not ObjectId.is_valid(solicitante_id) or not ObjectId.is_valid(destinatario_id):
        return jsonify({"erro": "IDs inválidos."}), 400

    solicitante = ObjectId(solicitante_id)
    destinatario = ObjectId(destinatario_id)

    if solicitante == destinatario:
        return jsonify({"erro": "Você não pode adicionar a si mesmo."}), 400

    if not usuarios.find_one({"_id": destinatario}):
        return jsonify({"erro": "Usuário destinatário não encontrado."}), 404

    # Verifica se já existe uma solicitação ou amizade
    existente = amizades.find_one({
        "$or": [
            {
                "solicitante_id": solicitante,
                "destinatario_id": destinatario
            },
            {
                "solicitante_id": destinatario,
                "destinatario_id": solicitante
            }
        ],
        "status": {"$in": ["pendente", "aceita"]}
    })

    if existente:
        return jsonify({"erro": "Já existe uma solicitação ou amizade."}), 409

    amizades.insert_one({
        "solicitante_id": solicitante,
        "destinatario_id": destinatario,
        "status": "pendente",
        "data": datetime.now()
    })

    return jsonify({
        "mensagem": "Solicitação enviada!"
    }), 201