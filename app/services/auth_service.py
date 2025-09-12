# app/services/auth_service.py
from __future__ import annotations

from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Usuario


class AuthService:
    """Serviço de autenticação e registro de usuários."""

    @staticmethod
    def register(email: str, senha: str) -> Usuario:
        """
        Registra novo usuário com email/senha.
        Lança ValueError em caso de entrada inválida ou email duplicado.
        """
        if not email or not senha:
            raise ValueError("email e senha são obrigatórios")

        user = Usuario(
            email=email.strip().lower(),
            password_hash=generate_password_hash(senha),
        )
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ValueError("email já foi cadastrado")
        return user

    @staticmethod
    def authenticate(email: str, senha: str) -> Optional[Usuario]:
        """
        Retorna o usuário autenticado ou None se credenciais inválidas.
        """
        if not email or not senha:
            return None

        user = Usuario.query.filter_by(email=email.strip().lower()).first()
        if user and check_password_hash(user.password_hash, senha):
            return user
        return None


# instância "singleton" para import conveniente (como já estava)
auth_service = AuthService()
