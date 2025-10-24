from __future__ import annotations

from app.models.simulado_materia import SimuladoMateria
from app.models.usuario import Usuario
from app.models.materia import Materia
from app.models.questao import QuestaoENEM
from app.models.questao_alternativa import QuestaoAlternativa
from app.models.simulado import Simulado
from app.models.simulado_questao import SimuladoQuestao
from app.models.resultado_simulado import ResultadoSimulado
from app.models.rel_prof_aluno import RelProfAluno  # se existir

__all__ = [
    "SimuladoMateria",
    "Usuario",
    "Materia",
    "QuestaoENEM",
    "QuestaoAlternativa",
    "Simulado",
    "SimuladoQuestao",
    "ResultadoSimulado",
    "RelProfAluno",
]
