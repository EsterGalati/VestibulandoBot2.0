from datetime import datetime
from app.extensions import db
from app.models import Simulado, SimuladoQuestao, ResultadoSimulado, QuestaoENEM


class SimuladoService:
    """Serviço unificado para Simulado, Questões vinculadas e Resultados."""

    # -------------------------
    # SIMULADOS
    # -------------------------
    @staticmethod
    def listar_todos():
        simulados = Simulado.query.order_by(Simulado.dt_criacao.desc()).all()
        return [s.to_dict(incluir_questoes=True) for s in simulados]

    @staticmethod
    def buscar_por_id(cod_simulado: int):
        simulado = Simulado.query.get(cod_simulado)
        return simulado.to_dict(incluir_questoes=True) if simulado else None

    @staticmethod
    def criar_simulado(dados: dict):
        sim = Simulado(
            titulo=dados["titulo"].strip(),
            descricao=dados.get("descricao", "").strip(),
            ativo=bool(dados.get("ativo", True)),
            cod_materia=dados.get("cod_materia"), 
        )
        db.session.add(sim)
        db.session.commit()
        return {"cod_simulado": sim.cod_simulado, "mensagem": "Simulado criado com sucesso."}

    @staticmethod
    def atualizar_simulado(cod_simulado: int, dados: dict):
        sim = Simulado.query.get(cod_simulado)
        if not sim:
            return None
        sim.titulo = dados.get("titulo", sim.titulo).strip()
        sim.descricao = dados.get("descricao", sim.descricao).strip()
        sim.ativo = bool(dados.get("ativo", sim.ativo))
        sim.cod_materia = dados.get("cod_materia", sim.cod_materia)
        db.session.commit()
        return {"cod_simulado": sim.cod_simulado, "mensagem": "Simulado atualizado com sucesso."}

    @staticmethod
    def deletar_simulado(cod_simulado: int):
        sim = Simulado.query.get(cod_simulado)
        if not sim:
            return None
        db.session.delete(sim)
        db.session.commit()
        return {"mensagem": f"Simulado {cod_simulado} removido com sucesso."}

    # -------------------------
    # QUESTÕES DO SIMULADO
    # -------------------------
    @staticmethod
    def adicionar_questao(cod_simulado: int, dados: dict):
        """Adiciona uma questão ao simulado."""
        cod_questao = int(dados.get("cod_questao"))
        ordem = dados.get("ordem")

        if not QuestaoENEM.query.get(cod_questao):
            return {"erro": "Questão inválida."}

        sq = SimuladoQuestao(cod_simulado=cod_simulado, cod_questao=cod_questao, ordem=ordem)
        db.session.add(sq)
        db.session.commit()
        return {"mensagem": "Questão adicionada ao simulado com sucesso."}

    @staticmethod
    def listar_questoes(cod_simulado: int):
        """Lista todas as questões vinculadas a um simulado."""
        questoes = SimuladoQuestao.listar_por_simulado(cod_simulado)
        return [q.to_dict(incluir_questao=True) for q in questoes]

    # -------------------------
    # RESULTADOS
    # -------------------------
    @staticmethod
    def registrar_resultado(cod_simulado: int, dados: dict):
        """Registra o resultado de um simulado."""
        from app.models import ResultadoSimulado
        from app.extensions import db

        try:
            resultado = ResultadoSimulado(
                cod_simulado=cod_simulado,
                cod_usuario=dados["cod_usuario"],
                qtd_acertos=dados.get("qtd_acertos", 0),
                qtd_erros=dados.get("qtd_erros", 0)
            )

            db.session.add(resultado)
            db.session.commit()

            return {
                "mensagem": "Resultado registrado com sucesso.",
                "cod_resultado": resultado.cod_resultado,
                "cod_simulado": cod_simulado,
                "cod_usuario": dados["cod_usuario"],
                "qtd_acertos": resultado.qtd_acertos,
                "qtd_erros": resultado.qtd_erros
            }

        except Exception as e:
            db.session.rollback()
            return {"erro": f"Falha ao registrar resultado: {str(e)}"}

    @staticmethod
    def listar_resultados(cod_simulado: int):
        """Lista todos os resultados registrados para um simulado."""
        resultados = ResultadoSimulado.query.filter_by(cod_simulado=cod_simulado).all()
        return [r.to_dict() for r in resultados]
    
    @staticmethod
    def listar_resultados_por_usuario(cod_usuario: int):
        """Lista todos os resultados de simulados feitos por um usuário específico."""
        resultados = (
            ResultadoSimulado.query
            .join(Simulado, Simulado.cod_simulado == ResultadoSimulado.cod_simulado)
            .filter(ResultadoSimulado.cod_usuario == cod_usuario)
            .order_by(ResultadoSimulado.cod_resultado.desc())
            .all()
        )
        return [
            {
                **r.to_dict(),
                "titulo_simulado": r.simulado.titulo if r.simulado else None,
                "descricao_simulado": r.simulado.descricao if r.simulado else None,
            }
            for r in resultados
        ]
