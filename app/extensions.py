# app/extensions.py
from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth


class Extensions:
    """Wrapper para inicializar e expor extensões Flask de forma organizada."""

    def __init__(self):
        # instâncias reais das extensões
        self.db = SQLAlchemy()
        self.login_manager = LoginManager()
        self.oauth = OAuth()

        # ajustes default
        self.login_manager.login_view = None  # API não redireciona para login HTML

    def init_app(self, app) -> None:
        """Inicializa todas as extensões com a aplicação Flask."""
        self.db.init_app(app)
        self.login_manager.init_app(app)
        self.oauth.init_app(app)


# instância única usada pelo resto da app
_ext = Extensions()

# aliases para uso em outros módulos
db: SQLAlchemy = _ext.db
login_manager: LoginManager = _ext.login_manager
oauth: OAuth = _ext.oauth

# função auxiliar para inicialização manual (caso precise)
def init_app(app) -> None:
    """Inicializa todas as extensões (atalho)."""
    _ext.init_app(app)
