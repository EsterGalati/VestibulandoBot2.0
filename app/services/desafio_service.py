from sqlalchemy import func
from app.extensions import db
from app.models import QuestaoENEM, ResultadoUsuario


def proxima_questao(usuario_id: int) -> QuestaoENEM | None:
    # primeira questão ainda não respondida pelo usuário (simples; você pode randomizar)
    subq = db.session.query(ResultadoUsuario.questao_id).filter_by(
        usuario_id=usuario_id
    )
    return (
        db.session.query(QuestaoENEM)
        .filter(~QuestaoENEM.id.in_(subq))
        .order_by(QuestaoENEM.id.asc())
        .first()
    )


def responder(usuario_id: int, questao_id: int, resposta: str) -> dict:
    q = db.session.get(QuestaoENEM, questao_id)
    if not q:
        raise ValueError("questao_nao_encontrada")

    r = (resposta or "").upper().strip()
    if r not in {"A", "B", "C", "D", "E"}:
        raise ValueError("resposta_invalida")

    acertou = r == (q.resposta_correta or "").upper().strip()
    db.session.add(
        ResultadoUsuario(
            usuario_id=usuario_id,
            questao_id=questao_id,
            resposta=r,
            acertou=acertou,
        )
    )
    db.session.commit()

    return {"acertou": acertou, "correta": (q.resposta_correta or "").upper().strip()}
