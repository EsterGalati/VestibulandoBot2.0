from __future__ import annotations
from datetime import datetime
from typing import Dict, List
from app.extensions import db


class Simulado(db.Model):
    """Tabela de simulados disponíveis (ENEM, desafios, testes rápidos etc.)."""

    __tablename__ = "TB_SIMULADO"

    cod_simulado = db.Column("COD_SIMULADO", db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column("TITULO", db.String(150), nullable=False)
    descricao = db.Column("DESCRICAO", db.Text, nullable=True)
    dt_criacao = db.Column("DT_CRIACAO", db.DateTime, default=datetime.utcnow, nullable=False)
    ativo = db.Column("ATIVO", db.Boolean, nullable=False, default=True)
    cod_materia = db.Column("COD_MATERIA", db.Integer, db.ForeignKey("TB_MATERIA.COD_MATERIA"), nullable=True)

    # 🔽 Adiciona o relacionamento com Materia
    materia = db.relationship("Materia", back_populates="simulados", lazy=True)

    questoes = db.relationship(
        "SimuladoQuestao",
        back_populates="simulado",
        lazy=True,
        cascade="all, delete-orphan"
    )

    resultados = db.relationship(
        "ResultadoSimulado",
        back_populates="simulado",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def to_dict(self, incluir_questoes: bool = False) -> Dict:
        data = {
            "cod_simulado": self.cod_simulado,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "dt_criacao": self.dt_criacao.isoformat() if self.dt_criacao else None,
            "ativo": self.ativo,
            "cod_materia": self.cod_materia,
        }
        if incluir_questoes:
            data["questoes"] = [sq.to_dict() for sq in self.questoes]
        return data

    def __repr__(self):
        return f"<Simulado cod={self.cod_simulado} titulo='{self.titulo}'>"
