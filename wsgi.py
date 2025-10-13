from app import create_app
import os
import click  # Certifique-se de importar 'click'
from app.extensions import db
from app.models import QuestaoENEM  # Certifique-se de importar o modelo QuestaoENEM
import pandas as pd
from pathlib import Path

app = create_app()

# Configura a chave do GeminiAI no app
app.config['GEMINI_API_KEY'] = os.environ.get('GEMINI_API_KEY')

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
    GOOGLE_CLIENT_ID=os.environ.get('GOOGLE_CLIENT_ID', 'your-client-id'),
    GOOGLE_CLIENT_SECRET=os.environ.get('GOOGLE_CLIENT_SECRET', 'your-client-secret'),
    GOOGLE_REDIRECT_URI=os.environ.get('GOOGLE_REDIRECT_URI', 'your-redirect-uri'),  # Se necessário
    
    # URLs
    FRONTEND_URL=os.environ.get('FRONTEND_URL', 'http://localhost:5173'),
    BACKEND_URL=os.environ.get('BACKEND_URL', 'http://localhost:8000'),
)

@app.cli.command("db-init")
def db_init():
    """Cria as tabelas no banco (não apaga as existentes)."""
    with app.app_context():
        db.create_all()
        click.secho("✓ Tabelas criadas (ou já existentes).", fg="green")


@app.cli.command("import-questoes")
@click.option(
    "--csv",
    "csv_path",
    default="data/enem_questoes.csv",
    show_default=True,
    help="Caminho do CSV de questões do ENEM",
)
@click.option(
    "--encoding",
    default="utf-8",
    show_default=True,
    help="Encoding do arquivo (ex.: utf-8, utf-8-sig, latin1)",
)
@click.option(
    "--truncate/--no-truncate",
    default=True,
    show_default=True,
    help="Apaga as questões existentes antes de importar",
)
@click.option(
    "--chunk-size",
    type=int,
    default=2000,
    show_default=True,
    help="Tamanho do lote para insert em massa (0 = tudo de uma vez)",
)
def import_questoes(csv_path, encoding, truncate, chunk_size):
    """Importa questões do ENEM a partir de um CSV."""
    path = Path(csv_path)
    if not path.exists():
        raise click.ClickException(f"CSV não encontrado: {path}")

    with app.app_context():
        try:
            df = pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError as e:
            raise click.ClickException(
                f"Erro de encoding ao ler {path}. "
                f"Tente --encoding utf-8-sig ou latin1. Detalhe: {e}"
            )

        df.columns = [c.strip().lower() for c in df.columns]
        required = {
            "ano",
            "pergunta",
            "opcao_a",
            "opcao_b",
            "opcao_c",
            "opcao_d",
            "opcao_e",
            "resposta_correta",
        }
        missing = required - set(df.columns)
        if missing:
            raise click.ClickException(
                f"CSV inválido. Faltando colunas: {', '.join(sorted(missing))}"
            )

        if truncate:
            db.session.query(QuestaoENEM).delete()
            db.session.commit()
            click.secho("• Tabela questoes_enem limpa.", fg="yellow")

        objs = [
            QuestaoENEM(
                ano=int(r["ano"]),
                pergunta=str(r["pergunta"]),
                opcao_a=str(r["opcao_a"]),
                opcao_b=str(r["opcao_b"]),
                opcao_c=str(r["opcao_c"]),
                opcao_d=str(r["opcao_d"]),
                opcao_e=str(r["opcao_e"]),
                resposta_correta=str(r["resposta_correta"]).upper().strip(),
            )
            for _, r in df.iterrows()
        ]

        if chunk_size and chunk_size > 0:
            total = 0
            for start in range(0, len(objs), chunk_size):
                batch = objs[start : start + chunk_size]
                db.session.bulk_save_objects(batch)
                db.session.commit()
                total += len(batch)
                click.secho(f"  • Inseridas {len(batch)} (acumulado {total})", fg="blue")
        else:
            db.session.bulk_save_objects(objs)
            db.session.commit()
            click.secho(f"✓ Importadas {len(objs)} questões de {path}", fg="green")

# Log das configurações importantes
print("=== CONFIGURAÇÕES CARREGADAS ===")
print(f"GOOGLE_CLIENT_ID: {'✅ Configurado' if app.config.get('GOOGLE_CLIENT_ID') else '❌ Não configurado'}")
print(f"GOOGLE_CLIENT_SECRET: {'✅ Configurado' if app.config.get('GOOGLE_CLIENT_SECRET') else '❌ Não configurado'}")
print(f"SECRET_KEY: {'✅ Configurado' if app.config.get('SECRET_KEY') else '❌ Não configurado'}")
print(f"GEMINI_API_KEY: {'✅ Configurado' if app.config.get('GEMINI_API_KEY') else '❌ Não configurado'}")
print(f"FRONTEND_URL: {app.config.get('FRONTEND_URL')}")
print("================================")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)