# app/routes/auth.py
from flask import Blueprint, request, jsonify, redirect, url_for, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, oauth
from app.models.usuario import Usuario
import os, secrets

bp = Blueprint("auth", __name__)

# ---------- Helpers ----------
NAME_FIELDS = ("nome", "name", "full_name", "username")
PASS_FIELDS = ("senha_hash", "password_hash", "senha", "password")
GOOGLE_SUB_FIELDS = ("google_sub", "google_id", "sub")

def set_first_attr_if_exists(obj, names, value):
    for n in names:
        if hasattr(obj, n):
            setattr(obj, n, value)
            return n
    return None

def get_first_attr(obj, names):
    for n in names:
        if hasattr(obj, n):
            return n, getattr(obj, n)
    return None, None

def set_password_hash(user, senha_em_texto: str):
    hashed = generate_password_hash(senha_em_texto)
    used = set_first_attr_if_exists(user, PASS_FIELDS, hashed)
    if not used:
        raise RuntimeError(
            "Seu model Usuario não tem nenhuma coluna de senha "
            "(esperado uma entre: senha_hash, password_hash, senha, password)."
        )
    return used

def check_user_password(user, senha_em_texto: str) -> bool:
    _, stored = get_first_attr(user, PASS_FIELDS)
    if not stored:
        return False
    try:
        return check_password_hash(stored, senha_em_texto)
    except Exception:
        return False

def has_password(user) -> bool:
    _, stored = get_first_attr(user, PASS_FIELDS)
    if not stored:
        return False
    # trata placeholder "__GOOGLE_PLACEHOLDER__" como "sem senha"
    try:
        from werkzeug.security import check_password_hash as _chk
        if _chk(stored, "__GOOGLE_PLACEHOLDER__"):
            return False
    except Exception:
        pass
    return True

def has_google_link(user) -> bool:
    return any(getattr(user, f, None) for f in GOOGLE_SUB_FIELDS)

# ---------- Cadastro (e-mail/senha) ----------
@bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    senha = data.get("senha") or ""
    nome  = (data.get("nome")  or "").strip()

    if not email or not senha:
        return jsonify({"error": "Informe email e senha."}), 400

    if Usuario.query.filter_by(email=email).first():
        return jsonify({"error": "E-mail já cadastrado."}), 409

    user = Usuario(email=email)
    # agora que existe a coluna, setamos diretamente
    if hasattr(user, "nome"):
        user.nome = nome

    try:
        set_password_hash(user, senha)
    except RuntimeError as err:
        return jsonify({"error": str(err)}), 500

    db.session.add(user)
    db.session.commit()
    return jsonify({"ok": True, "id": user.id, "email": user.email}), 201

# ---------- Login (e-mail/senha) ----------
@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    senha = data.get("senha") or ""

    user = Usuario.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Credenciais inválidas."}), 401

    if not check_user_password(user, senha):
        if has_google_link(user) and not has_password(user):
            return jsonify({
                "error": "Conta criada com Google. Entre com o Google ou crie uma senha nas configurações.",
                "code": "USE_GOOGLE_OR_SET_PASSWORD"
            }), 403
        return jsonify({"error": "Credenciais inválidas."}), 401

    login_user(user)  # seta cookie de sessão
    return jsonify({"ok": True, "id": user.id, "email": user.email})

# ---------- Logout ----------
@bp.post("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"ok": True})

# ---------- Quem sou eu ----------
@bp.get("/me")
def me():
    if not current_user.is_authenticated:
        return jsonify({"error": "Não autenticado."}), 401
    _, nome_val = get_first_attr(current_user, NAME_FIELDS)
    return jsonify({
        "id": current_user.id,
        "email": current_user.email,
        "nome": (nome_val or ""),
        "google": has_google_link(current_user),
        "has_password": has_password(current_user),
    })

# ---------- Definir senha (após login com Google) ----------
@bp.post("/password/set")
@login_required
def password_set():
    data = request.get_json(silent=True) or {}
    senha = (data.get("senha") or "").strip()
    confirma = (data.get("confirmacao") or "").strip()

    if len(senha) < 6:
        return jsonify({"error": "A senha deve ter pelo menos 6 caracteres."}), 400
    if senha != confirma:
        return jsonify({"error": "As senhas não conferem."}), 400

    try:
        set_password_hash(current_user, senha)
    except RuntimeError as err:
        return jsonify({"error": str(err)}), 500

    db.session.commit()
    return jsonify({"ok": True})

# ---------- Google OAuth ----------
@bp.get("/google/login")
def google_login():
    # nonce para OIDC (usado em parse_id_token)
    nonce = secrets.token_urlsafe(16)
    session["google_oauth_nonce"] = nonce

    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI") or url_for("auth.google_callback", _external=True)
    current_app.logger.info("Google OAuth redirect_uri usado: %s", redirect_uri)

    return oauth.google.authorize_redirect(
        redirect_uri,
        prompt="select_account",
        nonce=nonce,
    )

@bp.get("/google/callback")
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
    except Exception as e:
        current_app.logger.exception("authorize_access_token falhou")
        return jsonify({"error": "Falha ao autorizar com o Google", "detail": str(e)}), 400

    # 1) tenta claims do ID Token com nonce
    claims = None
    try:
        nonce = session.pop("google_oauth_nonce", None)
        claims = oauth.google.parse_id_token(token, nonce=nonce)
    except Exception as e:
        current_app.logger.warning("parse_id_token falhou: %s", e)

    # 2) fallback: /userinfo
    if not claims or not claims.get("email"):
        try:
            resp = oauth.google.get("userinfo")
            resp.raise_for_status()
            claims = resp.json()
        except Exception as e:
            current_app.logger.exception("Falha ao obter /userinfo: %s", e)
            claims = {}

    email = (claims.get("email") or "").strip().lower()
    name  = (claims.get("name") or claims.get("given_name") or "").strip()
    sub   = claims.get("sub") or claims.get("id")

    if not email:
        return jsonify({"error": "Não foi possível obter e-mail do Google."}), 400

    created_now = False
    user = Usuario.query.filter_by(email=email).first()
    if not user:
        user = Usuario(email=email)
        if hasattr(user, "nome"):
            user.nome = name  # salva nome vindo do Google
        # senha placeholder para satisfazer NOT NULL
        try:
            set_password_hash(user, "__GOOGLE_PLACEHOLDER__")
        except RuntimeError:
            pass
        set_first_attr_if_exists(user, GOOGLE_SUB_FIELDS, sub)
        db.session.add(user)
        db.session.commit()
        created_now = True
    else:
        # se o usuário já existe e ainda não tem nome, atualize
        if hasattr(user, "nome") and not (user.nome or "").strip() and name:
            user.nome = name
            db.session.commit()

    login_user(user)

    front = os.getenv("FRONTEND_URL", "http://127.0.0.1:5173")
    if created_now:
        return redirect(f"{front}/criar-senha?from=google")
    return redirect(f"{front}/?login=google_ok")
