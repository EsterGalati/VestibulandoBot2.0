from flask_login import current_user
from app.services import desafio_service
from app.utils.schemas import questao_to_dict


def proxima_controller():
    q = desafio_service.proxima_questao(current_user.id)
    if not q:
        return None, 204
    return questao_to_dict(q), 200


def responder_controller(payload):
    questao_id = int(payload.get("questao_id"))
    resposta = payload.get("resposta")
    out = desafio_service.responder(current_user.id, questao_id, resposta)
    return {"questao_id": questao_id, **out}, 200
