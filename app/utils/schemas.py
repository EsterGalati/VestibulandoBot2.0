from app.models import Usuario, QuestaoENEM


def usuario_to_dict(u: Usuario) -> dict[str, object]:
    return {"id": u.id, "email": u.email}


def questao_to_dict(q: QuestaoENEM) -> dict[str, object]:
    return {
        "id": q.id,
        "ano": q.ano,
        "pergunta": q.pergunta,
        "alternativas": {
            "A": q.opcao_a,
            "B": q.opcao_b,
            "C": q.opcao_c,
            "D": q.opcao_d,
            "E": q.opcao_e,
        },
    }
