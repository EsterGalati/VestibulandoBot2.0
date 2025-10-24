from __future__ import annotations
from typing import Dict
from app.extensions import db


class QuestaoAlternativa(db.Model):
    """Alternativas vinculadas a cada questão (A, B, C, D, E)."""

    __tablename__ = "TB_QUESTAO_ALTERNATIVA"

    cod_alternativa = db.Column("COD_ALTERNATIVA", db.Integer, primary_key=True, autoincrement=True)
    cod_questao = db.Column("COD_QUESTAO", db.Integer, db.ForeignKey("TB_QUESTAO.COD_QUESTAO"), nullable=False)
    tx_letra = db.Column("TX_LETRA", db.String(1), nullable=False)
    tx_texto = db.Column("TX_TEXTO", db.Text, nullable=False)

    # Relacionamentos 1:N e N:1
    questao = db.relationship("QuestaoENEM", back_populates="alternativas")

    def to_dict(self) -> Dict:
        return {
            "cod_alternativa": self.cod_alternativa,
            "cod_questao": self.cod_questao,
            "tx_letra": self.tx_letra,
            "tx_texto": self.tx_texto,
        }

    def __repr__(self):
        return f"<Alternativa cod={self.cod_alternativa} letra={self.tx_letra} questao={self.cod_questao}>"
