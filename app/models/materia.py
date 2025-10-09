from __future__ import annotations
from app.extensions import db


class Materia(db.Model):
    """Tabela de matérias do ENEM."""

    __tablename__ = "TB_MATERIA"

    cod_materia = db.Column("COD_MATERIA", db.Integer, primary_key=True, autoincrement=True)
    nome_materia = db.Column("NOME_MATERIA", db.String(100), nullable=False, unique=True)

    # Relacionamento 1:N com QuestaoENEM
    questoes = db.relationship(
        "QuestaoENEM",
        back_populates="materia",
        cascade="all, delete-orphan",
        lazy=True
    )

    def to_dict(self):
        return {
            "cod_materia": self.cod_materia,
            "nome_materia": self.nome_materia,
        }

    def __repr__(self):
        return f"<Materia cod={self.cod_materia} nome={self.nome_materia}>"
