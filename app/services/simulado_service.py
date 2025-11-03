from datetime import datetime
from app.extensions import db
from sqlalchemy.orm import joinedload
from app.models import Simulado, SimuladoMateria, SimuladoQuestao, ResultadoSimulado, QuestaoENEM, Materia

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
        """Cria um novo simulado e vincula matérias via tabela associativa."""
        from app.models.simulado_materia import SimuladoMateria

        cod_materias = dados.get("cod_materias", [])

        sim = Simulado(
            titulo=dados["titulo"].strip(),
            descricao=dados.get("descricao", "").strip(),
            ativo=bool(dados.get("ativo", True)),
        )

        db.session.add(sim)
        db.session.flush()

        for cod_materia in cod_materias:
            db.session.add(
                SimuladoMateria(
                    cod_simulado=sim.cod_simulado,
                    cod_materia=cod_materia
                )
            )

        db.session.commit()

        return {
            "cod_simulado": sim.cod_simulado,
            "materias_vinculadas": len(cod_materias),
            "mensagem": "Simulado criado com sucesso."
        }

    @staticmethod
    def atualizar_simulado(cod_simulado: int, dados: dict):
        sim = Simulado.query.get(cod_simulado)
        if not sim:
            return None

        sim.titulo = dados.get("titulo", sim.titulo).strip()
        sim.descricao = dados.get("descricao", sim.descricao).strip()
        sim.ativo = bool(dados.get("ativo", sim.ativo))
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
        return questoes

    # -------------------------
    # RESULTADOS
    # -------------------------
    @staticmethod
    def registrar_resultado(cod_simulado: int, dados: dict):
        """Registra o resultado de um simulado."""
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
        resultados = ResultadoSimulado.query.filter_by(cod_simulado=cod_simulado).all()
        return [r.to_dict() for r in resultados]

    @staticmethod
    def listar_resultados_por_usuario(cod_usuario: int):
        """
        Retorna os resultados do usuário já com dados do simulado
        e suas matérias para permitir filtro no front.
        """
        resultados = (
            ResultadoSimulado.query
            .filter(ResultadoSimulado.cod_usuario == cod_usuario)
            .options(
                joinedload(ResultadoSimulado.simulado)
                .joinedload(Simulado.materias)  # carrega materias
            )
            .order_by(ResultadoSimulado.dt_finalizacao.desc())
            .all()
        )

        payload = []
        for r in resultados:
            sim = r.simulado
            materias = sim.materias if sim else []
            payload.append({
                "cod_resultado": r.cod_resultado,
                "cod_usuario": r.cod_usuario,
                "cod_simulado": r.cod_simulado,
                "qtd_acertos": r.qtd_acertos,
                "qtd_erros": r.qtd_erros,
                "nota_final": r.nota_final,
                "dt_finalizacao": r.dt_finalizacao.isoformat() if r.dt_finalizacao else None,
                "simulado": {
                    "cod_simulado": sim.cod_simulado if sim else None,
                    "titulo": sim.titulo if sim else None,
                    "descricao": sim.descricao if sim else None,
                    "cod_materias": [m.cod_materia for m in materias],
                    "nomes_materias": [m.nome_materia for m in materias],
                }
            })
        return payload
        """
        Lista os resultados de um usuário, com filtros opcionais por simulado e matéria.
        - cod_simulado: retorna resultados apenas desse simulado
        - cod_materia: retorna resultados apenas de simulados que incluam essa matéria
        """
        query = db.session.query(ResultadoSimulado).join(Simulado).filter(ResultadoSimulado.cod_usuario == cod_usuario)

        # 🔹 Filtro por simulado
        if cod_simulado:
            query = query.filter(ResultadoSimulado.cod_simulado == cod_simulado)

        # 🔹 Filtro por matéria (via relação N:N)
        if cod_materia:
            query = query.join(SimuladoMateria, SimuladoMateria.cod_simulado == Simulado.cod_simulado)
            query = query.filter(SimuladoMateria.cod_materia == cod_materia)

        resultados = query.order_by(ResultadoSimulado.dt_finalizacao.desc()).all()

        return [
            {
                **r.to_dict(),
                "titulo_simulado": r.simulado.titulo if r.simulado else None,
                "materias": [m.nome_materia for m in r.simulado.materias] if r.simulado else [],
            }
            for r in resultados
        ]