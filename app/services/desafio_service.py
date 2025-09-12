# app/services/desafio_service.py
from __future__ import annotations

from typing import Optional, Dict
from sqlalchemy import exists
from sqlalchemy.orm import aliased
from app.extensions import db
from app.models import QuestaoENEM, ResultadoUsuario


class DesafioService:
    """Casos de uso do modo Desafio (seleção de questões e registro de respostas)."""

    # -------------------------
    # Seleção da próxima questão
    # -------------------------
    def proxima_questao(self, usuario_id: int, *, randomize: bool = False) -> Optional[QuestaoENEM]:
        """
        Retorna a primeira questão ainda não respondida pelo usuário.
        Se `randomize=True`, sorteia entre as não respondidas.
        """
        # Maneira eficiente: usa EXISTS para excluir as já respondidas
        RU = aliased(ResultadoUsuario)
        base = (
            db.session.query(QuestaoENEM)
            .filter(~exists().where((RU.questao_id == QuestaoENEM.id) & (RU.usuario_id == usuario_id)))
        )

        if randomize:
            # sqlite: db.func.random(); postgres: db.func.random() também funciona
            return base.order_by(db.func.random()).first()

        return base.order_by(QuestaoENEM.id.asc()).first()

    # -------------------------
    # Registrar resposta (upsert)
    # -------------------------
    def responder(self, usuario_id: int, questao_id: int, resposta: str) -> Dict:
        """
        Registra (ou atualiza) a resposta do usuário para a questão.
        Retorna dict com {'acertou': bool, 'correta': 'A'..'E'}.
        Lança ValueError para inputs inválidos.
        """
        q = db.session.get(QuestaoENEM, int(questao_id))  # type: ignore[arg-type]
        if not q:
            raise ValueError("questao_nao_encontrada")

        r = self._normalize_answer(resposta)
        if r not in {"A", "B", "C", "D", "E"}:
            raise ValueError("resposta_invalida")

        correta = (q.resposta_correta or "").strip().upper()
        # Usa método de upsert do modelo (evita duplicidade pelo UniqueConstraint)
        inst = ResultadoUsuario.registrar_resposta(
            usuario_id=usuario_id,
            questao_id=q.id,
            resposta=r,
            correta=correta,
        )

        return {"acertou": bool(inst.acertou), "correta": correta}

    # -------------------------
    # Helpers
    # -------------------------
    @staticmethod
    def _normalize_answer(value: str) -> str:
        return (value or "").strip().upper()


# Instância para import conveniente (mantém compatibilidade)
desafio_service = DesafioService()
