from __future__ import annotations
from typing import Dict
from app.extensions import db


class SimuladoQuestao(db.Model):
    """Tabela de associação entre simulados e questões."""

    __tablename__ = "TB_SIMULADO_QUESTAO"

    cod_simulado_questao = db.Column("COD_SIMULADO_QUESTAO", db.Integer, primary_key=True, autoincrement=True)
    cod_simulado = db.Column("COD_SIMULADO", db.Integer, db.ForeignKey("TB_SIMULADO.COD_SIMULADO"), nullable=False)
    cod_questao = db.Column("COD_QUESTAO", db.Integer, db.ForeignKey("TB_QUESTAO.COD_QUESTAO"), nullable=False)
    ordem = db.Column("ORDEM", db.Integer, nullable=True)

    simulado = db.relationship("Simulado", back_populates="questoes")
    questao = db.relationship("QuestaoENEM", lazy=True)

    def to_dict(self, incluir_questao: bool = False) -> Dict:
        data = {
            "cod_simulado_questao": self.cod_simulado_questao,
            "cod_simulado": self.cod_simulado,
            "cod_questao": self.cod_questao,
            "ordem": self.ordem,
        }
        if incluir_questao and self.questao:
            data["questao"] = self.questao.to_dict()
        return data
