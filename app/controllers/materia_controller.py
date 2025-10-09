from flask import jsonify, request
from app.services.materia_service import MateriaService


class MateriaController:
    """Controller responsável por lidar com as requisições HTTP de Matéria."""

    @staticmethod
    def listar_todas():
        materias = MateriaService.listar_todas()
        return jsonify([m.to_dict() for m in materias]), 200

    @staticmethod
    def buscar_por_id(cod_materia: int):
        materia = MateriaService.buscar_por_id(cod_materia)
        if not materia:
            return jsonify({"erro": "Matéria não encontrada"}), 404
        return jsonify(materia.to_dict()), 200

    @staticmethod
    def criar():
        data = request.get_json()
        nome = data.get("nome_materia")

        if not nome:
            return jsonify({"erro": "Campo 'nome_materia' é obrigatório."}), 400

        materia = MateriaService.criar(nome)
        return jsonify(materia.to_dict()), 201

    @staticmethod
    def atualizar(cod_materia: int):
        data = request.get_json()
        nome = data.get("nome_materia")

        if not nome:
            return jsonify({"erro": "Campo 'nome_materia' é obrigatório."}), 400

        materia = MateriaService.atualizar(cod_materia, nome)
        if not materia:
            return jsonify({"erro": "Matéria não encontrada"}), 404
        return jsonify(materia.to_dict()), 200

    @staticmethod
    def deletar(cod_materia: int):
        sucesso = MateriaService.deletar(cod_materia)
        if not sucesso:
            return jsonify({"erro": "Matéria não encontrada"}), 404
        return jsonify({"mensagem": "Matéria removida com sucesso"}), 200
