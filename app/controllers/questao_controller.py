from flask import jsonify, request
from app.services.questao_service import QuestaoService


class QuestaoController:
    """Camada de controle das questões e alternativas."""

    @staticmethod
    def listar():
        questoes = QuestaoService.listar_todas()
        return jsonify(questoes), 200

    @staticmethod
    def listar_por_materia(cod_materia):
        """Lista questões filtradas por matéria."""
        questoes = QuestaoService.listar_por_materia(cod_materia)
        if not questoes:
            return jsonify([]), 200  # devolve lista vazia em vez de 404
        return jsonify(questoes), 200

    @staticmethod
    def buscar(cod_questao):
        questao = QuestaoService.buscar_por_id(cod_questao)
        if not questao:
            return jsonify({"erro": "Questão não encontrada."}), 404
        return jsonify(questao), 200

    @staticmethod
    def criar():
        dados = request.get_json()
        criado = QuestaoService.criar(dados)
        return jsonify(criado), 201

    @staticmethod
    def atualizar(cod_questao):
        dados = request.get_json()
        atualizado = QuestaoService.atualizar(cod_questao, dados)
        if not atualizado:
            return jsonify({"erro": "Questão não encontrada."}), 404
        return jsonify(atualizado), 200

    @staticmethod
    def deletar(cod_questao):
        deletado = QuestaoService.deletar(cod_questao)
        if not deletado:
            return jsonify({"erro": "Questão não encontrada."}), 404
        return jsonify(deletado), 200
