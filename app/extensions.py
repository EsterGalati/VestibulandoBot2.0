# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()

login_manager = LoginManager()
# Em API pura, não queremos redirecionar para página de login:
login_manager.login_view = None

# OAuth (Google etc.)
oauth = OAuth()
