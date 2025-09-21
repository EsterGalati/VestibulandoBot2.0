# app/__init__.py
from __future__ import annotations

import os
from flask import Flask, jsonify
from flask_cors import CORS

# torna opcional o python-dotenv
try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    def load_dotenv(*args, **kwargs):
        return False

from .extensions import db, login_manager, oauth, migrate


# =========================
# Configurações por classe
# =========================
class BaseConfig:
    """Configuração base da aplicação."""
    SECRET_KEY = os.getenv("SECRET_KEY", "troque-esta-chave")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///vestibulando.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Cookies: valores default (dev); produção sobrescreve abaixo
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False


class DevConfig(BaseConfig):
    """Ambiente de desenvolvimento (padrão)."""
    pass


class ProdConfig(BaseConfig):
    """Ambiente de produção (HTTPS + SameSite=None)."""
    SESSION_COOKIE_SAMESITE = "None"
    SESSION_COOKIE_SECURE = True


# =========================
# Construtor da aplicação
# =========================
def create_app(config_object: str | None = None) -> Flask:
    load_dotenv()
    app = Flask(__name__)

    # Escolhe config: string (dotted path) ou classe local
    env = os.getenv("ENV", "dev").lower()
    default_config = ProdConfig if env == "prod" else DevConfig
    app.config.from_object(config_object or default_config)

    # Extensões
    db.init_app(app)
    login_manager.init_app(app)
    oauth.init_app(app)
    migrate.init_app(app, db)  # <-- Migrate habilitado

    # --------- OAuth (Google) ---------
    oauth.register(
        name="google",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        # Descoberta OIDC
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        api_base_url="https://openidconnect.googleapis.com/v1/",
        client_kwargs={"scope": "openid email profile"},
    )

    # --------- CORS ---------
    origins = [
        o.strip()
        for o in os.getenv(
            "CORS_ORIGINS",
            "http://127.0.0.1:5173,http://localhost:5173"
        ).split(",")
        if o.strip()
    ]
    app.config["CORS_ORIGINS"] = origins

    CORS(
        app,
        supports_credentials=True,  # ok para cookies/sessão; com token também funciona
        resources={r"/api/*": {"origins": origins}},
        expose_headers=["Content-Type", "Authorization"],  # útil p/ front ler headers
    )

    # --------- Blueprints ---------
    from .routes.auth import bp as auth_bp
    from .routes.desafio import bp as desafio_bp
    from .routes.desempenho import bp as desempenho_bp

    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(desafio_bp, url_prefix="/api/v1/desafio")
    app.register_blueprint(desempenho_bp, url_prefix="/api/v1/desempenho")

    # --------- Login loader ---------
    from .models.usuario import Usuario

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(Usuario, int(user_id))

    # --------- Raiz ---------
    @app.get("/")
    def root():
        return jsonify(
            {
                "name": "Vestibulando API",
                "version": "v1",
                "endpoints": [
                    "/api/v1/auth/register",
                    "/api/v1/auth/login",
                    "/api/v1/auth/me",
                    "/api/v1/desafio/proxima",
                    "/api/v1/desafio/responder",
                    "/api/v1/desempenho/resumo",
                    "/api/v1/desempenho/por-ano",
                    "/api/v1/desempenho/por-assunto",
                ],
            }
        )

    return app
