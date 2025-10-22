from flask import Flask
import os


def create_app():
    print("🚀 Iniciando create_app...")
    app = Flask(__name__)

    # ========== CONFIGURAÇÕES BÁSICAS ==========
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///vestibulando.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Configurações OAuth
    app.config["GOOGLE_CLIENT_ID"] = os.environ.get("GOOGLE_CLIENT_ID")
    app.config["GOOGLE_CLIENT_SECRET"] = os.environ.get("GOOGLE_CLIENT_SECRET")

    # URLs
    app.config["FRONTEND_URL"] = os.environ.get("FRONTEND_URL", "http://localhost:5173")
    app.config["BACKEND_URL"] = os.environ.get("BACKEND_URL", "http://localhost:8000")
    app.config["CHAT_API_URL"] = os.environ.get("CHAT_API_URL")
    app.config["CHAT_API_KEY"] = os.environ.get("CHAT_API_KEY")
    app.config["CHAT_API_TIMEOUT"] = os.environ.get("CHAT_API_TIMEOUT", "15")

    print("✅ Configurações carregadas")

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

        client_id = app.config.get("GOOGLE_CLIENT_ID")
        client_secret = app.config.get("GOOGLE_CLIENT_SECRET")

        if not client_id or not client_secret:
            print("❌ Credenciais do Google não configuradas")
        else:
            print(f"✅ Google Client ID: {client_id[:10]}...")

        oauth.register(
            name="google",
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
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

        # Auth
        from app.routes.auth import bp as auth_bp
        app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
        print("✅ Blueprint auth registrado com prefixo /api/v1/auth")

        # Chat
        from app.routes.chat import bp as chat_bp
        app.register_blueprint(chat_bp, url_prefix="/api/v1/chat")
        print("✅ Blueprint chat registrado com prefixo /api/v1/chat")
        
        # Usuario
        try:
            from app.routes.usuario import bp as usuario_bp
            app.register_blueprint(usuario_bp)
            print("✅ Blueprint usuario registrado com prefixo /api/v1/usuario")
        except Exception as e:
            print(f"⚠️  Não foi possível registrar blueprint 'usuario': {e}")

        # Questões
        try:
            from app.routes.questao import questao_bp
            app.register_blueprint(questao_bp)
            print("✅ Blueprint questao registrado com prefixo /api/v1/questoes")
        except Exception as e:
            print(f"⚠️  Não foi possível registrar blueprint 'questao': {e}")

        # Respostas
        try:
            from app.routes.resposta import resposta_bp
            app.register_blueprint(resposta_bp)
            print("✅ Blueprint resposta registrado com prefixo /api/v1/respostas")
        except Exception as e:
            print(f"⚠️  Não foi possível registrar blueprint 'resposta': {e}")

        # Matérias
        try:
            from app.routes.materia import materia_bp
            app.register_blueprint(materia_bp)
            print("✅ Blueprint materia registrado com prefixo /api/v1/materias")
        except Exception as e:
            print(f"⚠️  Não foi possível registrar blueprint 'materia': {e}")

        # Simulados (Simulado + Questões + Resultados)
        try:
            from app.routes.simulado import simulado_bp
            app.register_blueprint(simulado_bp)
            print("✅ Blueprint simulado registrado com prefixo /api/v1/simulados")
        except Exception as e:
            print(f"⚠️  Não foi possível registrar blueprint 'simulado': {e}")

    except Exception as e:
        print(f"❌ Erro ao registrar blueprints: {e}")
        import traceback
        traceback.print_exc()

    # ========== ROTAS BÁSICAS ==========
    @app.route("/")
    def index():
        return {
            "message": "VestibulandoBot API funcionando!",
            "version": "2.0",
            "status": "ok",
        }

    @app.route("/health")
    def health():
        return {"status": "healthy"}

    # ========== DEBUG: LISTAR ROTAS ==========
    print("=== ROTAS REGISTRADAS ===")
    for rule in app.url_map.iter_rules():
        methods = ", ".join(rule.methods - {"HEAD", "OPTIONS"})
        print(f"{methods:10} {rule.rule:40} -> {rule.endpoint}")
    print("========================")

    print("🎉 create_app finalizado!")
    return app
