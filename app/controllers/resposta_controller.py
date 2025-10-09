from flask import jsonify, request
from app.services.resposta_service import RespostaService


class RespostaController:
    """Camada de controle para as respostas dos alunos."""

    @staticmethod
    def listar():
        respostas = RespostaService.listar_todas()
        return jsonify(respostas), 200

    @staticmethod
    def buscar(cod_resposta):
        r = RespostaService.buscar_por_id(cod_resposta)
        if not r:
            return jsonify({"erro": "Resposta não encontrada."}), 404
        return jsonify(r), 200

    @staticmethod
    def registrar():
        try:
            dados = request.get_json()
            r = RespostaService.registrar(dados)
            return jsonify({
                "mensagem": "Resposta registrada com sucesso.",
                "dados": r
            }), 201
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400
        except Exception as e:
            return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

    @staticmethod
    def deletar(cod_resposta):
        r = RespostaService.deletar(cod_resposta)
        if not r:
            return jsonify({"erro": "Resposta não encontrada."}), 404
        return jsonify(r), 200
