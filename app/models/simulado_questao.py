from __future__ import annotations
from typing import Dict
from app.extensions import db
from app.models.questao import QuestaoENEM


class SimuladoQuestao(db.Model):
    """Tabela de associação entre Simulado e Questões."""

    __tablename__ = "TB_SIMULADO_QUESTAO"

    cod_simulado_questao = db.Column("COD_SIMULADO_QUESTAO", db.Integer, primary_key=True, autoincrement=True)
    cod_simulado = db.Column("COD_SIMULADO", db.Integer, db.ForeignKey("TB_SIMULADO.COD_SIMULADO"), nullable=False)
    cod_questao = db.Column("COD_QUESTAO", db.Integer, db.ForeignKey("TB_QUESTAO.COD_QUESTAO"), nullable=False)
    ordem = db.Column("ORDEM", db.Integer, nullable=True)

    # Relações
    simulado = db.relationship("Simulado", back_populates="questoes")
    questao = db.relationship("QuestaoENEM", lazy=True)

    @staticmethod
    def listar_por_simulado(cod_simulado: int):
        """Lista todas as questões vinculadas a um simulado."""
        registros = SimuladoQuestao.query.filter_by(cod_simulado=cod_simulado).order_by(SimuladoQuestao.ordem).all()

        resultado = []
        for reg in registros:
            if reg.questao:
                resultado.append({
                    "cod_simulado_questao": reg.cod_simulado_questao,
                    "cod_simulado": reg.cod_simulado,
                    "cod_questao": reg.cod_questao,
                    "ordem": reg.ordem,
                    "questao": reg.questao.to_dict(incluir_alternativas=True)
                })
        return resultado

    def to_dict(self, incluir_questao: bool = False) -> Dict:
        data = {
            "cod_simulado_questao": self.cod_simulado_questao,
            "cod_simulado": self.cod_simulado,
            "cod_questao": self.cod_questao,
            "ordem": self.ordem,
        }
        if incluir_questao and self.questao:
            data["questao"] = self.questao.to_dict(incluir_alternativas=True)
        return data

    def __repr__(self):
        return f"<SimuladoQuestao simulado={self.cod_simulado} questao={self.cod_questao}>"
