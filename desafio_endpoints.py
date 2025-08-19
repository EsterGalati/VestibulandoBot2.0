from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "supersecreto"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vestibulando.db'
db = SQLAlchemy(app)

# === MODELOS ===
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    senha = db.Column(db.String(120))

class QuestaoENEM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ano = db.Column(db.Integer)
    pergunta = db.Column(db.String(500))
    opcoes = db.Column(db.PickleType)  # dicionário {'A':'...', 'B':'...'}

class ResultadoUsuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    questao_id = db.Column(db.Integer, db.ForeignKey('questao_e_n_e_m.id'))
    resposta_usuario = db.Column(db.String(1))

with app.app_context():
    db.create_all()

# === ROTAS ===
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    senha = request.form["senha"]
    usuario = Usuario.query.filter_by(email=email, senha=senha).first()
    if usuario:
        flash("Login realizado com sucesso!")
        return redirect(url_for("modo_estudo"))
    else:
        flash("Usuário ou senha incorretos!")
        return redirect(url_for("index"))

@app.route("/cadastro", methods=["POST"])
def cadastro():
    email = request.form["email"]
    senha = request.form["senha"]
    if Usuario.query.filter_by(email=email).first():
        flash("Usuário já existe!")
        return redirect(url_for("index"))
    usuario = Usuario(email=email, senha=senha)
    db.session.add(usuario)
    db.session.commit()
    flash("Cadastro realizado com sucesso!")
    return redirect(url_for("modo_estudo"))

@app.route("/modo_estudo")
def modo_estudo():
    questao = QuestaoENEM.query.first()
    return render_template("modo_estudo.html", questao=questao)

@app.route("/modo_desafio")
def modo_desafio():
    questoes = QuestaoENEM.query.limit(5).all()
    return render_template("modo_desafio.html", questoes=questoes)

@app.route("/responder/<int:questao_id>", methods=["POST"])
def responder_questao(questao_id):
    resposta = request.form["resposta"]
    questao = QuestaoENEM.query.get(questao_id)
    # Salva resultado (para simplificação, pegamos primeiro usuário)
    usuario = Usuario.query.first()
    resultado = ResultadoUsuario(usuario_id=usuario.id, questao_id=questao.id, resposta_usuario=resposta)
    db.session.add(resultado)
    db.session.commit()
    correta = (resposta.upper() == 'A')  # Ajuste conforme sua lógica ou CSV
    return render_template("resultado.html", resposta_usuario=resposta, resposta_correta='A', correta=correta)

if __name__ == "__main__":
    app.run(debug=True)
