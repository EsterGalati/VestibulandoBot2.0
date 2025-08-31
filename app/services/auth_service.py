from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models import Usuario


def register(email: str, senha: str) -> Usuario:
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
        raise ValueError("email_ja_cadastrado")
    return user


def authenticate(email: str, senha: str) -> Usuario | None:
    if not email or not senha:
        return None
    user = Usuario.query.filter_by(email=email.strip().lower()).first()
    if user and check_password_hash(user.password_hash, senha):
        return user
    return None
