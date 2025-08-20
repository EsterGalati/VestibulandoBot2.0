# ai_client.py
import os
from dotenv import load_dotenv

# OpenAI SDK v1.x
from openai import OpenAI

load_dotenv()  # carrega variáveis do .env

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
_client = None
if OPENAI_API_KEY:
    _client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = (
    "Você é um tutor paciente e objetivo para o ENEM. "
    "Explique com clareza e passo a passo quando fizer sentido, "
    "evite jargões e foque no raciocínio e nas definições-chave. "
    "Se a dúvida for ambígua, peça o mínimo de esclarecimento."
)

def responder_duvida(pergunta: str) -> str:
    """
    Retorna a resposta da IA. Se a chave não estiver configurada, devolve uma mensagem amigável.
    """
    if not _client:
        return ("⚠️ IA indisponível: configure sua chave no arquivo .env "
                "(OPENAI_API_KEY=...).")

    try:
        # Chat Completions (estável na SDK 1.x)
        completion = _client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            max_tokens=600,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": pergunta.strip()},
            ],
        )
        return (completion.choices[0].message.content or "").strip()
    except Exception as e:
        return f"⚠️ Erro ao consultar a IA: {e}"
