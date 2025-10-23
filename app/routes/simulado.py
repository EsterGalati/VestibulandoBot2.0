from flask import Blueprint
from app.controllers.simulado_controller import SimuladoController

simulado_bp = Blueprint("simulado_bp", __name__, url_prefix="/api/v1/simulados")

# --- SIMULADOS ---
simulado_bp.route("/", methods=["GET"])(SimuladoController.listar)
simulado_bp.route("/<int:cod_simulado>", methods=["GET"])(SimuladoController.buscar)
simulado_bp.route("/", methods=["POST"])(SimuladoController.criar)
simulado_bp.route("/<int:cod_simulado>", methods=["PUT"])(SimuladoController.atualizar)
simulado_bp.route("/<int:cod_simulado>", methods=["DELETE"])(SimuladoController.deletar)

# --- QUESTÕES DO SIMULADO ---
simulado_bp.route("/<int:cod_simulado>/questoes", methods=["GET"])(SimuladoController.listar_questoes)
simulado_bp.route("/<int:cod_simulado>/questoes", methods=["POST"])(SimuladoController.adicionar_questao)

# --- RESULTADOS ---
simulado_bp.route("/<int:cod_simulado>/resultados", methods=["GET"])(SimuladoController.listar_resultados)
simulado_bp.route("/<int:cod_simulado>/resultados", methods=["POST"])(SimuladoController.registrar_resultado)
simulado_bp.route("/resultados/usuario/<int:cod_usuario>", methods=["GET"])(SimuladoController.listar_resultados_por_usuario)