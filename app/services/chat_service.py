# app/services/chat_service.py
from __future__ import annotations

from typing import Dict, Tuple

import requests
from flask import current_app


class ChatService:
    """Caso de uso para conversar com a IA tutora do ENEM."""

    def perguntar(self, pergunta: str) -> str:
        """Envia a pergunta do usuario para a IA com o prompt padrao."""
        pergunta = (pergunta or "").strip()
        if not pergunta:
            raise ValueError("Pergunta obrigatoria para consultar a IA.")

        prompt = self._construir_prompt(pergunta)
        resposta = self._consultar_provedor(prompt)
        return self._normalizar_resposta(resposta)

    @staticmethod
    def _carregar_config() -> Tuple[str, str | None, float]:
        cfg = current_app.config
        url = (cfg.get("CHAT_API_URL") or "").strip()
        if not url:
            raise RuntimeError("CHAT_API_URL nao configurada. Ajuste o .env.")

        api_key = (cfg.get("CHAT_API_KEY") or "").strip() or None
        timeout_value = cfg.get("CHAT_API_TIMEOUT", 15)
        try:
            timeout = float(timeout_value)
        except (TypeError, ValueError):
            timeout = 15.0
        return url, api_key, timeout

    @staticmethod
    def _construir_prompt(pergunta: str) -> str:
        instrucoes = (
            "Voce e uma assistente de estudos para o ENEM. Responda em ate tres paragrafos "
            "curtos, em portugues do Brasil, sendo objetiva e conectando a resposta ao contexto "
            "do exame. Se fizer sentido, cite competencias ou provas especificas do ENEM."
        )
        return f"{instrucoes}\n\nPergunta: {pergunta}"

    def _consultar_provedor(self, prompt: str) -> Dict:
        url, api_key, timeout = self._carregar_config()

        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        payload = {"prompt": prompt}

        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            raise RuntimeError("Falha ao consultar o provedor de IA.") from exc
        except ValueError as exc:
            raise RuntimeError("Resposta do provedor de IA nao esta em JSON.") from exc

    @staticmethod
    def _normalizar_resposta(payload: Dict) -> str:
        if not isinstance(payload, dict):
            raise RuntimeError("Formato de resposta do provedor de IA invalido.")

        resposta = (
            payload.get("answer")
            or payload.get("response")
            or payload.get("message")
        )

        if not resposta and "choices" in payload:
            primeira_escolha = payload["choices"][0] if payload["choices"] else {}
            if isinstance(primeira_escolha, dict):
                resposta = (
                    primeira_escolha.get("text")
                    or (primeira_escolha.get("message") or {}).get("content")
                )

        if not resposta or not isinstance(resposta, str):
            raise RuntimeError("Nao foi possivel extrair a resposta da IA.")

        resposta = resposta.strip()
        if not resposta:
            raise RuntimeError("Resposta da IA vazia.")

        normalizado = resposta.replace("\r\n", "\n")
        paragrafos = [p.strip() for p in normalizado.split("\n\n") if p.strip()]
        if len(paragrafos) > 3:
            resposta = "\n\n".join(paragrafos[:3])
        if len(resposta) > 800:
            corte = resposta[:800].rstrip()
            if " " in corte:
                corte = corte.rsplit(" ", 1)[0]
            resposta = corte.rstrip(". ,;") + "..."

        return resposta


chat_service = ChatService()
