from __future__ import annotations
from typing import Optional, Dict
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class Usuario(UserMixin, db.Model):
    """Usuário do sistema (aluno, professor ou administrador)."""

    __tablename__ = "TB_USUARIO"

    cod_usuario = db.Column("COD_USUARIO", db.Integer, primary_key=True, autoincrement=True)
    nome_usuario = db.Column("NOME_USUARIO", db.String(120), nullable=False)
    email = db.Column("EMAIL", db.String(255), unique=True, nullable=False, index=True)
    senha_hash = db.Column("SENHA_HASH", db.String(255), nullable=False)
    is_admin = db.Column("IS_ADMIN", db.Boolean, nullable=False, default=False, index=True)

    respostas = db.relationship(
        "Resposta",
        back_populates="usuario",
        cascade="all, delete-orphan",
        lazy=True
    )

    resultados_simulados = db.relationship(
        "ResultadoSimulado",
        back_populates="usuario",
        cascade="all, delete-orphan",
        lazy=True
    )

    def set_password(self, password: str) -> None:
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.senha_hash, password)

    def to_dict(self) -> Dict:
        return {
            "cod_usuario": self.cod_usuario,
            "nome_usuario": self.nome_usuario,
            "email": self.email,
            "is_admin": bool(self.is_admin),
        }

    @classmethod
    def get_by_email(cls, email: str) -> Optional["Usuario"]:
        return cls.query.filter(db.func.lower(cls.email) == email.strip().lower()).first()

    @classmethod
    def create(
        cls,
        *,
        nome_usuario: str,
        email: str,
        senha: str,
        is_admin: bool = False,
        commit: bool = True,
    ) -> "Usuario":
        user = cls(
            nome_usuario=nome_usuario.strip(),
            email=email.strip().lower(),
            is_admin=bool(is_admin),
        )
        user.set_password(senha)
        db.session.add(user)
        if commit:
            db.session.commit()
        return user

    @classmethod
    def authenticate(cls, *, email: str, senha: str) -> Optional["Usuario"]:
        user = cls.get_by_email(email)
        if user and user.check_password(senha):
            return user
        return None

    @property
    def id(self):
        """Compatibilidade com Flask-Login."""
        return self.cod_usuario

    def get_id(self):
        """Retorna o identificador único do usuário como string."""
        return str(self.cod_usuario)

    def __repr__(self) -> str:
        return f"<Usuario cod={self.cod_usuario} email={self.email} admin={self.is_admin}>"
