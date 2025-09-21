# wsgi.py
from app import create_app
import os

app = create_app()

# Configurações para desenvolvimento - OAuth e sessões
app.config.update(
    # Cookies de sessão - configurações mais permissivas para desenvolvimento
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=False,  # False para debug
    SESSION_COOKIE_DOMAIN=None,
    SESSION_COOKIE_NAME='session',
    
    # OAuth específico - configurações mais robustas
    SESSION_TYPE='filesystem',  # ou 'redis' se tiver Redis
    SESSION_PERMANENT=True,     # Sessões persistem
    PERMANENT_SESSION_LIFETIME=7200,  # 2 horas
    
    # Configurações adicionais para OAuth
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-change-in-production-' + os.urandom(24).hex()),
    
    # Configurações específicas para desenvolvimento
    SESSION_COOKIE_PATH='/',
    
    # Configurações OAuth específicas
    GOOGLE_CLIENT_ID=os.environ.get('GOOGLE_CLIENT_ID'),
    GOOGLE_CLIENT_SECRET=os.environ.get('GOOGLE_CLIENT_SECRET'),
    
    # URLs
    FRONTEND_URL=os.environ.get('FRONTEND_URL', 'http://localhost:5173'),
    BACKEND_URL=os.environ.get('BACKEND_URL', 'http://localhost:8000'),
)

# Log das configurações importantes
print("=== CONFIGURAÇÕES CARREGADAS ===")
print(f"GOOGLE_CLIENT_ID: {'✅ Configurado' if app.config.get('GOOGLE_CLIENT_ID') else '❌ Não configurado'}")
print(f"GOOGLE_CLIENT_SECRET: {'✅ Configurado' if app.config.get('GOOGLE_CLIENT_SECRET') else '❌ Não configurado'}")
print(f"SECRET_KEY: {'✅ Configurado' if app.config.get('SECRET_KEY') else '❌ Não configurado'}")
print(f"FRONTEND_URL: {app.config.get('FRONTEND_URL')}")
print("================================")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)