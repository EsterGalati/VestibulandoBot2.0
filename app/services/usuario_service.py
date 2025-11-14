from typing import Optional, List, Dict
from flask_login import current_user
from sqlalchemy.orm import selectinload
from app.models.usuario import Usuario
from app.models.rel_prof_aluno import RelProfAluno
from app.models.resultado_simulado import ResultadoSimulado
from app.models.simulado import Simulado
from app.models.materia import Materia
from app.extensions import db
import re
from sqlalchemy.exc import IntegrityError

class UsuarioService:
    """Serviço para operações relacionadas a usuários."""

    @staticmethod
    def get_todos_usuarios_com_resultados() -> List[Dict]:
        query = (
            Usuario.query.options(
                selectinload(Usuario.resultados_simulados)
                    .selectinload(ResultadoSimulado.simulado)
                    .selectinload(Simulado.materias)
            )
            .order_by(Usuario.cod_usuario)
        )

        out: List[Dict] = []
        for u in query.all():
            u_dict = u.to_dict()
            resultados = []

            for r in u.resultados_simulados:
                sim = r.simulado
                resultados.append({
                    **r.to_dict(),
                    "simulado": sim.to_dict(incluir_questoes=False),
                    "materias": [m.to_dict() for m in (sim.materias or [])]
                })

            u_dict["resultados_simulados"] = resultados
            out.append(u_dict)

        return out

    @staticmethod
    def get_usuario_logado() -> Optional[Dict]:
        if current_user and getattr(current_user, "is_authenticated", False):
            try:
                return current_user.to_dict()
            except Exception:
                return {
                    "cod_usuario": getattr(current_user, "cod_usuario", None),
                    "nome_usuario": getattr(current_user, "nome_usuario", None),
                    "email": getattr(current_user, "email", None),
                    "is_admin": bool(getattr(current_user, "is_admin", False)),
                }
        return None

    @staticmethod
    def get_usuario_por_id(cod_usuario: int) -> Optional[Dict]:
        usuario = Usuario.query.get(cod_usuario)
        if not usuario:
            return None
        return usuario.to_dict()

    @staticmethod
    def get_alunos_do_professor(cod_professor: int) -> List[Dict]:
        """
        Retorna todos os alunos vinculados a um professor com:
        - resultados_simulados
        - simulado de cada resultado
        - materias do simulado
        """
        query = (
            db.session.query(Usuario)
            .join(RelProfAluno, Usuario.cod_usuario == RelProfAluno.cod_usuario_aluno)
            .filter(RelProfAluno.cod_usuario_prof == cod_professor)
            .options(
                selectinload(Usuario.resultados_simulados)
                    .selectinload(ResultadoSimulado.simulado)
                    .selectinload(Simulado.materias)
            )
            .order_by(Usuario.nome_usuario)
        )

        alunos_out: List[Dict] = []
        for aluno in query.distinct(Usuario.cod_usuario).all():
            a_dict = aluno.to_dict()
            resultados = []
            for r in aluno.resultados_simulados:
                sim = r.simulado
                resultados.append({
                    **r.to_dict(),
                    "simulado": sim.to_dict(incluir_questoes=False),
                    "materias": [m.to_dict() for m in (sim.materias or [])],
                })
            a_dict["resultados_simulados"] = resultados
            alunos_out.append(a_dict)

        return alunos_out
    
    @staticmethod
    def associar_alunos_ao_professor(cod_professor: int) -> Dict:
        """
        Associa automaticamente alunos a um professor específico (IDs 2 a 6),
        conforme o mapeamento fixo baseado no CSV original.
        """

        # 🔹 Mapeamento fixo (como o CSV)
        MAPEAMENTO = {
            2: list(range(7, 22)),   # 7–21
            3: list(range(22, 37)),  # 22–36
            4: list(range(37, 52)),  # 37–51
            5: list(range(52, 67)),  # 52–66
            6: list(range(67, 82)),  # 67–81
        }

        if cod_professor not in MAPEAMENTO:
            return {"erro": f"O professor {cod_professor} não está no mapeamento (válidos: 2–6)."}

        alunos_ids = MAPEAMENTO[cod_professor]
        total_inseridos = 0

        for aluno_id in alunos_ids:
            existe = (
                db.session.query(RelProfAluno)
                .filter_by(cod_usuario_prof=cod_professor, cod_usuario_aluno=aluno_id)
                .first()
            )
            if not existe:
                db.session.add(
                    RelProfAluno(
                        cod_usuario_prof=cod_professor,
                        cod_usuario_aluno=aluno_id,
                    )
                )
                total_inseridos += 1

        db.session.commit()

        return {
            "mensagem": f"✅ {total_inseridos} alunos associados ao professor {cod_professor}.",
            "professor": cod_professor,
            "alunos_associados": alunos_ids,
        }

    _email_re = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

    @staticmethod
    def _validar_email(email: str) -> bool:
        return bool(email and UsuarioService._email_re.match(email))

    @staticmethod
    def _buscar_por_id(cod_usuario: int) -> Optional[Usuario]:
        return Usuario.query.get(cod_usuario)

    @staticmethod
    def _email_em_uso(email: str, ignorar_id: Optional[int] = None) -> bool:
        q = Usuario.query.filter(Usuario.email.ilike(email))
        if ignorar_id:
            q = q.filter(Usuario.cod_usuario != ignorar_id)
        return db.session.query(q.exists()).scalar()

    @staticmethod
    def atualizar_perfil(*, target_id: int, nome: str, email: str) -> Dict:
        nome  = (nome or "").strip()
        email = (email or "").strip().lower()

        if not nome:
            return {"erro": "Nome é obrigatório."}
        if not UsuarioService._validar_email(email):
            return {"erro": "E-mail inválido."}
        if UsuarioService._email_em_uso(email, ignorar_id=target_id):
            return {"erro": "E-mail já está em uso por outro usuário."}

        usuario = UsuarioService._buscar_por_id(target_id)
        if not usuario:
            return {"erro": "Usuário não encontrado."}

        if hasattr(usuario, "nome"):
            usuario.nome = nome
        if hasattr(usuario, "nome_usuario"):
            usuario.nome_usuario = nome
        usuario.email = email

        try:
            db.session.add(usuario)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"erro": "Conflito de dados ao salvar (integridade)."}
        except Exception as e:
            db.session.rollback()
            return {"erro": f"Erro inesperado ao salvar: {e}"}

        try:
            return usuario.to_dict()
        except Exception:
            return {
                "cod_usuario": getattr(usuario, "cod_usuario", None),
                "nome_usuario": getattr(usuario, "nome_usuario", None) or getattr(usuario, "nome", None),
                "email": getattr(usuario, "email", None),
                "is_admin": bool(getattr(usuario, "is_admin", False)),
            }