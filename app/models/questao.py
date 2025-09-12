# app/models/questao.py
from __future__ import annotations

from typing import Dict
from app.extensions import db


class QuestaoENEM(db.Model):
    """Modelo que representa uma questão do ENEM."""

    __tablename__ = "questoes_enem"

    # -----------------------
    # Colunas
    # -----------------------
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ano = db.Column(db.Integer, nullable=False, index=True)
    pergunta = db.Column(db.Text, nullable=False)
    opcao_a = db.Column(db.Text, nullable=False)
    opcao_b = db.Column(db.Text, nullable=False)
    opcao_c = db.Column(db.Text, nullable=False)
    opcao_d = db.Column(db.Text, nullable=False)
    opcao_e = db.Column(db.Text, nullable=False)
    resposta_correta = db.Column(db.String(1), nullable=False)  # 'A'..'E'

    # -----------------------
    # Métodos de utilidade
    # -----------------------
    def to_dict(self) -> Dict:
        """Serializa a questão em dicionário (útil para APIs)."""
        return {
            "id": self.id,
            "ano": self.ano,
            "pergunta": self.pergunta,
            "opcoes": {
                "A": self.opcao_a,
                "B": self.opcao_b,
                "C": self.opcao_c,
                "D": self.opcao_d,
                "E": self.opcao_e,
            },
            "resposta_correta": self.resposta_correta,
        }

    @classmethod
    def by_ano(cls, ano: int) -> list["QuestaoENEM"]:
        """Retorna todas as questões de um ano específico."""
        return cls.query.filter_by(ano=ano).all()

    @classmethod
    def random(cls, limit: int = 1) -> list["QuestaoENEM"]:
        """Retorna questões aleatórias (pode ser útil no modo desafio)."""
        return cls.query.order_by(db.func.random()).limit(limit).all()

    def __repr__(self) -> str:  # debug/dev
        return f"<QuestaoENEM id={self.id} ano={self.ano} resposta={self.resposta_correta}>"
