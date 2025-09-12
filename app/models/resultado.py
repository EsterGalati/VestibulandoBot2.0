# app/models/resultado.py
from __future__ import annotations

from typing import Dict, Optional, List, Tuple
from sqlalchemy import Index, UniqueConstraint
from app.extensions import db


class ResultadoUsuario(db.Model):
    """Respostas dos usuários por questão."""

    __tablename__ = "resultado_usuario"

    # -------------
    # Colunas
    # -------------
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    usuario_id = db.Column(
        db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    questao_id = db.Column(
        db.Integer, db.ForeignKey("questoes_enem.id", ondelete="CASCADE"), nullable=False, index=True
    )

    resposta = db.Column(db.String(1), nullable=False)  # 'A'..'E'
    acertou = db.Column(db.Boolean, nullable=False)

    respondido_em = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        nullable=False,
        index=True,
    )

    # -------------
    # Relacionamentos
    # -------------
    usuario = db.relationship("Usuario", backref="resultados")
    questao = db.relationship("QuestaoENEM", backref="respostas")

    # -------------
    # Índices / Constraints
    # -------------
    __table_args__ = (
        # Evita múltiplos registros do mesmo usuário para a mesma questão
        UniqueConstraint("usuario_id", "questao_id", name="uq_usuario_questao"),
        # Índices auxiliares para filtros comuns
        Index("ix_resultado_usuario_usuario_id_data", "usuario_id", "respondido_em"),
        Index("ix_resultado_usuario_questao_id_data", "questao_id", "respondido_em"),
    )

    # -------------
    # Utilidades
    # -------------
    def to_dict(self) -> Dict:
        """Serialização amigável para APIs."""
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "questao_id": self.questao_id,
            "resposta": self.resposta,
            "acertou": self.acertou,
            "respondido_em": self.respondido_em.isoformat() if self.respondido_em else None,
        }

    @classmethod
    def registrar_resposta(
        cls, *, usuario_id: int, questao_id: int, resposta: str, correta: str
    ) -> "ResultadoUsuario":
        """
        Cria ou atualiza a resposta do usuário para a questão,
        garantindo unicidade (usuario_id, questao_id).
        """
        resposta = (resposta or "").strip().upper()
        correta = (correta or "").strip().upper()
        acertou = resposta == correta

        inst: Optional["ResultadoUsuario"] = cls.query.filter_by(
            usuario_id=usuario_id, questao_id=questao_id
        ).first()

        if inst:
            inst.resposta = resposta
            inst.acertou = acertou
        else:
            inst = cls(
                usuario_id=usuario_id,
                questao_id=questao_id,
                resposta=resposta,
                acertou=acertou,
            )
            db.session.add(inst)

        db.session.commit()
        return inst

    @classmethod
    def stats_usuario(cls, usuario_id: int) -> Dict[str, int | float]:
        """
        Retorna estatísticas básicas do usuário:
        total respondidas, acertos, erros e acurácia (%).
        """
        total = cls.query.filter_by(usuario_id=usuario_id).count()
        acertos = cls.query.filter_by(usuario_id=usuario_id, acertou=True).count()
        erros = total - acertos
        acc = (acertos / total * 100.0) if total else 0.0
        return {"total": total, "acertos": acertos, "erros": erros, "acuracia_pct": round(acc, 2)}

    @classmethod
    def acuracia_por_ano(cls, usuario_id: int) -> List[Dict[str, int | float]]:
        """
        Acurácia agrupada pelo ano da questão.
        """
        # join com questoes_enem para obter o ano
        from app.models import QuestaoENEM  # import local para evitar ciclo
        q = (
            db.session.query(QuestaoENEM.ano, db.func.count(cls.id), db.func.sum(db.case((cls.acertou, 1), else_=0)))
            .join(QuestaoENEM, QuestaoENEM.id == cls.questao_id)
            .filter(cls.usuario_id == usuario_id)
            .group_by(QuestaoENEM.ano)
            .order_by(QuestaoENEM.ano.asc())
        )

        resultado: List[Dict[str, int | float]] = []
        for ano, total, acertos in q:
            acc = (acertos / total * 100.0) if total else 0.0
            resultado.append(
                {"ano": int(ano), "total": int(total), "acertos": int(acertos or 0), "acuracia_pct": round(acc, 2)}
            )
        return resultado

    def __repr__(self) -> str:
        return (
            f"<ResultadoUsuario id={self.id} usuario={self.usuario_id} "
            f"questao={self.questao_id} resp={self.resposta} ok={self.acertou}>"
        )
