from flask import Blueprint
from app.controllers.resposta_controller import RespostaController

resposta_bp = Blueprint("resposta_bp", __name__, url_prefix="/api/v1/respostas")

resposta_bp.route("/", methods=["GET"])(RespostaController.listar)
resposta_bp.route("/<int:cod_resposta>", methods=["GET"])(RespostaController.buscar)
resposta_bp.route("/", methods=["POST"])(RespostaController.registrar)
resposta_bp.route("/<int:cod_resposta>", methods=["DELETE"])(RespostaController.deletar)
