from flask import jsonify
from flask_login import login_required
from app.services.usuario_service import UsuarioService


class UsuarioController:
    """Controller responsável pelas operações de usuário."""

    @staticmethod
    @login_required
    def get_usuario_logado():
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
        try:
            usuarios = UsuarioService.get_todos_usuarios()
            return jsonify(usuarios), 200
        except Exception as e:
            print(f"❌ Erro em get_todos_usuarios: {e}")
            return jsonify({"erro": "Erro interno ao listar usuários"}), 500

    @staticmethod
    @login_required
    def get_alunos_do_professor(cod_professor):
        """Retorna todos os alunos vinculados a um professor específico."""
        try:
            alunos = UsuarioService.get_alunos_do_professor(cod_professor)
            if not alunos:
                return jsonify({"mensagem": "Nenhum aluno vinculado a este professor."}), 404
            return jsonify(alunos), 200
        except Exception as e:
            print(f"❌ Erro em get_alunos_do_professor: {e}")
            return jsonify({"erro": "Erro interno ao buscar alunos do professor"}), 500
