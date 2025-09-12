# app/cli.py
from __future__ import annotations

import click
from pathlib import Path
import pandas as pd

from app.extensions import db
from app.models import QuestaoENEM


class CLI:
    """Registra comandos de linha de comando da aplicação e
    concentra utilitários (ler CSV, validação e persistência)."""

    # colunas mínimas esperadas no CSV
    REQUIRED_COLUMNS = {
        "ano",
        "pergunta",
        "opcao_a",
        "opcao_b",
        "opcao_c",
        "opcao_d",
        "opcao_e",
        "resposta_correta",
    }

    def __init__(self, app):
        self.app = app

    # ----------------------------
    # Registro dos comandos (Click)
    # ----------------------------
    def register(self) -> None:
        """Registra os comandos Click na app Flask."""

        @self.app.cli.command("db-init")
        def db_init():
            """Cria as tabelas no banco."""
            with self.app.app_context():
                db.create_all()
                click.secho("✔ Tabelas criadas (ou já existentes).", fg="green")

        @self.app.cli.command("import-questoes")
        @click.option(
            "--csv",
            "csv_path",
            default="data/enem_questoes.csv",
            show_default=True,
            help="Caminho do CSV com as questões do ENEM",
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

            # 1) Ler CSV
            df = self._read_csv(path, encoding)

            # 2) Validar colunas
            self._validate_columns(df.columns)

            with self.app.app_context():
                # 3) Limpar tabela (opcional)
                if truncate:
                    self._truncate_table()

                # 4) Inserir em massa (chunked)
                total = self._bulk_insert(df, chunk_size=chunk_size)
                click.secho(f"✔ Importadas {total} questões de {path}", fg="green")

    # ----------------------------
    # Utilitários
    # ----------------------------
    def _read_csv(self, path: Path, encoding: str) -> pd.DataFrame:
        """Lê CSV com pandas e normaliza nomes de colunas."""
        try:
            df = pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError as e:
            raise click.ClickException(
                f"Erro de encoding ao ler {path}. "
                f"Tente --encoding utf-8-sig ou latin1. Detalhe: {e}"
            )
        # normaliza nomes de colunas para minúsculas
        df.columns = [c.strip().lower() for c in df.columns]
        return df

    def _validate_columns(self, columns) -> None:
        cols = set(columns)
        missing = self.REQUIRED_COLUMNS - cols
        if missing:
            raise click.ClickException(
                "CSV inválido. Faltando colunas: " + ", ".join(sorted(missing))
            )

    def _truncate_table(self) -> None:
        db.session.query(QuestaoENEM).delete()
        db.session.commit()
        click.secho("• Tabela de questões limpa.", fg="yellow")

    def _row_to_model(self, row: pd.Series) -> QuestaoENEM:
        """Mapeia uma linha do DataFrame para o modelo QuestaoENEM."""
        return QuestaoENEM(
            ano=int(row["ano"]),
            pergunta=str(row["pergunta"]),
            opcao_a=str(row["opcao_a"]),
            opcao_b=str(row["opcao_b"]),
            opcao_c=str(row["opcao_c"]),
            opcao_d=str(row["opcao_d"]),
            opcao_e=str(row["opcao_e"]),
            resposta_correta=str(row["resposta_correta"]).upper().strip(),
        )

    def _bulk_insert(self, df: pd.DataFrame, chunk_size: int = 0) -> int:
        """Insere em massa usando bulk_save_objects, com ou sem chunk."""
        if chunk_size and chunk_size > 0:
            total = 0
            # processa em blocos para reduzir memória/tempo de transação
            for start in range(0, len(df), chunk_size):
                end = start + chunk_size
                objs = [self._row_to_model(r) for _, r in df.iloc[start:end].iterrows()]
                db.session.bulk_save_objects(objs)
                db.session.commit()
                total += len(objs)
                click.secho(f"  • Inseridas {len(objs)} (acumulado {total})", fg="blue")
            return total
        else:
            objs = [self._row_to_model(r) for _, r in df.iterrows()]
            db.session.bulk_save_objects(objs)
            db.session.commit()
            return len(objs)


def register_cli(app) -> None:
    """Ponto de entrada mantido (compatível com o __init__.py)."""
    CLI(app).register()
