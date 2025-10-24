from app.extensions import db

class SimuladoMateria(db.Model):
    """Tabela de associação entre Simulado e Materia (relação N:N)."""
    __tablename__ = "TB_SIMULADO_MATERIA"

    cod_simulado = db.Column(
        "COD_SIMULADO",
        db.Integer,
        db.ForeignKey("TB_SIMULADO.COD_SIMULADO", ondelete="CASCADE"),
        primary_key=True
    )
    cod_materia = db.Column(
        "COD_MATERIA",
        db.Integer,
        db.ForeignKey("TB_MATERIA.COD_MATERIA", ondelete="CASCADE"),
        primary_key=True
    )

    simulado = db.relationship("Simulado", back_populates="simulado_materias")
    materia = db.relationship("Materia", back_populates="materia_simulados")

    def __repr__(self):
        return f"<SimuladoMateria simulado={self.cod_simulado} materia={self.cod_materia}>"
