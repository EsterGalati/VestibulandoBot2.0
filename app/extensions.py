# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
# se não tiver páginas server-side, esse atributo é irrelevante:
login_manager.login_view = "pages.login"
