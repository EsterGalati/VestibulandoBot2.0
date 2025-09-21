# app/routes/auth.py
from flask import Blueprint, jsonify, redirect, url_for, request, session, current_app
from flask_login import login_required, login_user, logout_user, current_user
from ..extensions import oauth, db
from ..models.usuario import Usuario
from app.controllers.auth_controller import AuthController
from secrets import token_urlsafe
from authlib.integrations.base_client.errors import MismatchingStateError
import os

try:
    from werkzeug.security import generate_password_hash
except Exception:
    generate_password_hash = None

bp = Blueprint("auth", __name__)

# ---------- Fluxo clássico ----------
@bp.post("/register")
def register():
    return AuthController.register(request.get_json(silent=True) or {})

@bp.post("/login")
def login():
    return AuthController.login(request.get_json(silent=True) or {})

@bp.post("/logout")
@login_required
def logout():
    return AuthController.logout()

@bp.get("/me")
def me():
    return AuthController.me()

# ---------- Google OAuth ----------
@bp.get("/google")
@bp.get("/google/login")
def google_login():
    # use o env se existir; senão gera a partir da rota
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI") or url_for("auth.google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@bp.get("/google/callback")
def google_callback():
    # captura “state mismatch” e volta pro front com dica
    try:
        token = oauth.google.authorize_access_token()
    except MismatchingStateError:
        current_app.logger.warning(
            "OAuth state mismatch host=%s cookies=%s",
            request.host, request.headers.get("Cookie"),
        )
        front = os.getenv("FRONTEND_URL", "http://localhost:5173")
        return redirect(f"{front}/login?oauth=state_mismatch")

    # userinfo (OIDC)
    resp = oauth.google.get("userinfo")
    info = resp.json() if hasattr(resp, "json") else (token.get("userinfo") or {})

    email = (info.get("email") or "").strip().lower()
    nome  = info.get("name") or (email.split("@")[0] if email else None)
    if not email:
        return jsonify({"error": "google_login_failed"}), 400

    # upsert
    user = Usuario.query.filter_by(email=email).first()
    was_created = False
    if not user:
        # sua coluna password_hash é NOT NULL -> gere senha aleatória
        random_password = token_urlsafe(24)
        user = Usuario(email=email, nome=nome or email, is_admin=False)
        if hasattr(user, "set_password"):
            user.set_password(random_password)
        elif generate_password_hash:
            user.password_hash = generate_password_hash(random_password)
        else:
            user.password_hash = random_password  # fallback extremo
        db.session.add(user)
        db.session.commit()
        was_created = True

    login_user(user)

    # se acabou de criar via Google, obrigue a definir senha agora
    front = os.getenv("FRONTEND_URL", "http://localhost:5173")
    if was_created:
        session["must_set_password"] = True
        return redirect(f"{front}/criar-senha")

    return redirect(front)

# ---------- Definir / trocar senha ----------
@bp.post("/set-password")
@login_required
def set_password():
    data = request.get_json(silent=True) or {}
    new_pw     = (data.get("password") or "").strip()
    confirm    = (data.get("confirm") or "").strip()
    current_pw = (data.get("current_password") or "").strip()

    if not new_pw or len(new_pw) < 8:
        return jsonify({"error": "password_too_short", "min": 8}), 400
    if confirm and confirm != new_pw:
        return jsonify({"error": "password_mismatch"}), 400

    # se veio do Google agora, não exige senha atual
    must_set = session.pop("must_set_password", False)
    if not must_set and hasattr(current_user, "check_password"):
        if not current_pw or not current_user.check_password(current_pw):
            return jsonify({"error": "invalid_current_password"}), 400

    if hasattr(current_user, "set_password"):
        current_user.set_password(new_pw)
    elif generate_password_hash:
        current_user.password_hash = generate_password_hash(new_pw)
    else:
        current_user.password_hash = new_pw  # fallback extremo

    db.session.commit()
    return jsonify({"message": "password_set"})
