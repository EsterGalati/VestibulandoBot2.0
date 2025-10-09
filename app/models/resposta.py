from __future__ import annotations
from app.extensions import db
from datetime import datetime


class Resposta(db.Model):
    """Registro de respostas de alunos em simulados/desafios."""

    __tablename__ = "TB_RESPOSTA"

    cod_resposta = db.Column("COD_RESPOSTA", db.Integer, primary_key=True, autoincrement=True)
    cod_usuario = db.Column("COD_USUARIO", db.Integer, db.ForeignKey("TB_USUARIO.COD_USUARIO"), nullable=False)
    cod_questao = db.Column("COD_QUESTAO", db.Integer, db.ForeignKey("TB_QUESTAO.COD_QUESTAO"), nullable=False)
    cod_alternativa = db.Column("COD_ALTERNATIVA", db.Integer, db.ForeignKey("TB_QUESTAO_ALTERNATIVA.COD_ALTERNATIVA"), nullable=False)
    st_acerto = db.Column("ST_ACERTO", db.String(1), nullable=False)
    respondido_em = db.Column("RESPONDIDO_EM", db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    usuario = db.relationship("Usuario", back_populates="respostas")
    questao = db.relationship("QuestaoENEM", back_populates="respostas")
    alternativa = db.relationship("QuestaoAlternativa", back_populates="respostas")

    def to_dict(self):
        return {
            "cod_resposta": self.cod_resposta,
            "cod_usuario": self.cod_usuario,
            "cod_questao": self.cod_questao,
            "cod_alternativa": self.cod_alternativa,
            "st_acerto": self.st_acerto,
            "respondido_em": self.respondido_em.isoformat() if self.respondido_em else None,
        }

    @classmethod
    def registrar_resposta(cls, cod_usuario: int, cod_questao: int, cod_alternativa: int, alternativa_correta: str):
        from app.models.questao_alternativa import QuestaoAlternativa

        alternativa = QuestaoAlternativa.query.get(cod_alternativa)
        if not alternativa:
            raise ValueError("Alternativa inválida.")

        st_acerto = "S" if alternativa.tx_letra.upper() == alternativa_correta.upper() else "N"

        resposta = cls.query.filter_by(cod_usuario=cod_usuario, cod_questao=cod_questao).first()
        if resposta:
            resposta.cod_alternativa = cod_alternativa
            resposta.st_acerto = st_acerto
        else:
            resposta = cls(
                cod_usuario=cod_usuario,
                cod_questao=cod_questao,
                cod_alternativa=cod_alternativa,
                st_acerto=st_acerto,
            )
            db.session.add(resposta)

        db.session.commit()
        return resposta
