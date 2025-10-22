# app/routes/usuario.py
from flask import Blueprint
from app.controllers.usuario_controller import UsuarioController

bp = Blueprint("usuario", __name__, url_prefix="/api/v1/usuario")

# GET /api/v1/usuario/logado → retorna o usuário logado
bp.route("/logado", methods=["GET"])(UsuarioController.get_usuario_logado)

# GET /api/v1/usuario → retorna todos os usuários (somente admins)
bp.route("/", methods=["GET"])(UsuarioController.get_todos_usuarios)
