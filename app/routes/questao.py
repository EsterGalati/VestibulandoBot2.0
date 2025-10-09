from flask import Blueprint
from app.controllers.questao_controller import QuestaoController

questao_bp = Blueprint("questao_bp", __name__, url_prefix="/api/v1/questoes")

# CRUD de questões
questao_bp.route("/", methods=["GET"])(QuestaoController.listar)
questao_bp.route("/<int:cod_questao>", methods=["GET"])(QuestaoController.buscar)
questao_bp.route("/", methods=["POST"])(QuestaoController.criar)
questao_bp.route("/<int:cod_questao>", methods=["PUT"])(QuestaoController.atualizar)
questao_bp.route("/<int:cod_questao>", methods=["DELETE"])(QuestaoController.deletar)
