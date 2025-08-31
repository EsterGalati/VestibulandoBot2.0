from app.extensions import db


class QuestaoENEM(db.Model):
    __tablename__ = "questoes_enem"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ano = db.Column(db.Integer, nullable=False)
    pergunta = db.Column(db.Text, nullable=False)
    opcao_a = db.Column(db.Text, nullable=False)
    opcao_b = db.Column(db.Text, nullable=False)
    opcao_c = db.Column(db.Text, nullable=False)
    opcao_d = db.Column(db.Text, nullable=False)
    opcao_e = db.Column(db.Text, nullable=False)
    resposta_correta = db.Column(db.String(1), nullable=False)  # 'A'..'E'
