from app import app, db, QuestaoENEM
with app.app_context():
    print('DB URI:', app.config['SQLALCHEMY_DATABASE_URI'])
    total = db.session.query(QuestaoENEM).count()
    print('Total de questões:', total)
    q = QuestaoENEM.query.first()
    if q:
        print('Exemplo:', q.id, q.ano, q.pergunta[:80])
