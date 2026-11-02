from flask import Flask
from flask_cors import CORS

from routes.atividades import atividades_bp
from routes.autenticacao import autenticacao_bp
from routes.usuarios import usuarios_bp
from routes.amizades import amizades_bp

app = Flask(__name__)

CORS(app)

app.register_blueprint(atividades_bp)
app.register_blueprint(autenticacao_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(amizades_bp)

print(app.url_map)

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=3000,
        debug=True
    )