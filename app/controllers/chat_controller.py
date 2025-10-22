# app/controllers/chat_controller.py
from flask import request, jsonify
from app.services.chat_service import ChatService

class ChatController:
    """Controller responsável por lidar com as requisições do chat."""

    @staticmethod
    def gerar_resposta():
        """
        Recebe uma mensagem do usuário, chama o serviço de chat e retorna a resposta.
        """
        dados = request.get_json() or {}
        message = dados.get("message", "").strip()

        if not message:
            return jsonify({"erro": "Campo 'mensagem' é obrigatório."}), 400

        try:
            resposta = ChatService.gerar_resposta(message)
            return jsonify({"resposta": resposta}), 200
        except Exception as e:
            print(f"❌ Erro no ChatController: {e}")
            return jsonify({"erro": "Erro ao processar mensagem"}), 500
