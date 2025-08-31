# app/cli.py
import click
from app.extensions import db
from app.models import QuestaoENEM
import pandas as pd

def register_cli(app):
    @app.cli.command("db-init")
    def db_init():
        """Cria as tabelas no banco."""
        with app.app_context():
            db.create_all()
            click.echo("✔️ Tabelas criadas")

    @app.cli.command("import-questoes")
    @click.option("--csv", "csv_path", default="data/enem_questoes.csv", help="Caminho do CSV")
    def import_questoes(csv_path):
        """Importa questões do ENEM a partir de um CSV."""
        with app.app_context():
            df = pd.read_csv(csv_path, encoding="utf-8")
            db.session.query(QuestaoENEM).delete()
            db.session.commit()
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
            db.session.bulk_save_objects(objs)
            db.session.commit()
            click.echo(f"✔️ Importadas {len(objs)} questões de {csv_path}")
