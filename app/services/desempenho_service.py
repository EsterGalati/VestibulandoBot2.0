# app/services/desempenho_service.py
from sqlalchemy import func, case
from app.extensions import db
from app.models import QuestaoENEM, ResultadoUsuario
from app.utils.classificacao import classificar_assunto


def resumo(usuario_id: int) -> dict:
    total = (
        db.session.query(func.count(ResultadoUsuario.id))
        .filter(ResultadoUsuario.usuario_id == usuario_id)
        .scalar()
        or 0
    )
    acertos = (
        db.session.query(func.count(ResultadoUsuario.id))
        .filter(
            ResultadoUsuario.usuario_id == usuario_id,
            ResultadoUsuario.acertou.is_(True),
        )
        .scalar()
        or 0
    )
    percentual = round((acertos / total * 100), 2) if total else 0.0
    return {"total": total, "acertos": acertos, "percentual": percentual}


def por_ano(usuario_id: int) -> list[dict]:
    rows = (
        db.session.query(
            QuestaoENEM.ano.label("ano"),
            func.count(ResultadoUsuario.id).label("total"),
            func.sum(case((ResultadoUsuario.acertou.is_(True), 1), else_=0)).label(
                "acertos"
            ),
        )
        .join(QuestaoENEM, ResultadoUsuario.questao_id == QuestaoENEM.id)
        .filter(ResultadoUsuario.usuario_id == usuario_id)
        .group_by(QuestaoENEM.ano)
        .order_by(QuestaoENEM.ano)
        .all()
    )
    out: list[dict] = []
    for r in rows:
        ac = int(r.acertos or 0)
        out.append(
            {
                "ano": r.ano,
                "total": r.total,
                "acertos": ac,
                "percentual": round((ac / r.total * 100), 2) if r.total else 0.0,
            }
        )
    return out


def por_assunto(usuario_id: int) -> list[dict]:
    # carrega texto da pergunta para classificar
    rows = (
        db.session.query(ResultadoUsuario, QuestaoENEM)
        .join(QuestaoENEM, ResultadoUsuario.questao_id == QuestaoENEM.id)
        .filter(ResultadoUsuario.usuario_id == usuario_id)
        .all()
    )

    bucket: dict[str, dict] = {}
    for res, q in rows:
        assunto = classificar_assunto(q.pergunta)
        if assunto not in bucket:
            bucket[assunto] = {"assunto": assunto, "total": 0, "acertos": 0}
        bucket[assunto]["total"] += 1
        if res.acertou:
            bucket[assunto]["acertos"] += 1

    # calcula percentual
    out: list[dict] = []
    for d in bucket.values():
        total = d["total"]
        ac = d["acertos"]
        d["percentual"] = round((ac / total * 100), 2) if total else 0.0
        out.append(d)

    # ordena por percentual desc
    out.sort(key=lambda x: x["percentual"], reverse=True)
    return out
