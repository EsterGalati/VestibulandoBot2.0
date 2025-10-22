import os
import google.generativeai as genai


class ChatService:
    """Serviço responsável pela integração com o modelo Gemini."""

    @staticmethod
    def gerar_resposta(message: str) -> str:
        """
        Gera uma resposta do modelo Gemini com base na mensagem do usuário.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY não configurada")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        try:
            response = model.generate_content(
                f"Você é uma assistente de estudos para o ENEM. "
                f"Responda em até um parágrafo curto, em português do Brasil, "
                f"sendo objetiva e conectando a resposta ao contexto do exame. "
                f"Se fizer sentido, cite competências ou provas específicas do ENEM. "
                f"Se a pergunta não fizer sentido com seu objetivo, diga que não pode ajudar. "
                f"Caso a pergunta tenha ambiguidade, peça mais detalhes. "
                f"Não utilize asteriscos para deixar a resposta em negrito"
                f"Responda de forma simples e direta: {message}",
                generation_config={
                    "max_output_tokens": 1024,
                    "temperature": 0.7,
                },
            )

            # 🧩 Verifica se o modelo retornou partes válidas
            if not response or not getattr(response, "candidates", None):
                return "Desculpe, não consegui gerar uma resposta no momento."

            # Extrai o conteúdo de forma segura
            for candidate in response.candidates:
                if hasattr(candidate, "content") and candidate.content.parts:
                    parts = [
                        p.text for p in candidate.content.parts if hasattr(p, "text")
                    ]
                    reply = "\n".join(parts).strip()
                    if reply:
                        return reply

            finish_reason = getattr(response.candidates[0], "finish_reason", "unknown")
            print(f"⚠️ Nenhum texto retornado. finish_reason={finish_reason}")
            return "Desculpe, o modelo não conseguiu gerar uma resposta compreensível."

        except Exception as e:
            print(f"❌ [ChatService] Erro ao chamar Gemini: {e}")
            return "Desculpe, houve um erro ao processar sua mensagem."
