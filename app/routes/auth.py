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

# ✅ ROTA DE TESTE - Remover depois
@bp.get("/test")
def test_route():
    return {"message": "Auth routes funcionando!", "host": request.host}

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
    # Limpa sessão anterior
    for key in list(session.keys()):
        if key.startswith('_google_') or key.startswith('oauth_'):
            session.pop(key, None)
    
    # URL de callback fixa
    redirect_uri = "http://localhost:8000/api/v1/auth/google/callback"
    
    current_app.logger.info(f"=== GOOGLE LOGIN INICIADO ===")
    current_app.logger.info(f"Host: {request.host}")
    current_app.logger.info(f"Redirect URI: {redirect_uri}")
    
    try:
        # Versão manual para debug - construir URL do Google manualmente
        client_id = current_app.config.get('GOOGLE_CLIENT_ID')
        if not client_id:
            current_app.logger.error("GOOGLE_CLIENT_ID não configurado")
            front = os.getenv("FRONTEND_URL", "http://localhost:5173")
            return redirect(f"{front}/login?oauth=missing_config")
        
        # Gerar state manualmente
        state = token_urlsafe(32)
        session['oauth_state'] = state
        
        # URL manual do Google OAuth
        google_auth_url = (
            f"https://accounts.google.com/o/oauth2/auth?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"scope=openid%20email%20profile&"
            f"response_type=code&"
            f"state={state}&"
            f"prompt=select_account"
        )
        
        current_app.logger.info(f"Redirecionando para: {google_auth_url}")
        return redirect(google_auth_url)
        
    except Exception as e:
        current_app.logger.error(f"Erro ao iniciar OAuth: {e}")
        front = os.getenv("FRONTEND_URL", "http://localhost:5173")
        return redirect(f"{front}/login?oauth=init_error")

@bp.get("/google/callback")
def google_callback():
    front = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    current_app.logger.info(f"=== GOOGLE CALLBACK RECEBIDO ===")
    current_app.logger.info(f"Args: {dict(request.args)}")
    
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    
    if error:
        current_app.logger.error(f"Erro do Google: {error}")
        return redirect(f"{front}/login?oauth=google_error")
    
    if not code:
        current_app.logger.error("Código de autorização não recebido")
        return redirect(f"{front}/login?oauth=no_code")
    
    # Verificar state
    session_state = session.get('oauth_state')
    if not state or state != session_state:
        current_app.logger.warning(f"State mismatch: recebido={state}, sessão={session_state}")
        # Em desenvolvimento, apenas avisa mas continua
        if current_app.debug:
            current_app.logger.info("Modo debug: continuando apesar do state mismatch")
        else:
            return redirect(f"{front}/login?oauth=state_mismatch")
    
    try:
        # Trocar código por token manualmente
        import requests
        
        token_data = {
            'client_id': current_app.config.get('GOOGLE_CLIENT_ID'),
            'client_secret': current_app.config.get('GOOGLE_CLIENT_SECRET'),
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': 'http://localhost:8000/api/v1/auth/google/callback'
        }
        
        current_app.logger.info("Trocando código por token...")
        token_response = requests.post(
            'https://oauth2.googleapis.com/token',
            data=token_data,
            timeout=10
        )
        
        if token_response.status_code != 200:
            current_app.logger.error(f"Erro ao obter token: {token_response.text}")
            return redirect(f"{front}/login?oauth=token_error")
        
        token = token_response.json()
        access_token = token.get('access_token')
        
        # Obter informações do usuário
        current_app.logger.info("Obtendo informações do usuário...")
        userinfo_response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        
        if userinfo_response.status_code != 200:
            current_app.logger.error(f"Erro ao obter userinfo: {userinfo_response.text}")
            return redirect(f"{front}/login?oauth=userinfo_error")
        
        info = userinfo_response.json()
        current_app.logger.info(f"Userinfo: {info}")
        
        return process_google_user(info, front)
        
    except Exception as e:
        current_app.logger.error(f"Erro no callback: {e}")
        import traceback
        traceback.print_exc()
        return redirect(f"{front}/login?oauth=callback_error")

def process_google_user(info, front_url):
    """Processa os dados do usuário do Google"""
    email = (info.get("email") or "").strip().lower()
    nome = info.get("name") or (email.split("@")[0] if email else None)
    
    current_app.logger.info(f"Processando usuário: {email}")
    
    if not email:
        current_app.logger.error("Email não encontrado")
        return redirect(f"{front_url}/login?oauth=no_email")

    # Verificar se usuário já existe
    user = Usuario.query.filter_by(email=email).first()
    was_created = False
    
    if not user:
        # Criar novo usuário
        current_app.logger.info(f"Criando novo usuário: {email}")
        random_password = token_urlsafe(24)
        user = Usuario(email=email, nome=nome or email, is_admin=False)
        
        if hasattr(user, "set_password"):
            user.set_password(random_password)
        elif generate_password_hash:
            user.password_hash = generate_password_hash(random_password)
        else:
            user.password_hash = random_password
            
        try:
            db.session.add(user)
            db.session.commit()
            was_created = True
            current_app.logger.info(f"Usuário criado: {email}")
        except Exception as e:
            current_app.logger.error(f"Erro ao criar usuário: {e}")
            db.session.rollback()
            return redirect(f"{front_url}/login?oauth=db_error")
    else:
        current_app.logger.info(f"Usuário existente: {email}")

    # Fazer login
    try:
        login_user(user, remember=True)
        current_app.logger.info(f"Login realizado: {email}")
    except Exception as e:
        current_app.logger.error(f"Erro no login: {e}")
        return redirect(f"{front_url}/login?oauth=login_error")
    
    # Limpar sessão OAuth
    for key in list(session.keys()):
        if key.startswith('_google_') or key.startswith('oauth_'):
            session.pop(key, None)

    # Redirecionar
    if was_created:
        session["must_set_password"] = True
        current_app.logger.info(f"Redirecionando para criar senha: {email}")
        return redirect(f"{front_url}/criar-senha")
    else:
        current_app.logger.info(f"Redirecionando para dashboard: {email}")
        return redirect(f"{front_url}/dashboard")

# ---------- Definir / trocar senha ----------
@bp.post("/set-password")
@login_required
def set_password():
    data = request.get_json(silent=True) or {}
    new_pw = (data.get("password") or "").strip()
    confirm = (data.get("confirm") or "").strip()
    current_pw = (data.get("current_password") or "").strip()

    current_app.logger.info(f"Definindo senha para: {current_user.email}")

    if not new_pw or len(new_pw) < 8:
        return jsonify({"error": "password_too_short", "min": 8}), 400
    if confirm and confirm != new_pw:
        return jsonify({"error": "password_mismatch"}), 400

    # Se veio do Google, não exige senha atual
    must_set = session.pop("must_set_password", False)
    current_app.logger.info(f"Must set password: {must_set}")
    
    if not must_set and hasattr(current_user, "check_password"):
        if not current_pw or not current_user.check_password(current_pw):
            return jsonify({"error": "invalid_current_password"}), 400

    try:
        if hasattr(current_user, "set_password"):
            current_user.set_password(new_pw)
        elif generate_password_hash:
            current_user.password_hash = generate_password_hash(new_pw)
        else:
            current_user.password_hash = new_pw

        db.session.commit()
        current_app.logger.info(f"Senha definida para: {current_user.email}")
        return jsonify({"message": "password_set", "redirect": "/dashboard"})
        
    except Exception as e:
        current_app.logger.error(f"Erro ao definir senha: {e}")
        db.session.rollback()
        return jsonify({"error": "database_error"}), 500

# Alias para compatibilidade com o frontend
@bp.post("/password/set")
@login_required  
def set_password_alias():
    """Alias para /set-password para compatibilidade com frontend"""
    return set_password()