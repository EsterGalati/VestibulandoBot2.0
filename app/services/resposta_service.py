from app.extensions import db
from app.models.resposta import Resposta
from app.models.questao import QuestaoENEM
from app.models.questao_alternativa import QuestaoAlternativa


class RespostaService:
    """Serviço para gerenciar respostas dos alunos."""

    @staticmethod
    def listar_todas():
        respostas = Resposta.query.all()
        return [r.to_dict() for r in respostas]

    @staticmethod
    def buscar_por_id(cod_resposta: int):
        resposta = Resposta.query.get(cod_resposta)
        return resposta.to_dict() if resposta else None

    @staticmethod
    def registrar(dados: dict):
        """
        Registra (ou atualiza) a resposta do usuário.
        Espera:
        {
          "cod_usuario": 1,
          "cod_questao": 10,
          "cod_alternativa": 55
        }
        """
        cod_usuario = dados.get("cod_usuario")
        cod_questao = dados.get("cod_questao")
        cod_alternativa = dados.get("cod_alternativa")

        if not all([cod_usuario, cod_questao, cod_alternativa]):
            raise ValueError("Campos obrigatórios: cod_usuario, cod_questao e cod_alternativa.")

        questao = QuestaoENEM.query.get(cod_questao)
        alternativa = QuestaoAlternativa.query.get(cod_alternativa)

        if not questao:
            raise ValueError("Questão não encontrada.")
        if not alternativa:
            raise ValueError("Alternativa não encontrada.")

        # Determinar acerto
        st_acerto = "S" if alternativa.tx_letra.upper() == questao.tx_resposta_correta.upper() else "N"

        # Buscar se o usuário já respondeu essa questão
        resposta = Resposta.query.filter_by(cod_usuario=cod_usuario, cod_questao=cod_questao).first()
        if resposta:
            resposta.cod_alternativa = cod_alternativa
            resposta.st_acerto = st_acerto
        else:
            resposta = Resposta(
                cod_usuario=cod_usuario,
                cod_questao=cod_questao,
                cod_alternativa=cod_alternativa,
                st_acerto=st_acerto
            )
            db.session.add(resposta)

        db.session.commit()
        return resposta.to_dict()

    @staticmethod
    def deletar(cod_resposta: int):
        resposta = Resposta.query.get(cod_resposta)
        if not resposta:
            return None
        db.session.delete(resposta)
        db.session.commit()
        return {"mensagem": f"Resposta {cod_resposta} excluída com sucesso."}
