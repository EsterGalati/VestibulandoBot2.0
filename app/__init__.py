# app/__init__.py
from flask import Flask
import os

def create_app():
    print("🚀 Iniciando create_app...")
    app = Flask(__name__)
    
    # ========== CONFIGURAÇÕES BÁSICAS ==========
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///vestibulando.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configurações OAuth
    app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID')
    app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # URLs
    app.config['FRONTEND_URL'] = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
    app.config['BACKEND_URL'] = os.environ.get('BACKEND_URL', 'http://localhost:8000')
    
    print(f"✅ Configurações carregadas")
    
    # ========== INICIALIZAÇÃO DAS EXTENSÕES ==========
    try:
        from app.extensions import init_app
        init_app(app)
        print("✅ Extensões inicializadas")
    except Exception as e:
        print(f"❌ Erro ao inicializar extensões: {e}")
        import traceback
        traceback.print_exc()
    
    # ========== CONFIGURAÇÃO DO OAUTH GOOGLE ==========
    try:
        from app.extensions import oauth
        
        # Verificar se as credenciais estão disponíveis
        client_id = app.config.get('GOOGLE_CLIENT_ID')
        client_secret = app.config.get('GOOGLE_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            print("❌ Credenciais do Google não configuradas")
        else:
            print(f"✅ Google Client ID: {client_id[:10]}...")
            
        google = oauth.register(
            name='google',
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={
                'scope': 'openid email profile'
            }
        )
        print("✅ OAuth Google configurado")
    except Exception as e:
        print(f"❌ Erro ao configurar OAuth: {e}")
        import traceback
        traceback.print_exc()
    
    # ========== CONFIGURAÇÃO DO LOGIN MANAGER ==========
    try:
        from app.extensions import login_manager
        
        @login_manager.user_loader
        def load_user(user_id):
            from app.models.usuario import Usuario
            return Usuario.query.get(int(user_id))
        print("✅ Login Manager configurado")
    except Exception as e:
        print(f"❌ Erro ao configurar Login Manager: {e}")
    
    # ========== REGISTRO DOS BLUEPRINTS ==========
    try:
        print("📝 Registrando blueprints...")
        from app.routes.auth import bp as auth_bp
        app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
        print("✅ Blueprint auth registrado com prefixo /api/v1/auth")
        
        # Se tiver outros blueprints, adicione aqui
        
    except Exception as e:
        print(f"❌ Erro ao registrar blueprints: {e}")
        import traceback
        traceback.print_exc()
    
    # ========== ROTA BÁSICA ==========
    @app.route('/')
    def index():
        return {
            'message': 'VestibulandoBot API funcionando!',
            'version': '2.0',
            'status': 'ok'
        }
    
    @app.route('/health')
    def health():
        return {'status': 'healthy'}
    
    # ========== DEBUG: LISTAR ROTAS ==========
    print("=== ROTAS REGISTRADAS ===")
    for rule in app.url_map.iter_rules():
        methods = ', '.join(rule.methods - {'HEAD', 'OPTIONS'})
        print(f"{methods:10} {rule.rule:30} -> {rule.endpoint}")
    print("========================")
    
    print("🎉 create_app finalizado!")
    return app