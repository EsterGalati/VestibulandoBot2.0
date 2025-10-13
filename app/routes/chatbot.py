from flask import Blueprint, request, jsonify
import os
import google.generativeai as genai

bp = Blueprint("chatbot", __name__)

@bp.route("/message", methods=["POST"])
def chatbot_message():
    data = request.get_json()
    user_message = data.get("message") if data else None

    if not user_message:
        return jsonify({"error": "Campo 'message' é obrigatório"}), 400

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"error": "GEMINI_API_KEY não configurada"}), 500

    try:
        # Configura a API Gemini
        genai.configure(api_key=api_key)

        # Inicializa o modelo Gemini 2.5 Flash
        model = genai.GenerativeModel("gemini-2.5-flash")

        # Gera a resposta
        response = model.generate_content(
            f"Você é o VestibulandoBot, um assistente especializado em vestibulares e ENEM."
            f"Responda de forma simples e objetiva: {user_message}",
            generation_config={
                "max_output_tokens": 1024,
                "temperature": 0.7,
            }
        )

        reply = (getattr(response, "content", None) or
                 getattr(response, "text", None) or
                 "").strip()
        if not reply:
            reply = "Desculpe, não consegui gerar uma resposta agora."

        return jsonify({"reply": reply})

    except Exception as e:
        print(f"❌ Erro ao chamar Gemini: {e}")
        return jsonify({"error": "Erro ao processar a mensagem com Gemini"}), 500
