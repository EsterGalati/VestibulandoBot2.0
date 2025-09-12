# app/utils/schemas.py
from __future__ import annotations

from typing import Any, Dict
from app.models import Usuario, QuestaoENEM


def usuario_to_dict(u: Usuario, include_nome: bool = True, include_admin: bool = True) -> Dict[str, Any]:
    """
    Serializa o usuário em dicionário seguro para API.
    :param include_nome: se True, inclui campo 'nome' (quando existir no modelo)
    :param include_admin: se True, inclui flag 'is_admin'
    """
    data: Dict[str, Any] = {
        "id": u.id,
        "email": u.email,
    }
    if include_nome and hasattr(u, "nome"):
        data["nome"] = u.nome or ""
    if include_admin and hasattr(u, "is_admin"):
        data["is_admin"] = bool(u.is_admin)
    return data


def questao_to_dict(q: QuestaoENEM, include_resposta: bool = False) -> Dict[str, Any]:
    """
    Serializa uma questão em dicionário.
    :param include_resposta: se True, inclui a resposta correta (ex.: uso admin/debug)
    """
    data: Dict[str, Any] = {
        "id": q.id,
        "ano": q.ano,
        "pergunta": q.pergunta,
        "alternativas": {
            "A": q.opcao_a,
            "B": q.opcao_b,
            "C": q.opcao_c,
            "D": q.opcao_d,
            "E": q.opcao_e,
        },
    }
    if include_resposta:
        data["resposta_correta"] = q.resposta_correta
    return data
