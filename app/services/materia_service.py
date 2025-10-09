from app.extensions import db
from app.models import Materia


class MateriaService:
    """Serviço de regras de negócio para a tabela TB_MATERIA."""

    @staticmethod
    def listar_todas():
        return Materia.query.order_by(Materia.nome_materia.asc()).all()

    @staticmethod
    def buscar_por_id(cod_materia: int):
        return Materia.query.get(cod_materia)

    @staticmethod
    def criar(nome_materia: str) -> Materia:
        nova = Materia(nome_materia=nome_materia.strip())
        db.session.add(nova)
        db.session.commit()
        return nova

    @staticmethod
    def atualizar(cod_materia: int, nome_materia: str):
        materia = Materia.query.get(cod_materia)
        if not materia:
            return None
        materia.nome_materia = nome_materia.strip()
        db.session.commit()
        return materia

    @staticmethod
    def deletar(cod_materia: int) -> bool:
        materia = Materia.query.get(cod_materia)
        if not materia:
            return False
        db.session.delete(materia)
        db.session.commit()
        return True
