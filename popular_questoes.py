# popular_questoes.py
import pandas as pd
from app import app, db, QuestaoENEM  # importa do app.py

CSV_PATH = 'data/enem_questoes.csv'  # ajuste se necessário

with app.app_context():
    # limpa e repopula
    db.session.query(QuestaoENEM).delete()
    db.session.commit()

    df = pd.read_csv(CSV_PATH, encoding='utf-8')
    objs = []
    for _, r in df.iterrows():
        objs.append(QuestaoENEM(
            ano=int(r['ano']),
            pergunta=r['pergunta'],
            opcao_a=r['opcao_a'],
            opcao_b=r['opcao_b'],
            opcao_c=r['opcao_c'],
            opcao_d=r['opcao_d'],
            opcao_e=r['opcao_e'],
            resposta_correta=r['resposta_correta'].upper().strip()
        ))
    db.session.bulk_save_objects(objs)
    db.session.commit()
    print(f'Importadas {len(objs)} questões!')
