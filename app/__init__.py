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

from .extensions import db, login_manager, oauth

# registra CLI se o módulo existir
try:
    from .cli import register_cli
except Exception:  # pragma: no cover
    register_cli = None


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
class AppFactory:
    """Responsável por construir e configurar a instância Flask."""

    def __init__(self, config_object: str | None = None) -> None:
        load_dotenv()
        self.app = Flask(__name__)

        # Escolhe config: string (dotted path) ou classe local
        env = os.getenv("ENV", "dev").lower()
        default_config = ProdConfig if env == "prod" else DevConfig
        self.app.config.from_object(config_object or default_config)

        # Extensões
        db.init_app(self.app)
        login_manager.init_app(self.app)
        oauth.init_app(self.app)

        # Etapas de configuração
        self._configure_oauth()
        self._configure_cors()
        self._configure_login_loader()
        self._register_blueprints()
        self._register_cli()
        self._register_root()

    # --------- detalhes ---------
    def _configure_oauth(self) -> None:
        oauth.register(
            name="google",
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            # Descoberta OIDC
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            api_base_url="https://openidconnect.googleapis.com/v1/",
            client_kwargs={"scope": "openid email profile"},
        )

    def _configure_cors(self) -> None:
        # Lê origens do .env e persiste na config
        origins = [
            o.strip()
            for o in os.getenv(
                "CORS_ORIGINS",
                "http://127.0.0.1:5173,http://localhost:5173",
            ).split(",")
            if o.strip()
        ]
        self.app.config["CORS_ORIGINS"] = origins

        CORS(
            self.app,
            supports_credentials=True,
            resources={r"/api/*": {"origins": origins}},
        )

    def _configure_login_loader(self) -> None:
        from .models.usuario import Usuario

        @login_manager.user_loader
        def load_user(user_id: str):
            return db.session.get(Usuario, int(user_id))

    def _register_blueprints(self) -> None:
        from .routes.auth import bp as auth_bp
        from .routes.desafio import bp as desafio_bp
        from .routes.desempenho import bp as desempenho_bp

        self.app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
        self.app.register_blueprint(desafio_bp, url_prefix="/api/v1/desafio")
        self.app.register_blueprint(desempenho_bp, url_prefix="/api/v1/desempenho")

    def _register_cli(self) -> None:
        if register_cli:
            register_cli(self.app)

    def _register_root(self) -> None:
        @self.app.get("/")
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


# compat: mantém a factory funcional original
def create_app(config_object: str | None = None) -> Flask:
    return AppFactory(config_object=config_object).app
