from app.extensions import db
from app.models.questao import QuestaoENEM
from app.models.questao_alternativa import QuestaoAlternativa


class QuestaoService:
    """Serviço para manipular questões e alternativas."""

    @staticmethod
    def listar_todas():
        """Retorna todas as questões com alternativas."""
        questoes = QuestaoENEM.query.all()
        return QuestaoService._formatar_lista(questoes)

    @staticmethod
    def listar_por_materia(cod_materia: int):
        """Retorna as questões filtradas por matéria."""
        questoes = QuestaoENEM.query.filter_by(cod_materia=cod_materia).all()
        return QuestaoService._formatar_lista(questoes)

    @staticmethod
    def _formatar_lista(questoes):
        """Formata lista de questões com alternativas."""
        resultado = []
        for q in questoes:
            resultado.append({
                "cod_questao": q.cod_questao,
                "tx_questao": q.tx_questao,
                "cod_materia": q.cod_materia,
                "ano_questao": q.ano_questao,
                "tx_resposta_correta": q.tx_resposta_correta,
                "alternativas": [
                    {
                        "cod_alternativa": alt.cod_alternativa,
                        "tx_letra": alt.tx_letra,
                        "tx_texto": alt.tx_texto
                    } for alt in q.alternativas
                ]
            })
        return resultado

    @staticmethod
    def buscar_por_id(cod_questao: int):
        """Busca uma questão específica com suas alternativas."""
        questao = QuestaoENEM.query.get(cod_questao)
        if not questao:
            return None
        return {
            "cod_questao": questao.cod_questao,
            "tx_questao": questao.tx_questao,
            "cod_materia": questao.cod_materia,
            "ano_questao": questao.ano_questao,
            "tx_resposta_correta": questao.tx_resposta_correta,
            "alternativas": [
                {
                    "cod_alternativa": a.cod_alternativa,
                    "tx_letra": a.tx_letra,
                    "tx_texto": a.tx_texto
                } for a in questao.alternativas
            ]
        }

    @staticmethod
    def criar(dados: dict):
        """Cria uma nova questão com alternativas."""
        q = QuestaoENEM(
            tx_questao=dados["tx_questao"].strip(),
            cod_materia=int(dados["cod_materia"]),
            ano_questao=int(dados["ano_questao"]),
            tx_resposta_correta=dados["tx_resposta_correta"].upper().strip(),
        )
        db.session.add(q)
        db.session.flush()

        for alt in dados.get("alternativas", []):
            nova_alt = QuestaoAlternativa(
                cod_questao=q.cod_questao,
                tx_letra=alt["tx_letra"].upper(),
                tx_texto=alt["tx_texto"].strip(),
            )
            db.session.add(nova_alt)

        db.session.commit()
        return {"cod_questao": q.cod_questao}

    @staticmethod
    def atualizar(cod_questao: int, dados: dict):
        """Atualiza os dados de uma questão e suas alternativas."""
        questao = QuestaoENEM.query.get(cod_questao)
        if not questao:
            return None

        questao.tx_questao = dados.get("tx_questao", questao.tx_questao)
        questao.cod_materia = int(dados.get("cod_materia", questao.cod_materia))
        questao.ano_questao = int(dados.get("ano_questao", questao.ano_questao))
        questao.tx_resposta_correta = dados.get(
            "tx_resposta_correta", questao.tx_resposta_correta
        ).upper()

        if "alternativas" in dados:
            QuestaoAlternativa.query.filter_by(cod_questao=questao.cod_questao).delete()
            for alt in dados["alternativas"]:
                db.session.add(
                    QuestaoAlternativa(
                        cod_questao=questao.cod_questao,
                        tx_letra=alt["tx_letra"].upper(),
                        tx_texto=alt["tx_texto"].strip(),
                    )
                )

        db.session.commit()
        return {"cod_questao": questao.cod_questao, "mensagem": "Questão atualizada com sucesso."}

    @staticmethod
    def deletar(cod_questao: int):
        """Remove uma questão e suas alternativas."""
        questao = QuestaoENEM.query.get(cod_questao)
        if not questao:
            return None
        QuestaoAlternativa.query.filter_by(cod_questao=cod_questao).delete()
        db.session.delete(questao)
        db.session.commit()
        return {"mensagem": f"Questão {cod_questao} removida com sucesso."}
