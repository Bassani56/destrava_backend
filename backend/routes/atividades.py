
from flask import Blueprint, request, jsonify
from bson import ObjectId

from database import db

atividades_bp = Blueprint("atividades", __name__)

atividades = db["atividades"]
amizades = db["amizades"]
usuarios = db["usuarios"]


@atividades_bp.route("/listarCorridas", methods=["GET"])
def listarCorridas():
    usuario_id = request.args.get("usuario_id")

    if not usuario_id or not ObjectId.is_valid(usuario_id):
        return jsonify({
            "mensagem": "ID de usuário inválido."
        }), 400

    try:
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

    except Exception as e:
        print(f"Erro ao listar corridas: {e}")

        return jsonify({
            "mensagem": "Erro ao listar corridas.",
            "erro": str(e)
        }), 500


@atividades_bp.route("/salvarCorrida", methods=["POST"])
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

    try:
        usuario_object_id = ObjectId(usuario_id)

        usuario = usuarios.find_one({
            "_id": usuario_object_id
        })

        if not usuario:
            return jsonify({
                "mensagem": "Usuário não encontrado."
            }), 404

        atividade = {
            "usuario_id": usuario_object_id,
            "tempo": dado.get("tempo", ""),
            "distancia": dado.get("distancia", "0"),
            "pace": dado.get("pace", "--:--"),
            "data": dado.get("data"),
            "pontos": dado.get("pontos", [])
        }

        resultado = atividades.insert_one(atividade)

        return jsonify({
            "mensagem": "Corrida salva com sucesso!",
            "id": str(resultado.inserted_id)
        }), 201

    except Exception as e:
        print(f"Erro ao salvar corrida: {e}")

        return jsonify({
            "mensagem": "Erro ao salvar corrida.",
            "erro": str(e)
        }), 500


@atividades_bp.route("/feed", methods=["GET"])
def buscar_feed():
    usuario_id = request.args.get("usuario_id")

    if not usuario_id or not ObjectId.is_valid(usuario_id):
        return jsonify({
            "erro": "ID do usuário inválido."
        }), 400

    try:
        usuario_oid = ObjectId(usuario_id)

        # 1. Buscar amizades aceitas
        relacoes = amizades.find({
            "$or": [
                {"solicitante_id": usuario_oid},
                {"destinatario_id": usuario_oid}
            ],
            "status": "aceita"
        })

        # 2. Identificar o usuário e seus amigos
        ids_usuarios = {usuario_oid}

        for relacao in relacoes:
            solicitante = relacao["solicitante_id"]
            destinatario = relacao["destinatario_id"]

            if solicitante == usuario_oid:
                ids_usuarios.add(destinatario)
            else:
                ids_usuarios.add(solicitante)

        # 3. Buscar atividades desses usuários
        resultado = atividades.find({
            "usuario_id": {"$in": list(ids_usuarios)}
        }).sort("data", -1).limit(50)

        # 4. Buscar os dados dos usuários
        lista_usuarios = usuarios.find({
            "_id": {"$in": list(ids_usuarios)}
        })

        usuarios_por_id = {
            str(usuario["_id"]): usuario
            for usuario in lista_usuarios
        }

        # 5. Montar o feed
        feed = []

        for atividade in resultado:
            id_usuario = str(atividade["usuario_id"])
            usuario = usuarios_por_id.get(id_usuario)

            if not usuario:
                continue

            data = atividade.get("data")

            feed.append({
                "id": str(atividade["_id"]),
                "usuario_id": id_usuario,
                "nome": usuario.get(
                    "nome",
                    usuario.get("nomeUsuario", "Usuário")
                ),
                "tempo": atividade.get("tempo", ""),
                "distancia": atividade.get("distancia", ""),
                "pace": atividade.get("pace", "--:--"),
                "data": (
                    data.isoformat()
                    if hasattr(data, "isoformat")
                    else str(data)
                ),
                "pontos": atividade.get("pontos", [])
            })

        return jsonify(feed), 200

    except Exception as e:
        print(f"Erro ao carregar feed: {e}")

        return jsonify({
            "erro": "Não foi possível carregar o feed.",
            "detalhes": str(e)
        }), 500