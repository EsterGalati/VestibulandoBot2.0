from __future__ import annotations
from typing import Dict, List
from app.extensions import db


class QuestaoENEM(db.Model):
    """Tabela principal de questões (ENEM, simulados, etc.)."""

    __tablename__ = "TB_QUESTAO"

    cod_questao = db.Column("COD_QUESTAO", db.Integer, primary_key=True, autoincrement=True)
    tx_questao = db.Column("TX_QUESTAO", db.Text, nullable=False)
    ano_questao = db.Column("ANO_QUESTAO", db.Integer, nullable=False, index=True)
    tx_resposta_correta = db.Column("TX_RESPOSTA_CORRETA", db.String(1), nullable=False)

    # Chave estrangeira da matéria
    cod_materia = db.Column(
        "COD_MATERIA",
        db.Integer,
        db.ForeignKey("TB_MATERIA.COD_MATERIA"),
        nullable=False
    )

    # Relacionamento com matéria
    materia = db.relationship("Materia", back_populates="questoes")

    # Relacionamento 1:N com alternativas
    alternativas = db.relationship(
        "QuestaoAlternativa",
        back_populates="questao",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def to_dict(self) -> Dict:
        return {
            "cod_questao": self.cod_questao,
            "tx_questao": self.tx_questao,
            "ano_questao": self.ano_questao,
            "tx_resposta_correta": self.tx_resposta_correta,
            "cod_materia": self.cod_materia,
            "materia": self.materia.nome_materia if self.materia else None,
            "alternativas": [alt.to_dict() for alt in self.alternativas],
        }

    @classmethod
    def by_ano(cls, ano: int) -> List["QuestaoENEM"]:
        return cls.query.filter_by(ano_questao=ano).all()

    @classmethod
    def random(cls, limit: int = 1) -> List["QuestaoENEM"]:
        return cls.query.order_by(db.func.random()).limit(limit).all()

    def __repr__(self):
        return f"<Questao cod={self.cod_questao} ano={self.ano_questao} materia={self.cod_materia}>"
