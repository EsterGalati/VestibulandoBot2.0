# app/__init__.py
from flask import Flask, jsonify
from flask_cors import CORS
import os

# torna opcional o python-dotenv
try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv(*args, **kwargs):  # fallback no-op
        return False

from .extensions import db, login_manager
from .routes.auth import bp as auth_bp
from .routes.desafio import bp as desafio_bp
from .routes.desempenho import bp as desempenho_bp

# registra CLI se o módulo existir
try:
    from .cli import register_cli
except Exception:
    register_cli = None


def create_app(config_object: str | None = None) -> Flask:
    load_dotenv()
    app = Flask(__name__)

    # Config base
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "troque-esta-chave")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///vestibulando.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    if config_object:
        app.config.from_object(config_object)

    # Cookies por ambiente
    # DEV (default): mesmo host em portas diferentes -> Lax/False
    # PROD (ENV=prod): domínios diferentes com HTTPS -> None/True
    env = os.getenv("ENV", "dev").lower()
    if env == "prod":
        app.config.update(
            SESSION_COOKIE_SAMESITE="None",
            SESSION_COOKIE_SECURE=True,   # exige HTTPS
        )
    else:
        app.config.update(
            SESSION_COOKIE_SAMESITE="Lax",
            SESSION_COOKIE_SECURE=False,
        )

    # Extensões
    db.init_app(app)
    login_manager.init_app(app)

    # CORS (habilita cookies; origens configuráveis via env)
    # Ex.: CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
    cors_origins = os.getenv(
        "CORS_ORIGINS",
        "http://127.0.0.1:5173,http://localhost:5173",
    ).split(",")
    CORS(
        app,
        supports_credentials=True,
        resources={r"/api/*": {"origins": cors_origins}},
    )

    # Flask-Login
    from .models.usuario import Usuario

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(Usuario, int(user_id))

    # Blueprints (API)
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(desafio_bp, url_prefix="/api/v1/desafio")
    app.register_blueprint(desempenho_bp, url_prefix="/api/v1/desempenho")

    # CLI (db-init, import-questoes), se disponível
    if register_cli:
        register_cli(app)

    # Rota raiz (ping informativo)
    @app.get("/")
    def root():
        return jsonify({
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
        })

    return app
