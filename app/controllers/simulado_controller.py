from flask import jsonify, request
from app.services.simulado_service import SimuladoService


class SimuladoController:
    """Controller unificado para Simulado, Questões do Simulado e Resultados."""

    # -------------------------
    # SIMULADOS
    # -------------------------
    @staticmethod
    def listar():
        simulados = SimuladoService.listar_todos()
        return jsonify(simulados), 200

    @staticmethod
    def buscar(cod_simulado):
        simulado = SimuladoService.buscar_por_id(cod_simulado)
        if not simulado:
            return jsonify({"erro": "Simulado não encontrado."}), 404
        return jsonify(simulado), 200

    @staticmethod
    def criar():
        dados = request.get_json()
        criado = SimuladoService.criar_simulado(dados)
        return jsonify(criado), 201

    @staticmethod
    def atualizar(cod_simulado):
        dados = request.get_json()
        atualizado = SimuladoService.atualizar_simulado(cod_simulado, dados)
        if not atualizado:
            return jsonify({"erro": "Simulado não encontrado."}), 404
        return jsonify(atualizado), 200

    @staticmethod
    def deletar(cod_simulado):
        deletado = SimuladoService.deletar_simulado(cod_simulado)
        if not deletado:
            return jsonify({"erro": "Simulado não encontrado."}), 404
        return jsonify(deletado), 200

    # -------------------------
    # QUESTÕES DO SIMULADO
    # -------------------------
    @staticmethod
    def adicionar_questao(cod_simulado):
        dados = request.get_json()
        adicionado = SimuladoService.adicionar_questao(cod_simulado, dados)
        return jsonify(adicionado), 201

    @staticmethod
    def listar_questoes(cod_simulado):
        questoes = SimuladoService.listar_questoes(cod_simulado)
        return jsonify(questoes), 200

    # -------------------------
    # RESULTADOS
    # -------------------------
    @staticmethod
    def registrar_resultado(cod_simulado):
        dados = request.get_json()
        registrado = SimuladoService.registrar_resultado(cod_simulado, dados)
        return jsonify(registrado), 201

    @staticmethod
    def listar_resultados(cod_simulado):
        resultados = SimuladoService.listar_resultados(cod_simulado)
        return jsonify(resultados), 200
    
    @staticmethod
    def listar_resultados_por_usuario(cod_usuario):
        from app.services.simulado_service import SimuladoService
        resultados = SimuladoService.listar_resultados_por_usuario(cod_usuario)
        if not resultados:
            return {"mensagem": "Nenhum resultado encontrado para este usuário."}, 404
        return resultados, 200

