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
    # MATERIAS DO SIMULADO
    # -------------------------
    @staticmethod
    def vincular_materias(cod_simulado: int, cod_materias: list[int]):
        """Vincula uma lista de matérias a um simulado existente."""
        simulado = Simulado.query.get(cod_simulado)
        if not simulado:
            return {"erro": "Simulado não encontrado."}

        if not cod_materias:
            return {"erro": "Nenhuma matéria informada."}

        materias = Materia.query.filter(Materia.cod_materia.in_(cod_materias)).all()
        if not materias:
            return {"erro": "Nenhuma matéria válida encontrada."}

        simulado.materias = materias
        db.session.commit()

        return {
            "mensagem": f"{len(materias)} matéria(s) vinculada(s) com sucesso.",
            "cod_simulado": simulado.cod_simulado,
            "materias_vinculadas": [m.to_dict() for m in materias],
        }

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
        dados = SimuladoService.listar_resultados_por_usuario(cod_usuario)
        if not dados:
                return jsonify({"mensagem": "Nenhum resultado encontrado para este usuário."}), 404
        return jsonify(dados), 200

        """Retorna resultados de um usuário filtrados por simulado e/ou matéria."""
        try:
            cod_simulado = request.args.get("cod_simulado", type=int)
            cod_materia = request.args.get("cod_materia", type=int)

            resultados = SimuladoService.listar_resultados_filtrados(
                cod_usuario=cod_usuario,
                cod_simulado=cod_simulado,
                cod_materia=cod_materia
            )

            if not resultados:
                return jsonify({"mensagem": "Nenhum resultado encontrado com esses filtros."}), 404
            return jsonify(resultados), 200

        except Exception as e:
            print(f"❌ Erro em listar_resultados_filtrados: {e}")
            return jsonify({"erro": "Erro interno ao buscar resultados filtrados."}), 500