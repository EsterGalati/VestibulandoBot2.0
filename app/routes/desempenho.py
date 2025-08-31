from flask import Blueprint, jsonify
from flask_login import login_required
from app.controllers import desempenho_controller

bp = Blueprint("desempenho_api", __name__)


@bp.get("/resumo")
@login_required
def resumo():
    body, code = desempenho_controller.resumo_controller()
    return jsonify(body), code


@bp.get("/por-ano")
@login_required
def por_ano():
    body, code = desempenho_controller.por_ano_controller()
    return jsonify(body), code


@bp.get("/por-assunto")
@login_required
def por_assunto():
    body, code = desempenho_controller.por_assunto_controller()
    return jsonify(body), code
