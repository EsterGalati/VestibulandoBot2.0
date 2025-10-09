from __future__ import annotations

from app.models.usuario import Usuario
from app.models.materia import Materia
from app.models.questao import QuestaoENEM
from app.models.questao_alternativa import QuestaoAlternativa
from app.models.resposta import Resposta
from app.models.simulado import Simulado
from app.models.simulado_questao import SimuladoQuestao
from app.models.resultado_simulado import ResultadoSimulado

__all__ = [
    "Usuario",
    "Materia",
    "QuestaoENEM",
    "QuestaoAlternativa",
    "Resposta",
    "Simulado",
    "SimuladoQuestao",
    "ResultadoSimulado",
]
