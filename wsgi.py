from app import create_app
import os
import click
from app.extensions import db
from app.models import (
    Usuario,
    QuestaoENEM,
    QuestaoAlternativa,
    Materia,
    Simulado,
    SimuladoQuestao,
    Resposta,
    ResultadoSimulado,
)
import pandas as pd
from pathlib import Path
from datetime import datetime

app = create_app()

# ========== CONFIG EXTRA ==========
app.config.update(
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=False,
    SESSION_COOKIE_DOMAIN=None,
    SESSION_COOKIE_NAME="session",
    SESSION_TYPE="filesystem",
    SESSION_PERMANENT=True,
    PERMANENT_SESSION_LIFETIME=7200,
    SECRET_KEY=os.environ.get(
        "SECRET_KEY", "dev-secret-change-in-production-" + os.urandom(24).hex()
    ),
    SESSION_COOKIE_PATH="/",
    GOOGLE_CLIENT_ID=os.environ.get("GOOGLE_CLIENT_ID", "your-client-id"),
    GOOGLE_CLIENT_SECRET=os.environ.get("GOOGLE_CLIENT_SECRET", "your-client-secret"),
    GOOGLE_REDIRECT_URI=os.environ.get("GOOGLE_REDIRECT_URI", "your-redirect-uri"),
    FRONTEND_URL=os.environ.get("FRONTEND_URL", "http://localhost:5173"),
    BACKEND_URL=os.environ.get("BACKEND_URL", "http://localhost:8000"),
)

# ==============================================================
# 🧱 COMANDOS CLI
# ==============================================================

@app.cli.command("db-init")
def db_init():
    """Cria todas as tabelas necessárias para o sistema."""
    with app.app_context():
        db.create_all()
        click.secho("✅ Todas as tabelas foram criadas com sucesso.", fg="green")


@app.cli.command("db-reset")
def db_reset():
    """Apaga e recria todas as tabelas (⚠️ use com cautela)."""
    with app.app_context():
        db.drop_all()
        db.create_all()
        click.secho("⚠️ Banco de dados resetado e recriado com sucesso.", fg="yellow")


@app.cli.command("create-admin")
def create_admin():
    """Cria o usuário administrador padrão."""
    with app.app_context():
        if Usuario.query.filter_by(email="admin@email.com").first():
            click.secho("⚠️ Usuário admin já existe.", fg="yellow")
            return

        admin_user = Usuario(
            nome_usuario="Admin",
            email="admin@email.com",
            is_admin=True,
        )
        admin_user.set_password("123456")

        db.session.add(admin_user)
        db.session.commit()

        click.secho("✅ Usuário admin criado com sucesso!", fg="green")
        click.secho("📧 Email: admin@email.com", fg="cyan")
        click.secho("🔑 Senha: 123456", fg="cyan")


# ==============================================================
# 📥 IMPORTAÇÃO DE DADOS
# ==============================================================

@app.cli.command("import-dados")
@click.option("--materias", default="data/materias.csv", show_default=True)
@click.option("--simulados", default="data/simulados.csv", show_default=True)
@click.option("--questoes", default="data/enem_questoes.csv", show_default=True)
@click.option("--encoding", default="utf-8", show_default=True)
@click.option("--truncate/--no-truncate", default=True, show_default=True)
def import_dados(materias, simulados, questoes, encoding, truncate):
    """
    Importa os dados base do sistema:
      • Matérias
      • Simulados
      • Questões + Alternativas
    """

    def safe_read_csv(path):
        """Lê CSV com fallback de encoding e erro amigável."""
        p = Path(path)
        if not p.exists():
            click.secho(f"⚠️  Arquivo não encontrado: {p}", fg="red")
            return None
        try:
            return pd.read_csv(p, encoding=encoding)
        except Exception as e:
            click.secho(f"❌ Erro ao ler {p}: {e}", fg="red")
            return None

    with app.app_context():
        if truncate:
            click.secho("🧹 Limpando tabelas...", fg="yellow")
            db.session.query(QuestaoAlternativa).delete()
            db.session.query(QuestaoENEM).delete()
            db.session.query(SimuladoQuestao).delete()
            db.session.query(ResultadoSimulado).delete()
            db.session.query(Simulado).delete()
            db.session.query(Materia).delete()
            db.session.commit()

        # -------------------------
        # MATERIAS
        # -------------------------
        df_materias = safe_read_csv(materias)
        total_materias = 0
        if df_materias is not None and "nome_materia" in df_materias.columns:
            for nome in df_materias["nome_materia"].dropna().unique():
                m = Materia(nome_materia=str(nome).strip())
                db.session.add(m)
                total_materias += 1
            db.session.commit()
            click.secho(f"✅ {total_materias} matérias importadas.", fg="green")
        else:
            click.secho("⚠️ Nenhum dado de matérias encontrado.", fg="yellow")

        # -------------------------
        # SIMULADOS
        # -------------------------
        df_simulados = safe_read_csv(simulados)
        total_simulados = 0

        if df_simulados is not None:
            # 🔧 Corrige nomes de colunas com espaços ou maiúsculas
            df_simulados.columns = [c.strip().lower() for c in df_simulados.columns]

            if "titulo" in df_simulados.columns:
                click.secho(f"🧩 Colunas CSV normalizadas: {list(df_simulados.columns)}", fg="cyan")

                for _, s in df_simulados.iterrows():
                    cod_materia_value = None

                    # 🔧 Busca segura, mesmo que a coluna não exista
                    cod_materia_raw = s.get("cod_materia")

                    if pd.notna(cod_materia_raw):
                        try:
                            cod_materia_value = int(cod_materia_raw)
                        except Exception as e:
                            click.secho(f"⚠️ Erro ao converter cod_materia='{cod_materia_raw}': {e}", fg="red")

                    click.secho(
                        f"📘 Criando simulado '{s['titulo']}' com cod_materia={cod_materia_value}",
                        fg="green"
                    )

                    sim = Simulado(
                        titulo=str(s["titulo"]).strip(),
                        descricao=str(s.get("descricao", "")).strip(),
                        dt_criacao=datetime.fromisoformat(str(s["dt_criacao"]))
                        if pd.notna(s.get("dt_criacao"))
                        else datetime.utcnow(),
                        ativo=str(s.get("ativo", True)).strip().lower() in ("true", "1", "t", "yes"),
                        cod_materia=cod_materia_value,
                    )

                    db.session.add(sim)
                    total_simulados += 1

                db.session.commit()
                click.secho(f"✅ {total_simulados} simulados importados (com cod_materia).", fg="green")
            else:
                click.secho("⚠️ Nenhum dado de simulados encontrado.", fg="yellow")

        # -------------------------
        # QUESTÕES
        # -------------------------
        df_questoes = safe_read_csv(questoes)
        total_questoes = 0
        total_alternativas = 0

        if df_questoes is not None:
            df_questoes.columns = [c.strip().lower() for c in df_questoes.columns]
            required = {
                "ano",
                "cod_materia",
                "pergunta",
                "opcao_a",
                "opcao_b",
                "opcao_c",
                "opcao_d",
                "opcao_e",
                "resposta_correta",
            }
            missing = required - set(df_questoes.columns)
            if missing:
                click.secho(
                    f"❌ CSV de questões faltando colunas: {', '.join(sorted(missing))}",
                    fg="red",
                )
            else:
                for r in df_questoes.to_dict("records"):
                    q = QuestaoENEM(
                        tx_questao=str(r["pergunta"]).strip(),
                        ano_questao=int(r["ano"]),
                        cod_materia=int(r["cod_materia"]),
                        tx_resposta_correta=str(r["resposta_correta"]).upper().strip(),
                    )
                    db.session.add(q)
                    db.session.flush()

                    alternativas = [
                        QuestaoAlternativa(cod_questao=q.cod_questao, tx_letra="A", tx_texto=str(r["opcao_a"]).strip()),
                        QuestaoAlternativa(cod_questao=q.cod_questao, tx_letra="B", tx_texto=str(r["opcao_b"]).strip()),
                        QuestaoAlternativa(cod_questao=q.cod_questao, tx_letra="C", tx_texto=str(r["opcao_c"]).strip()),
                        QuestaoAlternativa(cod_questao=q.cod_questao, tx_letra="D", tx_texto=str(r["opcao_d"]).strip()),
                        QuestaoAlternativa(cod_questao=q.cod_questao, tx_letra="E", tx_texto=str(r["opcao_e"]).strip()),
                    ]
                    db.session.add_all(alternativas)
                    total_questoes += 1
                    total_alternativas += 5

                db.session.commit()
                click.secho(f"✅ {total_questoes} questões e {total_alternativas} alternativas importadas.", fg="green")

        click.secho("🎉 Importação concluída com sucesso!", fg="cyan")

# ==============================================================
# ℹ️ LOG DE CONFIGURAÇÃO
# ==============================================================

print("=== CONFIGURAÇÕES CARREGADAS ===")
print(f"GOOGLE_CLIENT_ID: {'✅ Configurado' if app.config.get('GOOGLE_CLIENT_ID') else '❌ Não configurado'}")
print(f"GOOGLE_CLIENT_SECRET: {'✅ Configurado' if app.config.get('GOOGLE_CLIENT_SECRET') else '❌ Não configurado'}")
print(f"SECRET_KEY: {'✅ Configurado' if app.config.get('SECRET_KEY') else '❌ Não configurado'}")
print(f"FRONTEND_URL: {app.config.get('FRONTEND_URL')}")
print("================================")

# ==============================================================
# MAIN
# ==============================================================

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
