# app/controllers/desempenho_controller.py
from __future__ import annotations

from typing import Any, Dict, List, Tuple
from flask_login import current_user

from app.services.desempenho_service import desempenho_service

class DesempenhoController:
    """Controller para consultas de desempenho do usuário logado."""

    @staticmethod
    def resumo() -> Tuple[Dict[str, Any], int]:
        """
        Retorna um resumo geral do desempenho do usuário:
        total respondidas, acertos, erros, acurácia etc.
        """
        return desempenho_service.resumo(current_user.id), 200

    @staticmethod
    def por_ano() -> Tuple[List[Dict[str, Any]], int]:
        """
        Retorna a acurácia e estatísticas agrupadas por ano.
        """
        return desempenho_service.por_ano(current_user.id), 200

    @staticmethod
    def por_assunto() -> Tuple[List[Dict[str, Any]], int]:
        """
        Retorna estatísticas agrupadas por assunto (matéria ou área).
        """
        return desempenho_service.por_assunto(current_user.id), 200
