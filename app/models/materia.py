from __future__ import annotations
from app.extensions import db
from app.models.simulado_materia import SimuladoMateria

class Materia(db.Model):
    """Tabela de matérias do ENEM."""
    __tablename__ = "TB_MATERIA"

    cod_materia = db.Column("COD_MATERIA", db.Integer, primary_key=True, autoincrement=True)
    nome_materia = db.Column("NOME_MATERIA", db.String(100), nullable=False, unique=True)

    questoes = db.relationship(
        "QuestaoENEM",
        back_populates="materia",
        cascade="all, delete-orphan",
        lazy=True
    )

    materia_simulados = db.relationship(
        "SimuladoMateria",
        back_populates="materia",
        cascade="all, delete-orphan",
        lazy=True,
        overlaps="simulados,materias,simulado_materias,simulado"
    )

    simulados = db.relationship(
        "Simulado",
        secondary=lambda: SimuladoMateria.__table__,
        back_populates="materias",
        lazy="joined",
        overlaps="materia_simulados,simulado_materias,materia,simulado"
    )

    def to_dict(self):
        return {
            "cod_materia": self.cod_materia,
            "nome_materia": self.nome_materia,
        }

    def __repr__(self):
        return f"<Materia cod={self.cod_materia} nome={self.nome_materia}>"
