import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")

client = MongoClient(mongo_uri)

db = client["destrava"]

# Coleções
colecao = db["banco"]
usuarios = db["usuarios"]
atividades = db["atividades"]
amizades = db["amizades"]

def ensure_indexes():
    usuarios.create_index("email", unique=True)

    amizades.create_index(
        [
            ("solicitante_id", 1),
            ("destinatario_id", 1)
        ],
        unique=True,
        name="idx_solicitacao_unica"
    )

    amizades.create_index(
        [
            ("solicitante_id", 1),
            ("status", 1)
        ],
        name="idx_solicitante_status"
    )

    amizades.create_index(
        [
            ("destinatario_id", 1),
            ("status", 1)
        ],
        name="idx_destinatario_status"
    )