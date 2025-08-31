from flask_login import login_user, logout_user, current_user
from app.services import auth_service
from app.utils.schemas import usuario_to_dict


def register_controller(payload: dict) -> tuple[dict, int]:
    user = auth_service.register(payload.get("email"), payload.get("senha"))
    login_user(user)
    return usuario_to_dict(user), 200


def login_controller(payload: dict) -> tuple[dict, int]:
    user = auth_service.authenticate(payload.get("email"), payload.get("senha"))
    if not user:
        return {"error": "invalid_credentials"}, 401
    login_user(user)
    return usuario_to_dict(user), 200


def logout_controller() -> tuple[dict, int]:
    logout_user()
    return {"ok": True}, 200


def me_controller() -> tuple[dict, int]:
    if not current_user.is_authenticated:
        return {"error": "unauthenticated"}, 401
    return usuario_to_dict(current_user), 200
