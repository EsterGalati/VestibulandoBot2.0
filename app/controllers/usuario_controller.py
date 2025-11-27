from flask import jsonify, request
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

    @staticmethod
    @login_required
    def atualizar(cod_usuario: int):
        """
        Atualiza nome e e-mail do usuário.
        Regras:
          - Usuário comum: só pode alterar o próprio registro.
          - Admin: pode alterar qualquer usuário.
        Body: { "nome": str, "email": str }
        """
        try:
            # permissão
            is_admin = bool(getattr(current_user, "is_admin", False))
            is_self = getattr(current_user, "cod_usuario", None) == int(cod_usuario)
            if not (is_admin or is_self):
                return jsonify({"erro": "Acesso negado"}), 403

            data = request.get_json(silent=True) or {}
            nome = data.get("nome")
            email = data.get("email")

            if nome is None or email is None:
                return jsonify({"erro": "Campos obrigatórios: nome e email."}), 400

            result = UsuarioService.atualizar_perfil(
                target_id=cod_usuario,
                nome=nome,
                email=email,
            )

            if "erro" in result:
                msg = (result.get("erro") or "").lower()
                status = 409 if ("uso" in msg or "conflito" in msg) else 400
                return jsonify(result), status

            return jsonify(result), 200

        except Exception as e:
            print(f"❌ Erro em atualizar (PUT): {e}")
            return jsonify({"erro": "Erro interno ao atualizar usuário"}), 500