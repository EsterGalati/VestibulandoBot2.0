import unicodedata
from collections import Counter

KEYWORDS = {
    "Matemática": [
        "função",
        "equação",
        "logaritmo",
        "derivada",
        "probabilidade",
        "estatística",
        "porcentagem",
        "geometria",
        "polígono",
        "triângulo",
        "reta",
        "ângulo",
    ],
    "Física": [
        "velocidade",
        "aceleração",
        "força",
        "energia",
        "trabalho",
        "cinemática",
        "dinâmica",
        "eletricidade",
        "campo elétrico",
        "óptica",
    ],
    "Química": [
        "mol",
        "reação",
        "ácido",
        "base",
        "equilíbrio",
        "estequiometria",
    ],
    "Biologia": [
        "DNA",
        "RNA",
        "célula",
        "ecologia",
        "evolução",
        "fotossíntese",
    ],
    "História": [
        "imperialismo",
        "revolução",
        "ditadura",
        "colonização",
        "iluminismo",
    ],
    "Geografia": [
        "clima",
        "relevo",
        "hidrografia",
        "urbanização",
        "globalização",
    ],
    "Linguagens": [
        "interpretação",
        "figura de linguagem",
        "semântica",
        "conotação",
        "denotação",
    ],
}


def _normalize(s: str) -> str:
    # remove acentos e baixa caixa
    return (
        unicodedata.normalize("NFKD", s)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )


# pré-processa keywords normalizadas
_NKEYS = {area: [_normalize(w) for w in ws] for area, ws in KEYWORDS.items()}


def classificar_assunto(texto: str) -> str:
    if not texto:
        return "Outros"
    t = _normalize(texto)
    score = Counter()
    for area, palavras in _NKEYS.items():
        score[area] = sum(1 for p in palavras if p in t)
    area, pontos = score.most_common(1)[0]
    return area if pontos > 0 else "Outros"
