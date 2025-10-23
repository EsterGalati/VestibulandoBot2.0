from __future__ import annotations
from datetime import datetime
from app.extensions import db


class RelProfAluno(db.Model):
    """
    Relação entre professor e aluno.
    Cada registro representa o vínculo de um professor (usuário admin/professor)
    com um aluno (usuário comum).
    """

    __tablename__ = "REL_PROF_ALUNO"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    cod_usuario_prof = db.Column(
        "COD_USUARIO_PROF",
        db.Integer,
        db.ForeignKey("TB_USUARIO.COD_USUARIO", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    cod_usuario_aluno = db.Column(
        "COD_USUARIO_ALUNO",
        db.Integer,
        db.ForeignKey("TB_USUARIO.COD_USUARIO", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    dt_criacao = db.Column(
        "DT_CRIACAO",
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # --- RELACIONAMENTOS ---
    professor = db.relationship(
        "Usuario",
        foreign_keys=[cod_usuario_prof],
        backref=db.backref("alunos_vinculados", cascade="all, delete-orphan", lazy=True)
    )

    aluno = db.relationship(
        "Usuario",
        foreign_keys=[cod_usuario_aluno],
        backref=db.backref("professores_vinculados", cascade="all, delete-orphan", lazy=True)
    )

    # --- MÉTODOS AUXILIARES ---
    def to_dict(self):
        return {
            "id": self.id,
            "cod_usuario_prof": self.cod_usuario_prof,
            "cod_usuario_aluno": self.cod_usuario_aluno,
            "dt_criacao": self.dt_criacao.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<RelProfAluno prof={self.cod_usuario_prof} aluno={self.cod_usuario_aluno}>"
