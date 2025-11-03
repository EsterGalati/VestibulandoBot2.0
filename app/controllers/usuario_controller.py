from flask import jsonify
from flask_login import login_required, current_user
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
            if not current_user.is_admin:
                return jsonify({"erro": "Acesso negado"}), 403

            usuarios = UsuarioService.get_todos_usuarios_com_resultados()
            return jsonify(usuarios), 200
        except Exception as e:
            print(f"❌ Erro em get_todos_usuarios: {e}")
            return jsonify({"erro": "Erro interno ao listar usuários"}), 500

    @staticmethod
    @login_required
    def get_alunos_do_professor(cod_professor):
        """
        Retorna os alunos vinculados ao professor informado, com resultados, simulado e matérias.
        Permissão: admin OU o próprio professor.
        """
        try:
            if not (current_user.is_admin or current_user.cod_usuario == int(cod_professor)):
                return jsonify({"erro": "Acesso negado"}), 403

            alunos = UsuarioService.get_alunos_do_professor(cod_professor)
            if not alunos:
                return jsonify({"mensagem": "Nenhum aluno vinculado a este professor."}), 404

            return jsonify(alunos), 200
        except Exception as e:
            print(f"❌ Erro em get_alunos_do_professor: {e}")
            return jsonify({"erro": "Erro interno ao buscar alunos do professor"}), 500
        
    @staticmethod
    @login_required
    def associar_alunos_ao_professor(cod_professor):
        """Associa automaticamente alunos a um professor (simulação do CSV)."""
        try:
            resultado = UsuarioService.associar_alunos_ao_professor(cod_professor)
            if "erro" in resultado:
                return jsonify(resultado), 400
            return jsonify(resultado), 200
        except Exception as e:
            print(f"❌ Erro em associar_alunos_ao_professor: {e}")
            return jsonify({"erro": "Erro interno ao associar alunos"}), 500
