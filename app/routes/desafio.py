from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.controllers import desafio_controller

bp = Blueprint("desafio_api", __name__)


@bp.get("/proxima")
@login_required
def proxima():
    body, code = desafio_controller.proxima_controller()
    if code == 204:
        return ("", 204)
    return jsonify(body), code


@bp.post("/responder")
@login_required
def responder():
    data = request.get_json(force=True, silent=True) or {}
    try:
        body, code = desafio_controller.responder_controller(data)
        return jsonify(body), code
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
