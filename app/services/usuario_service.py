# app/services/usuario_service.py
from typing import Optional, List, Dict
from flask_login import current_user
from app.models.usuario import Usuario


class UsuarioService:
    """Serviço para operações relacionadas a usuários."""

    @staticmethod
    def get_todos_usuarios() -> List[Dict]:
        """Retorna todos os usuários em formato dicionário."""
        usuarios = Usuario.query.order_by(Usuario.cod_usuario).all()
        return [u.to_dict() for u in usuarios]

    @staticmethod
    def get_usuario_logado() -> Optional[Dict]:
        """
        Retorna o usuário atualmente autenticado (usando Flask-Login).
        Retorna None se não houver usuário autenticado.
        """
        if current_user and getattr(current_user, "is_authenticated", False):
            # current_user pode já ser uma instância de Usuario
            try:
                return current_user.to_dict()
            except Exception:
                # fallback caso current_user não tenha to_dict (defensive)
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

usuario_service = UsuarioService()
