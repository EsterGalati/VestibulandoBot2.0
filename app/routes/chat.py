from flask import Blueprint
from app.controllers.chat_controller import ChatController

bp = Blueprint("bp", __name__)

# Rota POST para gerar resposta do chat
bp.route("/message", methods=["POST"])(ChatController.gerar_resposta)
