# app/models/usuario.py
from __future__ import annotations

from typing import Optional, Dict
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Index
from app.extensions import db


class Usuario(UserMixin, db.Model):
    """Usuário do sistema (aluno/professor)."""

    __tablename__ = "usuarios"

    # -----------------------
    # Colunas
    # -----------------------
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # normalizar email para lower-case em métodos de criação/atualização
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)

    password_hash = db.Column(db.String(255), nullable=False)

    nome = db.Column(db.String(120), nullable=True, default="")

    # flag para perfis administrativos (professor/coordenador)
    is_admin = db.Column(db.Boolean, nullable=False, default=False, index=True)

    criado_em = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        # índice composto útil para listagens por perfil e ordem temporal
        Index("ix_usuarios_admin_data", "is_admin", "criado_em"),
    )

    # -----------------------
    # Métodos de domínio
    # -----------------------
    def set_password(self, password: str) -> None:
        """Define (ou redefine) a senha do usuário."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Valida a senha informada."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> Dict:
        """Serialização segura para APIs (não expõe hash)."""
        return {
            "id": self.id,
            "email": self.email,
            "nome": self.nome or "",
            "is_admin": bool(self.is_admin),
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
        }

    # -----------------------
    # Consultas comuns
    # -----------------------
    @classmethod
    def normalize_email(cls, email: str) -> str:
        return (email or "").strip().lower()

    @classmethod
    def get_by_id(cls, user_id: int) -> Optional["Usuario"]:
        return cls.query.get(int(user_id))

    @classmethod
    def get_by_email(cls, email: str) -> Optional["Usuario"]:
        return cls.query.filter_by(email=cls.normalize_email(email)).first()

    @classmethod
    def create(
        cls,
        *,
        email: str,
        password: str,
        nome: str = "",
        is_admin: bool = False,
        commit: bool = True,
    ) -> "Usuario":
        """Cria um novo usuário já com senha hasheada."""
        user = cls(
            email=cls.normalize_email(email),
            nome=(nome or "").strip(),
            is_admin=bool(is_admin),
        )
        user.set_password(password)
        db.session.add(user)
        if commit:
            db.session.commit()
        return user

    @classmethod
    def authenticate(cls, *, email: str, password: str) -> Optional["Usuario"]:
        """Autentica por email/senha; retorna usuário ou None."""
        user = cls.get_by_email(email)
        if user and user.check_password(password):
            return user
        return None

    # Flask-Login: UserMixin já fornece is_authenticated, is_active, etc.

    def __repr__(self) -> str:  # debug/dev
        return f"<Usuario id={self.id} email={self.email} admin={self.is_admin}>"
