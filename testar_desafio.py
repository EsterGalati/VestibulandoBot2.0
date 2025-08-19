import requests
import json

# URL base do seu servidor Flask
BASE_URL = "http://127.0.0.1:5000"

# --- PARTE 1: PEGAR UMA QUESTÃO ---
ano = 2021
res = requests.get(f"{BASE_URL}/desafio/questao/{ano}")

if res.status_code != 200:
    print("Erro ao buscar questão:", res.text)
    exit()

questao = res.json()
print("Questão recebida:")
print(json.dumps(questao, indent=2, ensure_ascii=False))

# --- PARTE 2: ENVIAR RESPOSTA DO USUÁRIO ---
# Aqui você escolhe uma resposta aleatória só para testar
import random
resposta = random.choice(["A", "B", "C", "D", "E"])

usuario_id = 1  # Certifique-se de que este usuário existe no banco
questao_id = questao["id"]

payload = {
    "usuario_id": usuario_id,
    "questao_id": questao_id,
    "resposta": resposta
}

resposta_post = requests.post(f"{BASE_URL}/desafio/responder", json=payload)

if resposta_post.status_code != 200:
    print("Erro ao enviar resposta:", resposta_post.text)
    exit()

resultado = resposta_post.json()
print("\nResposta registrada:")
print(json.dumps(resultado, indent=2, ensure_ascii=False))
