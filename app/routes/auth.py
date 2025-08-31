from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.controllers import auth_controller

bp = Blueprint("auth_api", __name__)


@bp.post("/register")
def register():
    data = request.get_json(force=True, silent=True) or {}
    try:
        body, code = auth_controller.register_controller(data)
        return jsonify(body), code
    except ValueError as e:
        msg = str(e)
        code = 409 if msg == "email já foi cadastrado" else 400
        return jsonify({"error": msg}), code


@bp.post("/login")
def login():
    data = request.get_json(force=True, silent=True) or {}
    body, code = auth_controller.login_controller(data)
    return jsonify(body), code


@bp.post("/logout")
@login_required
def logout():
    body, code = auth_controller.logout_controller()
    return jsonify(body), code


@bp.get("/me")
@login_required
def me():
    body, code = auth_controller.me_controller()
    return jsonify(body), code
