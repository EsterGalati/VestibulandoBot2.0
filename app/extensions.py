# app/extensions.py
from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from flask_migrate import Migrate
from flask_cors import CORS  # ← Adicionado


class Extensions:
    """Wrapper para inicializar e expor extensões Flask de forma organizada."""

    def __init__(self):
        # instâncias reais das extensões
        self.db = SQLAlchemy()
        self.login_manager = LoginManager()
        self.oauth = OAuth()
        self.migrate = Migrate()
        self.cors = CORS()  # ← Adicionado

        # ajustes default
        # API não deve redirecionar para página de login HTML
        self.login_manager.login_view = None

    def init_app(self, app) -> None:
        """Inicializa todas as extensões com a aplicação Flask."""
        self.db.init_app(app)
        self.login_manager.init_app(app)
        self.oauth.init_app(app)
        self.cors.init_app(app)  # ← Adicionado
        # importante: migrate depende de 'app' e 'db'
        self.migrate.init_app(app, self.db)


# instância única usada pelo resto da app
_ext = Extensions()

# aliases para uso em outros módulos
db: SQLAlchemy = _ext.db
login_manager: LoginManager = _ext.login_manager
oauth: OAuth = _ext.oauth
migrate: Migrate = _ext.migrate
cors: CORS = _ext.cors  # ← Adicionado

# função auxiliar para inicialização manual (caso precise)
def init_app(app) -> None:
    """Inicializa todas as extensões (atalho)."""
    _ext.init_app(app)