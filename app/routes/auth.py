from flask import Blueprint, request
from flask_login import login_required
from app.controllers.auth_controller import AuthController

bp = Blueprint("auth", __name__)

@bp.post("/register")
def register():
    return AuthController.register(request.get_json(silent=True) or {})

@bp.post("/login")
def login():
    return AuthController.login(request.get_json(silent=True) or {})

@bp.post("/logout")
@login_required
def logout():
    return AuthController.logout()

@bp.get("/me")
def me():
    return AuthController.me()
