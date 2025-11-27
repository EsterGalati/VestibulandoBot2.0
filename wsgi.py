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
    ResultadoSimulado,
)
import pandas as pd
from pathlib import Path
from datetime import datetime

app = create_app()

# Configura a chave do GeminiAI no app
app.config['GEMINI_API_KEY'] = os.environ.get('GEMINI_API_KEY')

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

# ==============================================================
# 📥 IMPORTAÇÃO DE DADOS
# ==============================================================

@app.cli.command("import-dados")
@click.option("--enem-anos", default="", help="Anos do ENEM a importar (ex: 2020,2021)") # <-- NOVA OPÇÃO
@click.option("--usuarios",   default="data/usuarios.csv",        show_default=True)
@click.option("--materias",   default="data/materias.csv",        show_default=True)
@click.option("--simulados",  default="data/simulados.csv",       show_default=True)
@click.option("--questoes",   default="data/enem_questoes.csv",   show_default=True)
@click.option("--simulados-questoes", default="data/simulados_questoes.csv", show_default=True,
              help="CSV de associação entre simulados e questões")
@click.option("--encoding",   default="utf-8",                    show_default=True)
@click.option("--truncate/--no-truncate", default=True,           show_default=True,
              help="Trunca questões/simulados/matérias")
@click.option("--truncate-usuarios/--no-truncate-usuarios", default=False, show_default=True,
              help="Opcional: trunca TB_USUARIO antes de importar")
def import_dados(usuarios, materias, simulados, questoes, simulados_questoes, encoding, truncate, truncate_usuarios, enem_anos):
    """
    Importa dados base do sistema:
      • Usuários (CSV)
      • Matérias
      • Simulados (com várias matérias)
      • Questões + Alternativas
      • Vínculos Professor-Aluno
      • Associação Simulado ↔ Questões
    """

    def safe_read_csv(path: str):
        """Lê CSV com tratamento de encoding e erros amigáveis."""
        p = Path(path)
        if not p.exists():
            click.secho(f"⚠️  Arquivo não encontrado: {p}", fg="red")
            return None
        try:
            return pd.read_csv(p, encoding=encoding, skipinitialspace=True)
        except Exception as e:
            click.secho(f"❌ Erro ao ler {p}: {e}", fg="red")
            return None

    with app.app_context():
        # =========================
        # USUÁRIOS
        # =========================
        if truncate_usuarios:
            click.secho("🧹 Limpando usuários...", fg="yellow")
            db.session.query(Usuario).delete()
            db.session.commit()

        df_users = safe_read_csv(usuarios)
        if df_users is not None:
            df_users.columns = [c.strip().lower() for c in df_users.columns]
            required_users = {"nome_usuario", "email", "senha", "is_admin"}
            missing_u = required_users - set(df_users.columns)
            if missing_u:
                click.secho(f"❌ CSV de usuários faltando colunas: {', '.join(sorted(missing_u))}", fg="red")
            else:
                total_novos, total_existentes = 0, 0
                for r in df_users.to_dict("records"):
                    nome  = str(r["nome_usuario"]).strip()
                    email = str(r["email"]).strip().lower()
                    senha = str(r["senha"]).strip()
                    is_admin = str(r.get("is_admin", "False")).strip().lower() in ("true","1","t","yes")

                    if not email:
                        continue

                    if Usuario.get_by_email(email):
                        total_existentes += 1
                        continue

                    Usuario.create(
                        nome_usuario=nome,
                        email=email,
                        senha=senha,
                        is_admin=is_admin,
                        commit=False
                    )
                    total_novos += 1

                db.session.commit()
                click.secho(f"✅ Usuários importados: {total_novos} (ignorados: {total_existentes}).", fg="green")

        # =========================
        # TRUNCATE conteúdos
        # =========================
        if truncate:
            click.secho("🧹 Limpando tabelas de conteúdos...", fg="yellow")
            db.session.query(SimuladoQuestao).delete()
            db.session.query(QuestaoAlternativa).delete()
            db.session.query(QuestaoENEM).delete()
            db.session.query(Simulado).delete()
            db.session.query(Materia).delete()
            db.session.commit()

        # =========================
        # MATÉRIAS
        # =========================
        df_materias = safe_read_csv(materias)
        total_materias = 0
        if df_materias is not None and "nome_materia" in df_materias.columns:
            for nome in df_materias["nome_materia"].dropna().unique():
                m = Materia(nome_materia=str(nome).strip())
                db.session.add(m)
                total_materias += 1
            db.session.commit()
            click.secho(f"✅ {total_materias} matérias importadas.", fg="green")

        # =========================
        # SIMULADOS
        # =========================
        df_simulados = safe_read_csv(simulados)
        total_simulados = 0
        if df_simulados is not None:
            df_simulados.columns = [c.strip().lower() for c in df_simulados.columns]
            for _, s in df_simulados.iterrows():
                raw_dt = str(s.get("dt_criacao", "")).strip()
                ts = pd.to_datetime(raw_dt, errors="coerce", utc=True)
                dt = datetime.utcnow() if pd.isna(ts) else ts.to_pydatetime().replace(tzinfo=None)
                materias_str = str(s.get("cod_materias", "")).strip()
                cods = [int(x) for x in materias_str.split(",") if x.strip().isdigit()]
                materias_objs = db.session.query(Materia).filter(Materia.cod_materia.in_(cods)).all()
                sim = Simulado(
                    titulo=str(s["titulo"]).strip(),
                    descricao=str(s.get("descricao", "")).strip(),
                    dt_criacao=dt,
                    ativo=str(s.get("ativo", True)).strip().lower() in ("true", "1", "t", "yes"),
                    materias=materias_objs,
                )
                db.session.add(sim)
                db.session.flush()
                total_simulados += 1
            db.session.commit()
            click.secho(f"✅ {total_simulados} simulados importados.", fg="green")

        # =========================
        # QUESTÕES
        # =========================
        df_questoes = safe_read_csv(questoes)
        total_questoes = 0
        if df_questoes is not None:
            df_questoes.columns = [c.strip().lower() for c in df_questoes.columns]
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
            db.session.commit()
            click.secho(f"✅ {total_questoes} questões importadas.", fg="green")

        # =========================
        # SIMULADO ↔ QUESTÕES
        # =========================
        df_sq = safe_read_csv(simulados_questoes)
        total_links = 0
        if df_sq is not None:
            df_sq.columns = [c.strip().lower() for c in df_sq.columns]
            required = {"cod_simulado", "cod_questao"}
            if required.issubset(df_sq.columns):
                for i, r in enumerate(df_sq.to_dict("records")):
                    cod_simulado = int(r["cod_simulado"])
                    cod_questao = int(r["cod_questao"])
                    ordem = int(r.get("ordem", i+1))
                    db.session.add(SimuladoQuestao(
                        cod_simulado=cod_simulado,
                        cod_questao=cod_questao,
                        ordem=ordem
                    ))
                    total_links += 1
                db.session.commit()
                click.secho(f"✅ {total_links} associações Simulado ↔ Questão importadas.", fg="green")
            else:
                click.secho("⚠️ CSV de simulados_questoes faltando colunas necessárias.", fg="yellow")

        click.secho("🎉 Importação concluída com sucesso!", fg="cyan")
        
        # =========================
        # QUESTÕES ENEM (API)
        # =========================
        if enem_anos:
            from app.services.questao_service import QuestaoService
            
            anos = [int(a.strip()) for a in enem_anos.split(",") if a.strip().isdigit()]
            
            if anos:
                click.secho(f"📥 Iniciando importação de questões do ENEM para os anos: {', '.join(map(str, anos))}", fg="blue")
                for ano in anos:
                    click.secho(f"   → Importando ENEM {ano}...", fg="blue")
                    try:
                        resultado = QuestaoService.importar_enem(ano)
                        if resultado["status"] == "sucesso":
                            click.secho(f"   ✅ ENEM {ano}: {resultado['mensagem']}", fg="green")
                        else:
                            click.secho(f"   ❌ ENEM {ano}: {resultado['mensagem']}", fg="red")
                            for erro in resultado.get("erros", []):
                                click.secho(f"      - {erro}", fg="red")
                    except Exception as e:
                        click.secho(f"   ❌ Erro fatal ao importar ENEM {ano}: {e}", fg="red")
            else:
                click.secho("⚠️ Nenhum ano válido fornecido para a importação do ENEM.", fg="yellow")

        click.secho("🎉 Importação concluída com sucesso!", fg="cyan")

# ==============================================================
# ℹ️ LOG DE CONFIGURAÇÃO
# ==============================================================

print("=== CONFIGURAÇÕES CARREGADAS ===")
print(f"GOOGLE_CLIENT_ID: {'✅ Configurado' if app.config.get('GOOGLE_CLIENT_ID') else '❌ Não configurado'}")
print(f"GOOGLE_CLIENT_SECRET: {'✅ Configurado' if app.config.get('GOOGLE_CLIENT_SECRET') else '❌ Não configurado'}")
print(f"SECRET_KEY: {'✅ Configurado' if app.config.get('SECRET_KEY') else '❌ Não configurado'}")
print(f"GEMINI_API_KEY: {'✅ Configurado' if app.config.get('GEMINI_API_KEY') else '❌ Não configurado'}")
print(f"FRONTEND_URL: {app.config.get('FRONTEND_URL')}")
print("================================")

# ==============================================================
# MAIN
# ==============================================================

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
