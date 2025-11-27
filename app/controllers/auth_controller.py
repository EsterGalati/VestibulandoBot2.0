# app/controllers/auth_controller.py
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from flask import current_app, request
from flask_login import current_user, login_user, logout_user

from app.services.auth_service import auth_service
from app.utils.schemas import usuario_to_dict


class AuthController:
    """Controller para autenticacao e sessao de usuario."""

    @staticmethod
    def _log_event(
        action: str,
        status: int,
        *,
        email: Optional[str] = None,
        message: Optional[str] = None,
        extra: Dict[str, Any] | None = None,
        level: str = "info",
    ) -> None:
        try:
            remote_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        except RuntimeError:
            remote_ip = None

        parts = [f"action={action}", f"status={status}"]
        if email:
            parts.append(f"email={email}")
        if remote_ip:
            parts.append(f"ip={remote_ip}")
        if extra:
            parts.extend(f"{k}={v}" for k, v in extra.items() if v is not None)
        if message:
            safe_message = message.replace('"', "\"")
            parts.append(f'message="{safe_message}"')

        log_method = getattr(current_app.logger, level, current_app.logger.info)
        log_method("auth_event %s", " ".join(parts))

    @staticmethod
    def register(payload: Dict[str, Any]) -> Tuple[Dict, int]:
        """Registra um novo usuario e autentica na sessao."""
        email = (payload.get("email") or "").strip().lower()
        senha = (payload.get("senha") or "").strip()
        nome = (payload.get("nome") or "").strip()
        if not email or not senha:
            message = "Informe email e senha para registrar o usuario."
            AuthController._log_event(
                "register",
                400,
                email=email or None,
                message=message,
                extra={"reason": "missing_fields"},
            )
            return {"error": "missing_fields", "message": message}, 400

        try:
            user = auth_service.register(email, senha, nome)
        except ValueError as exc:
            message = "Este email ja foi cadastrado."
            AuthController._log_event(
                "register",
                409,
                email=email,
                message=message,
                extra={"reason": "email_exists", "detail": str(exc)},
            )
            return {"error": "email_already_registered", "message": message}, 409

        login_user(user)
        response = usuario_to_dict(user)
        response["message"] = "Usuario registrado e autenticado com sucesso."
        AuthController._log_event(
            "register",
            200,
            email=email,
            message=response["message"],
            extra={"user_id": getattr(user, "id", None)},
        )
        return response, 200

    @staticmethod
    def login(payload: Dict[str, Any]) -> Tuple[Dict, int]:
        """Autentica um usuario existente."""
        email = (payload.get("email") or "").strip().lower()
        senha = (payload.get("senha") or "").strip()
        if not email or not senha:
            message = "Informe email e senha para entrar."
            AuthController._log_event(
                "login",
                400,
                email=email or None,
                message=message,
                extra={"reason": "missing_fields"},
            )
            return {"error": "missing_credentials", "message": message}, 400

        user = auth_service.authenticate(email, senha)
        if not user:
            message = "Email ou senha incorretos."
            AuthController._log_event(
                "login",
                401,
                email=email,
                message=message,
                extra={"reason": "invalid_credentials"},
            )
            return {"error": "invalid_credentials", "message": message}, 401

        login_user(user)
        response = usuario_to_dict(user)
        response["message"] = "Login realizado com sucesso."
        AuthController._log_event(
            "login",
            200,
            email=email,
            message=response["message"],
            extra={"user_id": getattr(user, "id", None)},
        )
        return response, 200

    @staticmethod
    def logout() -> Tuple[Dict, int]:
        """Finaliza a sessao do usuario."""
        email = getattr(current_user, "email", None) if current_user.is_authenticated else None
        user_id = getattr(current_user, "id", None) if current_user.is_authenticated else None
        logout_user()
        message = "Sessao encerrada com sucesso."
        AuthController._log_event(
            "logout",
            200,
            email=email,
            message=message,
            extra={"user_id": user_id},
        )
        return {"ok": True, "message": message}, 200

    @staticmethod
    def me() -> Tuple[Dict, int]:
        """Retorna o usuario autenticado ou 401 se nao houver sessao."""
        if not current_user.is_authenticated:
            message = "Nenhum usuario autenticado."
            AuthController._log_event("me", 401, message=message)
            return {"error": "unauthenticated", "message": message}, 401

        response = usuario_to_dict(current_user)
        response["message"] = "Usuario autenticado."
        AuthController._log_event(
            "me",
            200,
            email=getattr(current_user, "email", None),
            message=response["message"],
            extra={"user_id": getattr(current_user, "id", None)},
        )
        return response, 200
