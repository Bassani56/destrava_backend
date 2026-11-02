
import random
from datetime import datetime, timedelta
from flask import app, request, jsonify
from bson import ObjectId


from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os
from dotenv import load_dotenv

from werkzeug.security import generate_password_hash, check_password_hash
from pymongo.errors import DuplicateKeyError
from bson import ObjectId


import re


load_dotenv()

app = Flask(__name__)

CORS(app)

mongo_uri = os.getenv("MONGO_URI")

client = MongoClient(mongo_uri)

db = client["destrava"]

@app.route("/gerarAtividadesTeste", methods=["POST"])
def gerar_atividades_teste():
    try:
        # Os cinco usuários que você informou
        emails = [
            "gabriel@gmail.com",
            "daniel@gmail.com",
            "rafael@gmail.com",
            "joao@gmail.com",
            "guilherme@gmail.com"
        ]

        quantidade_por_usuario = 5
        atividades_teste = []

        for email in emails:
            usuario = db["usuarios"].find_one({"email": email})

            if not usuario:
                continue

            for _ in range(quantidade_por_usuario):
                # Distância entre 2 e 15 km
                distancia = round(random.uniform(2.0, 15.0), 2)

                # Ritmo entre 4:30 e 7:30 minutos por km
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

        if not atividades_teste:
            return jsonify({
                "sucesso": False,
                "mensagem": "Nenhum dos usuários informados foi encontrado."
            }), 404

        resultado = db["atividades"].insert_many(atividades_teste)

        return jsonify({
            "sucesso": True,
            "mensagem": "Atividades de teste geradas com sucesso.",
            "usuarios_encontrados": len({
                str(a["usuario_id"]) for a in atividades_teste
            }),
            "atividades_por_usuario": quantidade_por_usuario,
            "total_atividades": len(resultado.inserted_ids),
            "atividades_compartilhadas": sum(
                1 for a in atividades_teste if a["compartilhada"]
            ),
            "atividades_privadas": sum(
                1 for a in atividades_teste if not a["compartilhada"]
            )
        }), 201

    except Exception as erro:
        return jsonify({
            "sucesso": False,
            "mensagem": str(erro)
        }), 500
