from flask_login import current_user
from app.services import desempenho_service


def resumo_controller() -> tuple[dict, int]:
    return desempenho_service.resumo(current_user.id), 200


def por_ano_controller() -> tuple[list[dict], int]:
    return desempenho_service.por_ano(current_user.id), 200


def por_assunto_controller() -> tuple[list[dict], int]:
    return desempenho_service.por_assunto(current_user.id), 200
