from __future__ import annotations
from datetime import datetime
from typing import Dict
from app.extensions import db


class ResultadoSimulado(db.Model):
    """Armazena o resultado final de um usuário em um simulado."""

    __tablename__ = "TB_RESULTADO_SIMULADO"

    cod_resultado = db.Column("COD_RESULTADO", db.Integer, primary_key=True, autoincrement=True)
    cod_usuario = db.Column("COD_USUARIO", db.Integer, db.ForeignKey("TB_USUARIO.COD_USUARIO"), nullable=False)
    cod_simulado = db.Column("COD_SIMULADO", db.Integer, db.ForeignKey("TB_SIMULADO.COD_SIMULADO"), nullable=False)

    qtd_acertos = db.Column("QTD_ACERTOS", db.Integer, nullable=False, default=0)
    qtd_erros = db.Column("QTD_ERROS", db.Integer, nullable=False, default=0)
    nota_final = db.Column("NOTA_FINAL", db.Float, nullable=True)
    dt_finalizacao = db.Column("DT_FINALIZACAO", db.DateTime, default=datetime.utcnow, nullable=False)

    usuario = db.relationship("Usuario", back_populates="resultados_simulados")
    simulado = db.relationship("Simulado", back_populates="resultados")

    def calcular_nota(self, total_questoes: int) -> None:
        self.nota_final = round((self.qtd_acertos / total_questoes) * 100, 2) if total_questoes > 0 else 0.0

    def to_dict(self) -> Dict:
        return {
            "cod_resultado": self.cod_resultado,
            "cod_usuario": self.cod_usuario,
            "cod_simulado": self.cod_simulado,
            "qtd_acertos": self.qtd_acertos,
            "qtd_erros": self.qtd_erros,
            "nota_final": self.nota_final,
            "dt_finalizacao": self.dt_finalizacao.isoformat() if self.dt_finalizacao else None,
        }

    def __repr__(self):
        return (
            f"<ResultadoSimulado cod={self.cod_resultado} "
            f"usuario={self.cod_usuario} simulado={self.cod_simulado} "
            f"nota={self.nota_final}>"
        )
