from app.services.rag_memoria import rag
import os
import google.generativeai as genai


class ChatService:

    @staticmethod
    def gerar_resposta(message: str) -> str:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY não configurada")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        #Buscar contexto local via RAG
        try:
            contexto = rag.buscar(message)
        except Exception as e:
            print(f"⚠️ Erro no RAG: {e}")
            contexto = ""

        if contexto.strip() == "":
            return "Nenhuma informação sobre isso foi encontrada nos documentos."

        prompt = f"""
Você é uma assistente de estudos para o ENEM. 
Responda em até um parágrafo curto, em português do Brasil, 
Não utilize asteriscos para deixar a resposta em negrito

USE EXCLUSIVAMENTE O CONTEXTO ABAIXO para responder a pergunta.
Se a resposta não estiver no contexto, diga APENAS:
"Nenhuma informação sobre isso foi encontrada nos documentos."

### CONTEXTO (selecionado pelo RAG):
{contexto}

### PERGUNTA DO ALUNO:
{message}

### RESPOSTA:
"""

        try:
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 1028,
                }
            )

            # Extrair a resposta gerada
            for cand in response.candidates:
                parts = [p.text for p in cand.content.parts if hasattr(p, "text")]
                if parts:
                    return "\n".join(parts)

            return "Não consegui gerar uma resposta útil."

        except Exception as e:
            print(f"❌ Erro no Gemini: {e}")
            return "Erro ao gerar a resposta."
