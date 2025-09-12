# app/controllers/desafio_controller.py
from __future__ import annotations

from typing import Any, Dict, Tuple, Optional
from flask_login import current_user

from app.services.desafio_service import desafio_service
from app.utils.schemas import questao_to_dict


class DesafioController:
    """Controller para orquestrar as ações do modo desafio."""

    @staticmethod
    def proxima() -> Tuple[Optional[Dict], int]:
        """
        Retorna a próxima questão para o usuário logado.
        Retorna (None, 204) se não houver mais questões.
        """
        q = desafio_service.proxima_questao(current_user.id)
        if not q:
            return None, 204
        return questao_to_dict(q), 200

    @staticmethod
    def responder(payload: Dict[str, Any]) -> Tuple[Dict, int]:
        """
        Registra a resposta do usuário para a questão.
        Espera payload com questao_id (int) e resposta (str).
        """
        try:
            questao_id = int(payload.get("questao_id"))
        except (TypeError, ValueError):
            return {"error": "questao_id inválido"}, 400

        resposta = (payload.get("resposta") or "").strip().upper()
        if not resposta:
            return {"error": "resposta obrigatória"}, 400

        out = desafio_service.responder(current_user.id, questao_id, resposta)
        return {"questao_id": questao_id, **out}, 200
