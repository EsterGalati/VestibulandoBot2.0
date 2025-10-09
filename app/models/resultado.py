from __future__ import annotations
from datetime import datetime
from typing import Dict
from app.extensions import db


class ResultadoSimulado(db.Model):
    """Resultado consolidado de um usuário em um simulado."""

    __tablename__ = "TB_RESULTADO_SIMULADO"

    cod_resultado = db.Column("COD_RESULTADO", db.Integer, primary_key=True, autoincrement=True)
    cod_usuario = db.Column("COD_USUARIO", db.Integer, db.ForeignKey("TB_USUARIO.COD_USUARIO"), nullable=False)
    cod_simulado = db.Column("COD_SIMULADO", db.Integer, db.ForeignKey("TB_SIMULADO.COD_SIMULADO"), nullable=False)

    qtd_acertos = db.Column("QTD_ACERTOS", db.Integer, nullable=False, default=0)
    qtd_erros = db.Column("QTD_ERROS", db.Integer, nullable=False, default=0)
    nota_final = db.Column("NOTA_FINAL", db.Float, nullable=True)
    dt_finalizacao = db.Column("DT_FINALIZACAO", db.DateTime, default=datetime.utcnow)

    usuario = db.relationship("Usuario", backref="resultados_simulados", lazy=True)
    simulado = db.relationship("Simulado", backref="resultados", lazy=True)

    def calcular_nota(self, total_questoes: int) -> None:
        """Calcula a nota final proporcional aos acertos."""
        if total_questoes > 0:
            self.nota_final = round((self.qtd_acertos / total_questoes) * 100, 2)
        else:
            self.nota_final = 0.0

    def to_dict(self) -> Dict:
        """Serializa o resultado do simulado."""
        return {
            "cod_resultado": self.cod_resultado,
            "cod_usuario": self.cod_usuario,
            "cod_simulado": self.cod_simulado,
            "qtd_acertos": self.qtd_acertos,
            "qtd_erros": self.qtd_erros,
            "nota_final": self.nota_final,
            "dt_finalizacao": self.dt_finalizacao.isoformat() if self.dt_finalizacao else None,
        }

    @classmethod
    def get_by_usuario_e_simulado(cls, cod_usuario: int, cod_simulado: int) -> "ResultadoSimulado | None":
        """Busca o resultado de um usuário em um simulado específico."""
        return cls.query.filter_by(cod_usuario=cod_usuario, cod_simulado=cod_simulado).first()

    @classmethod
    def registrar_resultado(
        cls,
        cod_usuario: int,
        cod_simulado: int,
        qtd_acertos: int,
        qtd_erros: int,
        total_questoes: int,
    ) -> "ResultadoSimulado":
        """Cria ou atualiza o resultado de um simulado."""
        resultado = cls.get_by_usuario_e_simulado(cod_usuario, cod_simulado)
        if resultado:
            resultado.qtd_acertos = qtd_acertos
            resultado.qtd_erros = qtd_erros
        else:
            resultado = cls(
                cod_usuario=cod_usuario,
                cod_simulado=cod_simulado,
                qtd_acertos=qtd_acertos,
                qtd_erros=qtd_erros,
            )
            db.session.add(resultado)

        resultado.calcular_nota(total_questoes)
        db.session.commit()
        return resultado

    def __repr__(self):
        return f"<ResultadoSimulado cod={self.cod_resultado} usuario={self.cod_usuario} simulado={self.cod_simulado} nota={self.nota_final}>"
