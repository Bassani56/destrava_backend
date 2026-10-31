import requests

url = "http://127.0.0.1:3000/cadastro"
senha = "123456"

usuarios = [
    {"nome": "Lucas Ferreira", "email": "lucas.ferreira@gmail.com"},
    {"nome": "Mariana Oliveira", "email": "mariana.oliveira@gmail.com"},
    {"nome": "Gabriel Santos", "email": "gabriel.santos@gmail.com"},
    {"nome": "Isabela Costa", "email": "isabela.costa@gmail.com"},
    {"nome": "Matheus Rodrigues", "email": "matheus.rodrigues@gmail.com"},
    {"nome": "Camila Almeida", "email": "camila.almeida@gmail.com"},
    {"nome": "Rafael Souza", "email": "rafael.souza@gmail.com"},
    {"nome": "Beatriz Lima", "email": "beatriz.lima@gmail.com"},
    {"nome": "Pedro Carvalho", "email": "pedro.carvalho@gmail.com"},
    {"nome": "Juliana Martins", "email": "juliana.martins@gmail.com"}
]

for usuario in usuarios:
    dados = {
        "nome": usuario["nome"],
        "email": usuario["email"],
        "senha": senha
    }

    resposta = requests.post(url, json=dados)

    if resposta.status_code == 201:
        print(f"✅ Cadastro realizado: {usuario['nome']}")
    elif resposta.status_code == 409:
        print(f"⚠️ E-mail já cadastrado: {usuario['email']}")
    else:
        print(
            f"❌ Erro para {usuario['nome']}: "
            f"{resposta.status_code} - {resposta.text}"
        )