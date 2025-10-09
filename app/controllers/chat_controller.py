# app/controllers/chat_controller.py
from __future__ import annotations

from typing import Any, Dict, Tuple

from flask import current_app

from app.services.chat_service import chat_service


class ChatController:
    """Controller para orquestrar interacoes com a IA tutora do ENEM."""

    @staticmethod
    def perguntar(payload: Dict[str, Any]) -> Tuple[Dict[str, str], int]:
        pergunta = (
            payload.get("pergunta")
            or payload.get("question")
            or ""
        )

        pergunta = pergunta.strip()
        if not pergunta:
            return {
                "error": "pergunta_obrigatoria",
                "message": "Informe a pergunta que deseja enviar para a IA.",
            }, 400

        try:
            resposta = chat_service.perguntar(pergunta)
        except ValueError as exc:
            current_app.logger.info("chat_controller.perguntar erro de validacao: %s", exc)
            return {
                "error": "pergunta_invalida",
                "message": str(exc),
            }, 400
        except RuntimeError as exc:
            current_app.logger.error("chat_controller.perguntar erro ao consultar IA: %s", exc)
            return {
                "error": "ia_indisponivel",
                "message": "Nao foi possivel obter a resposta da IA. Tente novamente em instantes.",
            }, 502

        return {
            "pergunta": pergunta,
            "resposta": resposta,
        }, 200
