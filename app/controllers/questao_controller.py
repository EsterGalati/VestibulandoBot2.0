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

    @staticmethod
    def importar_enem_url():
        dados = request.get_json()
        anos = dados.get("anos")
        materias = dados.get("materias") # Lista de códigos de matéria

        if not anos or not isinstance(anos, list) or not anos:
            return jsonify({"erro": "Lista de anos é obrigatória"}), 400
        
        if not materias or not isinstance(materias, list) or not materias:
            return jsonify({"erro": "Lista de matérias é obrigatória"}), 400

        resultados = []
        for ano in anos:
            try:
                resultado = QuestaoService.importar_enem(int(ano), materias)
                resultados.append(resultado)
            except Exception as e:
                resultados.append({"status": "erro", "ano": ano, "mensagem": f"Erro ao importar questões do ENEM {ano}: {str(e)}"})

        return jsonify(resultados), 200