# app/services/desempenho_service.py
from __future__ import annotations

from typing import Dict, List
from sqlalchemy import func, case
from app.extensions import db
from app.models import QuestaoENEM, ResultadoUsuario
from app.utils.classificacao import classificar_assunto


class DesempenhoService:
    """Casos de uso para estatísticas de desempenho do usuário."""

    # -----------------------------
    # Resumo (1 query agregada)
    # -----------------------------
    def resumo(self, usuario_id: int) -> Dict:
        """
        Retorna {"total", "acertos", "percentual"}.
        Faz uma única query com agregações.
        """
        total, acertos = (
            db.session.query(
                func.count(ResultadoUsuario.id),
                func.sum(case((ResultadoUsuario.acertou.is_(True), 1), else_=0)),
            )
            .filter(ResultadoUsuario.usuario_id == usuario_id)
            .one()
        )

        total = int(total or 0)
        acertos = int(acertos or 0)
        percentual = round((acertos / total * 100), 2) if total else 0.0
        return {"total": total, "acertos": acertos, "percentual": percentual}

    # -----------------------------
    # Por ano (1 query agregada)
    # -----------------------------
    def por_ano(self, usuario_id: int) -> List[Dict]:
        """
        Lista [{"ano","total","acertos","percentual"}] ordenada por ano.
        """
        rows = (
            db.session.query(
                QuestaoENEM.ano.label("ano"),
                func.count(ResultadoUsuario.id).label("total"),
                func.sum(case((ResultadoUsuario.acertou.is_(True), 1), else_=0)).label("acertos"),
            )
            .join(QuestaoENEM, ResultadoUsuario.questao_id == QuestaoENEM.id)
            .filter(ResultadoUsuario.usuario_id == usuario_id)
            .group_by(QuestaoENEM.ano)
            .order_by(QuestaoENEM.ano)
            .all()
        )

        out: List[Dict] = []
        for r in rows:
            total = int(r.total or 0)
            acertos = int(r.acertos or 0)
            out.append(
                {
                    "ano": int(r.ano),
                    "total": total,
                    "acertos": acertos,
                    "percentual": round((acertos / total * 100), 2) if total else 0.0,
                }
            )
        return out

    # -----------------------------
    # Por assunto (classificação Python)
    # -----------------------------
    def por_assunto(self, usuario_id: int) -> List[Dict]:
        """
        Lista [{"assunto","total","acertos","percentual"}] ordenada por percentual desc.
        Carrega apenas o necessário (pergunta, acertou) e classifica em Python.
        """
        rows = (
            db.session.query(QuestaoENEM.pergunta, ResultadoUsuario.acertou)
            .join(QuestaoENEM, ResultadoUsuario.questao_id == QuestaoENEM.id)
            .filter(ResultadoUsuario.usuario_id == usuario_id)
            .all()
        )

        bucket: Dict[str, Dict[str, float | int | str]] = {}
        for pergunta, acertou in rows:
            assunto = classificar_assunto(pergunta or "")
            b = bucket.setdefault(assunto, {"assunto": assunto, "total": 0, "acertos": 0})
            b["total"] = int(b["total"]) + 1
            if bool(acertou):
                b["acertos"] = int(b["acertos"]) + 1

        out: List[Dict] = []
        for d in bucket.values():
            total = int(d["total"])
            acertos = int(d["acertos"])
            d["percentual"] = round((acertos / total * 100), 2) if total else 0.0
            out.append(d)

        out.sort(key=lambda x: x["percentual"], reverse=True)
        return out


# instância para manter compatibilidade com imports existentes
desempenho_service = DesempenhoService()
