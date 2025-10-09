from flask import Blueprint
from app.controllers.materia_controller import MateriaController

materia_bp = Blueprint("materia_bp", __name__, url_prefix="/api/v1/materias")

# Rotas RESTful
materia_bp.route("/", methods=["GET"])(MateriaController.listar_todas)
materia_bp.route("/<int:cod_materia>", methods=["GET"])(MateriaController.buscar_por_id)
materia_bp.route("/", methods=["POST"])(MateriaController.criar)
materia_bp.route("/<int:cod_materia>", methods=["PUT"])(MateriaController.atualizar)
materia_bp.route("/<int:cod_materia>", methods=["DELETE"])(MateriaController.deletar)
