from flask import Blueprint
from flask_login import login_required
from app.controllers.desempenho_controller import DesempenhoController

bp = Blueprint("desempenho", __name__)

@bp.get("/resumo")
@login_required
def resumo():
    return DesempenhoController.resumo()

@bp.get("/por-ano")
@login_required
def por_ano():
    return DesempenhoController.por_ano()

@bp.get("/por-assunto")
@login_required
def por_assunto():
    return DesempenhoController.por_assunto()
