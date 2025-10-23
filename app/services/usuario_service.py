from typing import Optional, List, Dict
from flask_login import current_user
from app.models.usuario import Usuario
from app.models.rel_prof_aluno import RelProfAluno
from app.extensions import db


class UsuarioService:
    """Serviço para operações relacionadas a usuários."""

    @staticmethod
    def get_todos_usuarios() -> List[Dict]:
        usuarios = Usuario.query.order_by(Usuario.cod_usuario).all()
        return [u.to_dict() for u in usuarios]

    @staticmethod
    def get_usuario_logado() -> Optional[Dict]:
        if current_user and getattr(current_user, "is_authenticated", False):
            try:
                return current_user.to_dict()
            except Exception:
                return {
                    "cod_usuario": getattr(current_user, "cod_usuario", None),
                    "nome_usuario": getattr(current_user, "nome_usuario", None),
                    "email": getattr(current_user, "email", None),
                    "is_admin": bool(getattr(current_user, "is_admin", False)),
                }
        return None

    @staticmethod
    def get_usuario_por_id(cod_usuario: int) -> Optional[Dict]:
        usuario = Usuario.query.get(cod_usuario)
        if not usuario:
            return None
        return usuario.to_dict()

    @staticmethod
    def get_alunos_do_professor(cod_professor: int) -> List[Dict]:
        """
        Retorna todos os alunos vinculados a um professor específico.
        """
        relacoes = (
            db.session.query(Usuario)
            .join(RelProfAluno, Usuario.cod_usuario == RelProfAluno.cod_usuario_aluno)
            .filter(RelProfAluno.cod_usuario_prof == cod_professor)
            .order_by(Usuario.nome_usuario)
            .all()
        )

        return [aluno.to_dict() for aluno in relacoes]
