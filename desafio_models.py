from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    criado_em = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

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
    resposta_correta = db.Column(db.String(1), nullable=False)

class ResultadoUsuario(db.Model):
    __tablename__ = "resultado_usuario"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    questao_id = db.Column(db.Integer, db.ForeignKey("questoes_enem.id"), nullable=False)
    resposta = db.Column(db.String(1), nullable=False)
    acertou = db.Column(db.Boolean, nullable=False)
    respondido_em = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    usuario = db.relationship("Usuario", backref="resultados")
    questao = db.relationship("QuestaoENEM", backref="respostas")
