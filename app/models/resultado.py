from app.extensions import db


class ResultadoUsuario(db.Model):
    __tablename__ = "resultado_usuario"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    questao_id = db.Column(
        db.Integer, db.ForeignKey("questoes_enem.id"), nullable=False
    )
    resposta = db.Column(db.String(1), nullable=False)
    acertou = db.Column(db.Boolean, nullable=False)
    respondido_em = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    usuario = db.relationship("Usuario", backref="resultados")
    questao = db.relationship("QuestaoENEM", backref="respostas")
