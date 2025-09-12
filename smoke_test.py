# smoke_test.py
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from contextlib import contextmanager

# --- GARANTE QUE O PYTHON ENXERGUE O PACOTE "app" ---
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# --- FORÇA DB EM MEMÓRIA ANTES DE IMPORTAR A APP ---
os.environ["ENV"] = "dev"
os.environ["DATABASE_URL"] = "sqlite://"  # override da URI do .env para testes

from app import create_app
from app.extensions import db
from app.models import QuestaoENEM, Usuario


@contextmanager
def test_app():
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_ENABLED=False,
        SESSION_COOKIE_SECURE=False,
        SESSION_COOKIE_SAMESITE="Lax",
    )
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def jprint(resp):
    try:
        return json.dumps(resp.get_json(), ensure_ascii=False, indent=2)
    except Exception:
        return resp.data.decode("utf-8", errors="ignore")


def main():
    with test_app() as app:
        client = app.test_client()

        # 1) Seed: 2 questões
        q1 = QuestaoENEM(
            ano=2020,
            pergunta="Qual é o valor de x na equação x + 2 = 5?",
            opcao_a="1",
            opcao_b="2",
            opcao_c="3",
            opcao_d="4",
            opcao_e="5",
            resposta_correta="C",
        )
        q2 = QuestaoENEM(
            ano=2021,
            pergunta="Aceleração é a variação de…",
            opcao_a="força",
            opcao_b="tempo",
            opcao_c="velocidade",
            opcao_d="massa",
            opcao_e="altura",
            resposta_correta="C",
        )
        db.session.add_all([q1, q2])
        db.session.commit()
        print("✓ Seed de questões feito.")

        # 2) /auth/register
        email = "teste@ex.com"
        r = client.post(
            "/api/v1/auth/register",
            json={"email": email, "senha": "minha123", "nome": "Teste"},
        )
        assert r.status_code == 200, f"register falhou: {jprint(r)}"
        print("✓ /auth/register OK:", jprint(r))

        # 3) /auth/me (já autenticado)
        r = client.get("/api/v1/auth/me")
        assert r.status_code == 200, f"/me falhou: {jprint(r)}"
        me_json = r.get_json()
        print("✓ /auth/me OK:", json.dumps(me_json, ensure_ascii=False, indent=2))
        assert me_json.get("is_admin") in (False, 0, None), "esperava não-admin inicialmente"

        # 3.1) Promove para admin e valida no /me
        user = db.session.query(Usuario).filter_by(email=email).first()
        assert user is not None, "usuário não encontrado após register"
        if hasattr(user, "is_admin"):
            user.is_admin = True
            db.session.commit()

            r = client.get("/api/v1/auth/me")
            assert r.status_code == 200, f"/me após promover falhou: {jprint(r)}"
            me_admin = r.get_json()
            print("✓ /auth/me (após promover) OK:", json.dumps(me_admin, ensure_ascii=False, indent=2))
            assert bool(me_admin.get("is_admin")) is True, "flag is_admin não refletiu como True"

        # 4) /desafio/proxima
        r = client.get("/api/v1/desafio/proxima")
        assert r.status_code in (200, 204), f"/desafio/proxima falhou: {jprint(r)}"
        if r.status_code == 204:
            raise SystemExit("Sem questões disponíveis (inesperado no teste).")
        primeira = r.get_json()
        print("✓ /desafio/proxima OK:", jprint(r))
        questao_id = primeira["id"]

        # 5) /desafio/responder
        r = client.post(
            "/api/v1/desafio/responder",
            json={"questao_id": questao_id, "resposta": "C"},
        )
        assert r.status_code == 200, f"/desafio/responder falhou: {jprint(r)}"
        print("✓ /desafio/responder OK:", jprint(r))

        # 6) /desempenho/resumo
        r = client.get("/api/v1/desempenho/resumo")
        assert r.status_code == 200, f"/desempenho/resumo falhou: {jprint(r)}"
        print("✓ /desempenho/resumo OK:", jprint(r))

        # 7) /desempenho/por-ano
        r = client.get("/api/v1/desempenho/por-ano")
        assert r.status_code == 200, f"/desempenho/por-ano falhou: {jprint(r)}"
        print("✓ /desempenho/por-ano OK:", jprint(r))

        # 8) /desempenho/por-assunto
        r = client.get("/api/v1/desempenho/por-assunto")
        assert r.status_code == 200, f"/desempenho/por-assunto falhou: {jprint(r)}"
        print("✓ /desempenho/por-assunto OK:", jprint(r))

        print("\n🎉 Smoke test concluído com sucesso (incluindo verificação de is_admin).")


if __name__ == "__main__":
    main()
