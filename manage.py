# manage.py
from __future__ import annotations

import click
from pathlib import Path
import pandas as pd
from sqlalchemy import inspect, text

from app import create_app
from app.extensions import db
from app.models import QuestaoENEM, Usuario

# cria app para registrar CLI
app = create_app()


@app.cli.command("db-init")
def db_init():
    """Cria as tabelas no banco (não apaga as existentes)."""
    with app.app_context():
        db.create_all()
        click.secho("✓ Tabelas criadas (ou já existentes).", fg="green")


@app.cli.command("db-reset")
def db_reset():
    """DROPA tudo e recria as tabelas conforme os models atuais."""
    with app.app_context():
        click.secho("Dropping all...", fg="yellow")
        db.drop_all()
        try:
            db.session.execute(text("PRAGMA foreign_keys=ON"))  # SQLite: garante FKs
        except Exception:
            pass
        click.secho("Creating all...", fg="yellow")
        db.create_all()
        db.session.commit()
        click.secho("✓ Banco recriado com schema atual.", fg="green")


@app.cli.command("db-check")
def db_check():
    """Mostra diagnóstico do schema: tabelas, colunas, PKs, FKs, índices."""
    with app.app_context():
        insp = inspect(db.engine)
        for tbl in insp.get_table_names():
            click.secho(f"\n== {tbl} ==", fg="cyan")
            for c in insp.get_columns(tbl):
                null = "NULL" if c.get("nullable", True) else "NOT NULL"
                default = c.get("default")
                click.echo(f"  - {c['name']}: {c.get('type')} {null} default={default}")
            pk = insp.get_pk_constraint(tbl)
            if pk and pk.get("constrained_columns"):
                click.echo(f"  PK: {pk['constrained_columns']}")
            for fk in insp.get_foreign_keys(tbl):
                click.echo(
                    f"  FK: {fk['constrained_columns']} -> "
                    f"{fk['referred_table']}.{fk['referred_columns']}"
                )
            for i in insp.get_indexes(tbl):
                click.echo(
                    f"  IDX: {i['name']} cols={i['column_names']} unique={i.get('unique')}"
                )
        click.secho("\n✓ Diagnóstico concluído.", fg="green")


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


@app.cli.command("create-admin")
@click.option("--email", prompt=True, help="Email do administrador")
@click.option(
    "--nome", prompt=True, default="", show_default=False, help="Nome do administrador"
)
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="Senha do administrador",
)
def create_admin(email, nome, password):
    """Cria ou atualiza um usuário administrador (professor)."""
    from werkzeug.security import generate_password_hash

    with app.app_context():
        email = (email or "").strip().lower()
        if not email or not password:
            raise click.ClickException("Email e senha são obrigatórios.")

        user = Usuario.query.filter_by(email=email).first()
        if user:
            click.secho(f"Usuário {email} encontrado. Atualizando…", fg="yellow")
            if hasattr(user, "nome") and nome:
                user.nome = nome
            if hasattr(user, "is_admin"):
                user.is_admin = True
            if hasattr(user, "set_password"):
                user.set_password(password)
            else:
                user.password_hash = generate_password_hash(password)
        else:
            if hasattr(Usuario, "create"):
                user = Usuario.create(
                    email=email, password=password, nome=nome, is_admin=True, commit=False
                )
            else:
                user = Usuario(
                    email=email, nome=nome if hasattr(Usuario, "nome") else None
                )
                if hasattr(user, "set_password"):
                    user.set_password(password)
                else:
                    user.password_hash = generate_password_hash(password)
                if hasattr(user, "is_admin"):
                    user.is_admin = True
                db.session.add(user)

        db.session.commit()
        click.secho(f"✓ Admin ativo: {user.email}", fg="green")
