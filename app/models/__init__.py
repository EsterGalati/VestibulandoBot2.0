# app/models/__init__.py
"""
Módulo agregador dos modelos.

Permite fazer:
    from app.models import Usuario, QuestaoENEM, ResultadoUsuario
"""

from __future__ import annotations

# importa explicitamente os modelos para facilitar uso
from .usuario import Usuario
from .questao import QuestaoENEM
from .resultado import ResultadoUsuario

# controla o que é exposto no import *
__all__ = ["Usuario", "QuestaoENEM", "ResultadoUsuario"]
