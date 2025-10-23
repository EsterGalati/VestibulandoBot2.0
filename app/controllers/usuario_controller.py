# app/controllers/usuario_controller.py
from flask import jsonify
from flask_login import login_required, current_user
from app.services.usuario_service import UsuarioService


class UsuarioController:
    """Controller responsável pelas operações de usuário."""

    @staticmethod
    @login_required
    def get_usuario_logado():
        """Retorna os dados do usuário logado."""
        try:
            usuario = UsuarioService.get_usuario_logado()
            if not usuario:
                return jsonify({"erro": "Usuário não autenticado"}), 401
            return jsonify(usuario), 200
        except Exception as e:
            print(f"❌ Erro em get_usuario_logado: {e}")
            return jsonify({"erro": "Erro interno ao buscar usuário logado"}), 500

    @staticmethod
    @login_required
    def get_todos_usuarios():
        """Lista todos os usuários (exemplo: rota protegida para admins)."""
        try:
            # if not getattr(current_user, "is_admin", False):
            #     return jsonify({"erro": "Acesso negado"}), 403

            usuarios = UsuarioService.get_todos_usuarios()
            return jsonify(usuarios), 200
        except Exception as e:
            print(f"❌ Erro em get_todos_usuarios: {e}")
            return jsonify({"erro": "Erro interno ao listar usuários"}), 500
