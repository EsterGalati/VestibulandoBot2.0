from flask import Blueprint, request

from app.controllers.chat_controller import ChatController

bp = Blueprint("chat", __name__)


@bp.post("/perguntar")
def perguntar():
    return ChatController.perguntar(request.get_json(silent=True) or {})
