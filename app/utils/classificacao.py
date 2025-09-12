# app/utils/classificacao.py
from __future__ import annotations

import unicodedata
from collections import Counter
from typing import Dict, List


class ClassificadorAssunto:
    """Classificador simples de questões ENEM por área usando palavras-chave."""

    KEYWORDS: Dict[str, List[str]] = {
        "Matemática": [
            "função", "equação", "logaritmo", "derivada",
            "probabilidade", "estatística", "porcentagem",
            "geometria", "polígono", "triângulo", "reta", "ângulo",
        ],
        "Física": [
            "velocidade", "aceleração", "força", "energia",
            "trabalho", "cinemática", "dinâmica",
            "eletricidade", "campo elétrico", "óptica",
        ],
        "Química": [
            "mol", "reação", "ácido", "base", "equilíbrio", "estequiometria",
        ],
        "Biologia": [
            "DNA", "RNA", "célula", "ecologia", "evolução", "fotossíntese",
        ],
        "História": [
            "imperialismo", "revolução", "ditadura", "colonização", "iluminismo",
        ],
        "Geografia": [
            "clima", "relevo", "hidrografia", "urbanização", "globalização",
        ],
        "Linguagens": [
            "interpretação", "figura de linguagem", "semântica", "conotação", "denotação",
        ],
    }

    # keywords normalizadas (sem acento/minúsculas) pré-computadas
    _NORMALIZED: Dict[str, List[str]] = {
        area: [unicodedata.normalize("NFKD", w)
               .encode("ascii", "ignore")
               .decode("ascii")
               .lower()
               for w in palavras]
        for area, palavras in KEYWORDS.items()
    }

    @staticmethod
    def _normalize(texto: str) -> str:
        """Remove acentos e converte para minúsculas."""
        return (
            unicodedata.normalize("NFKD", texto)
            .encode("ascii", "ignore")
            .decode("ascii")
            .lower()
        )

    @classmethod
    def classificar(cls, texto: str) -> str:
        """
        Retorna o nome da área mais provável, ou 'Outros' se não houver match.
        """
        if not texto:
            return "Outros"

        texto_norm = cls._normalize(texto)
        score = Counter()
        for area, palavras in cls._NORMALIZED.items():
            score[area] = sum(1 for p in palavras if p in texto_norm)

        area, pontos = score.most_common(1)[0]
        return area if pontos > 0 else "Outros"


# Atalho para uso direto (mantém compatibilidade)
def classificar_assunto(texto: str) -> str:
    return ClassificadorAssunto.classificar(texto)
