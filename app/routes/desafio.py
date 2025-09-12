from flask import Blueprint, request
from flask_login import login_required
from app.controllers.desafio_controller import DesafioController

bp = Blueprint("desafio", __name__)

@bp.get("/proxima")
@login_required
def proxima():
    return DesafioController.proxima()

@bp.post("/responder")
@login_required
def responder():
    return DesafioController.responder(request.get_json(silent=True) or {})
