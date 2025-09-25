from __future__ import annotations

from typing import Dict, Optional, Tuple

import requests
from flask import current_app


class ChatService:
    """Caso de uso para conversar com a IA tutora do ENEM."""

    def perguntar(self, pergunta: str) -> str:
        pergunta = (pergunta or "").strip()
        if not pergunta:
            raise ValueError("Pergunta obrigatoria para consultar a IA.")

        url, api_key, timeout, body = self._montar_requisicao(pergunta)
        resposta = self._consultar_provedor(url, api_key, timeout, body)
        return self._normalizar_resposta(resposta)

    def _montar_requisicao(self, pergunta: str) -> Tuple[str, Optional[str], float, Dict]:
        url, api_key, timeout, model = self._carregar_config()

        system_prompt = self._instrucoes_sistema()
        mensagens = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": pergunta},
        ]

        body: Dict = {
            "model": model,
            "messages": mensagens,
            "temperature": 0.3,
            "top_p": 0.9,
            "max_completion_tokens": 600,
            "n": 1,
        }
        return url, api_key, timeout, body

    @staticmethod
    def _carregar_config() -> Tuple[str, Optional[str], float, str]:
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

        model = (cfg.get("CHAT_API_MODEL") or "").strip()
        if not model:
            raise RuntimeError("CHAT_API_MODEL nao configurado. Ajuste o .env.")

        return url, api_key, timeout, model

    @staticmethod
    def _instrucoes_sistema() -> str:
        return (
            "Voce e uma assistente de estudos para o ENEM. Responda em ate tres paragrafos curtos, "
            "em portugues do Brasil, sendo objetiva e conectando a resposta ao contexto do exame. "
            "Se fizer sentido, cite competencias ou provas especificas do ENEM."
        )

    def _consultar_provedor(
        self,
        url: str,
        api_key: Optional[str],
        timeout: float,
        body: Dict,
    ) -> Dict:
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            response = requests.post(
                url,
                json=body,
                headers=headers,
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as exc:
            status = getattr(exc.response, "status_code", None)
            preview = ""
            if getattr(exc.response, "text", None):
                preview = exc.response.text[:500].strip()
            current_app.logger.error(
                "chat_service HTTP error status=%s preview=%s", status, preview
            )
            raise RuntimeError("Falha ao consultar o provedor de IA.") from exc
        except requests.RequestException as exc:
            current_app.logger.error("chat_service request exception: %s", exc)
            raise RuntimeError("Falha ao consultar o provedor de IA.") from exc
        except ValueError as exc:
            current_app.logger.error("chat_service erro ao converter resposta em JSON: %s", exc)
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
