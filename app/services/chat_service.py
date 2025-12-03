from app.services.rag_service import rag
import os
import google.generativeai as genai


class ChatService:

    # Continua armazenando histórico (se quiser expandir depois)
    historico = []

    @staticmethod
    def _registrar_historico(papel: str, conteudo: str):

        ChatService.historico.append({"papel": papel, "conteudo": conteudo})

        if len(ChatService.historico) > 10:
            ChatService.historico.pop(0)

    @staticmethod
    def _pegar_ultimo_historico():

        if len(ChatService.historico) < 2:
            return "Nenhum histórico relevante disponível."


        ultimo = ChatService.historico[-1]
        penultimo = ChatService.historico[-2]

        return f"{penultimo['papel'].upper()}: {penultimo['conteudo']}\n{ultimo['papel'].upper()}: {ultimo['conteudo']}"

    @staticmethod
    def gerar_resposta(message: str) -> str:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY não configurada")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        if not isinstance(message, str):
            try:
                message = str(message)
            except:
                message = "Conteúdo inválido enviado pelo usuário."

        ChatService._registrar_historico("aluno", message)

        # Busca RAG
        try:
            contexto = rag.buscar(message)
        except Exception as e:
            print(f"⚠️ Erro no RAG: {e}")
            contexto = ""


        historico_texto = ChatService._pegar_ultimo_historico()

        prompt = f"""

Você é um assistente de estudos para o ENEM.
        
IMPORTANTE:
A mensagem recebida pode não ser sempre uma string simples. Antes de responder,
verifique internamente se a PERGUNTA DO ALUNO é realmente texto utilizável.
Caso a pergunta venha como objeto, lista, dicionário ou qualquer outro tipo,
interprete o conteúdo textual presente e desconsidere estruturas inválidas.

Sua tarefa é analisar cuidadosamente o CONTEXTO fornecido pelo RAG e a PERGUNTA do aluno, aplicando as regras abaixo:

1. Verifique se o contexto é realmente relevante para a pergunta.
   - O contexto é relevante SOMENTE se ele realmente ajudar a responder a pergunta do aluno.
   - Se o contexto não tiver relação, for muito genérico ou não ajudar na resposta:
     → IGNORE completamente o contexto.

2. Se o contexto for relevante:
   - Utilize o conteúdo do contexto como base principal da resposta.
   - Em seguida, busque informações adicionais na internet para complementar e enriquecer a resposta.
   - Adicione ao final:
     "As informações adicionais vieram de fora dos nossos documentos: [URL]"

3. Se o contexto NÃO for relevante:
   - Ignore totalmente o contexto.
   - Busque diretamente na internet uma resposta completa e bem explicada em no máximo um parágrafo.
   - No final, escreva:
     "As informações acima vieram de fora dos nossos documentos: [URL]"

4. Regras de estilo da resposta:
   - Responda SEM usar asteriscos.
   - Texto claro, direto e curto.
   - Sempre em português do Brasil.
   - Separe com uma linha a parte onde a URL será colocada.

### ÚLTIMO HISTÓRICO:
{historico_texto}

### CONTEXTO DO RAG:
{contexto}

### PERGUNTA ATUAL:
{message}

### RESPOSTA:
"""

        try:
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 2056,
                }
            )

            for cand in response.candidates:
                parts = [p.text for p in cand.content.parts if hasattr(p, "text")]
                if parts:
                    resposta_final = "\n".join(parts)

                    ChatService._registrar_historico("assistente", resposta_final)

                    return resposta_final

            return "Não consegui gerar uma resposta no momento. Tente reformular sua pergunta."

        except Exception as e:
            print(f"❌ Erro no Gemini: {e}")
            return "Erro ao gerar a resposta."
