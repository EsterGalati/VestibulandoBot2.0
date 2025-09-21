# app/controllers/auth_controller.py
from __future__ import annotations

from typing import Any, Dict, Tuple
from flask_login import login_user, logout_user, current_user

from app.services.auth_service import auth_service
from app.utils.schemas import usuario_to_dict


class AuthController:
    """Controller para autenticação e sessão de usuário."""

    @staticmethod
    def register(payload: Dict[str, Any]) -> Tuple[Dict, int]:
        """
        Registra um novo usuário e autentica na sessão.
        Espera payload com 'email' e 'senha'.
        """
        email = (payload.get("email") or "").strip().lower()
        senha = (payload.get("senha") or "").strip()

        user = auth_service.register(email, senha)
        login_user(user)
        return usuario_to_dict(user), 200

    @staticmethod
    def login(payload: Dict[str, Any]) -> Tuple[Dict, int]:
        """
        Autentica um usuário existente.
        Retorna 401 se credenciais inválidas.
        """
        email = (payload.get("email") or "").strip().lower()
        senha = (payload.get("senha") or "").strip()

        user = auth_service.authenticate(email, senha)
        if not user:
            return {"error": "invalid_credentials"}, 401

        login_user(user)
        return usuario_to_dict(user), 200

    @staticmethod
    def logout() -> Tuple[Dict, int]:
        """Finaliza a sessão do usuário."""
        logout_user()
        return {"ok": True}, 200

    @staticmethod
    def me() -> Tuple[Dict, int]:
        """Retorna o usuário autenticado ou 401 se não houver sessão."""
        if not current_user.is_authenticated:
            return {"error": "unauthenticated"}, 401
        return usuario_to_dict(current_user), 200
