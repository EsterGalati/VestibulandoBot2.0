# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user, UserMixin
)
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func, case

# =========================================
# Configuração Flask + Banco
# =========================================
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vestibulando.db'  # mantenha igual no popular_questoes.py
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'troque-esta-chave'  # mude para um valor seguro em produção

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login_page'  # rota usada quando precisa logar


# =========================================
# Modelos
# =========================================
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class QuestaoENEM(db.Model):
    __tablename__ = 'questoes_enem'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ano = db.Column(db.Integer, nullable=False)
    pergunta = db.Column(db.Text, nullable=False)
    opcao_a = db.Column(db.Text, nullable=False)
    opcao_b = db.Column(db.Text, nullable=False)
    opcao_c = db.Column(db.Text, nullable=False)
    opcao_d = db.Column(db.Text, nullable=False)
    opcao_e = db.Column(db.Text, nullable=False)
    resposta_correta = db.Column(db.String(1), nullable=False)  # 'A'..'E'

class ResultadoUsuario(db.Model):
    __tablename__ = 'resultado_usuario'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    questao_id = db.Column(db.Integer, db.ForeignKey('questoes_enem.id'), nullable=False)
    resposta = db.Column(db.String(1), nullable=False)
    acertou = db.Column(db.Boolean, nullable=False)

    usuario = db.relationship('Usuario', backref='resultados')
    questao = db.relationship('QuestaoENEM', backref='respostas')


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


# cria tabelas
with app.app_context():
    db.create_all()


# =========================================
# Páginas públicas
# =========================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/cadastro', methods=['GET'])
def cadastro_page():
    return render_template('cadastro.html')


# =========================================
# Ações de autenticação
# =========================================
@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email', '').strip().lower()
    senha = request.form.get('senha', '')

    user = Usuario.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, senha):
        flash('E-mail ou senha inválidos.')
        return redirect(url_for('login_page'))

    login_user(user)
    flash('Login realizado!')
    return redirect(url_for('desafio'))

@app.route('/cadastro', methods=['POST'])
def cadastro_post():
    email = request.form.get('email', '').strip().lower()
    senha = request.form.get('senha', '')

    if not email or not senha:
        flash('Preencha e-mail e senha.')
        return redirect(url_for('cadastro_page'))

    if Usuario.query.filter_by(email=email).first():
        flash('Este e-mail já está cadastrado.')
        return redirect(url_for('login_page'))

    user = Usuario(email=email, password_hash=generate_password_hash(senha))
    db.session.add(user)
    db.session.commit()

    login_user(user)
    flash('Cadastro realizado com sucesso!')
    return redirect(url_for('desafio'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta.')
    return redirect(url_for('index'))


# =========================================
# Modo Estudo
# =========================================
@app.route('/estudo', methods=['GET', 'POST'])
@login_required
def estudo():
    if request.method == 'POST':
        pergunta = request.form.get('pergunta', '')
        # Aqui você pode integrar com uma IA. Por ora, simulamos:
        resposta = f"Resposta simulada para: {pergunta}"
        return render_template('estudo.html', pergunta=pergunta, resposta=resposta)
    return render_template('estudo.html')

# (alias opcional, caso tenha links antigos)
# app.add_url_rule('/modo_estudo', endpoint='modo_estudo', view_func=estudo, methods=['GET','POST'])


# =========================================
# Modo Desafio
# =========================================
@app.route('/desafio', methods=['GET', 'POST'])
@login_required
def desafio():
    if request.method == 'POST':
        questao_id = request.form.get('questao_id')
        resposta_usuario = request.form.get('resposta', '').upper().strip()

        if not questao_id or not resposta_usuario:
            flash('Selecione uma alternativa.')
            return redirect(url_for('desafio'))

        questao = QuestaoENEM.query.get(int(questao_id))
        if not questao:
            flash('Questão não encontrada.')
            return redirect(url_for('desafio'))

        acertou = (resposta_usuario == questao.resposta_correta.upper().strip())

        db.session.add(ResultadoUsuario(
            usuario_id=current_user.id,
            questao_id=questao.id,
            resposta=resposta_usuario,
            acertou=acertou
        ))
        db.session.commit()

        # SÓ mostra o feedback após o POST
        return render_template('desafio.html',
                               questao=questao,
                               acertou=acertou,
                               show_feedback=True)

    # ---- GET: mostrar apenas a questão, SEM feedback ----
    ano = request.args.get('ano', type=int)
    query = QuestaoENEM.query
    if ano:
        query = query.filter_by(ano=ano)
    questao = query.order_by(db.func.random()).first()

    return render_template('desafio.html',
                           questao=questao,
                           acertou=None,
                           show_feedback=False)

# (alias opcional, caso tenha links antigos)
# app.add_url_rule('/modo_desafio', endpoint='modo_desafio', view_func=desafio, methods=['GET','POST'])

def classificar_assunto(questao: "QuestaoENEM") -> str:
    """Classifica um assunto de forma simples a partir do enunciado/opções."""
    txt = " ".join([
        (questao.pergunta or ""),
        (questao.opcao_a or ""), (questao.opcao_b or ""),
        (questao.opcao_c or ""), (questao.opcao_d or ""), (questao.opcao_e or "")
    ]).lower()

    regras = [
        ("Química", [
            "símbolo químico", "simbolo quimico", "tabela periódica", "tabela periodica",
            "reação", "reacao", "equilíbrio químico", "equilibrio quimico", "mol", "ph",
            "ácido", "base", "sal", "estequiometria"
        ]),
        ("Física", [
            "força", "forca", "velocidade", "aceleração", "aceleracao", "energia",
            "trabalho", "potência", "potencia", "movimento", "newton", "eletricidade",
            "campo elétrico", "campo eletrico", "óptica", "optica", "ondas", "circuito"
        ]),
        ("Matemática", [
            "equação", "equacao", "função", "funcao", "porcentagem", "probabilidade",
            "estatística", "estatistica", "progressão", "progressao", "matriz", "logaritmo",
            "derivada", "integral", "geometria", "triângulo", "triangulo", "área", "area",
            "volume", "potenciação", "potenciacao", "fatoração", "fatoracao", "sistema linear"
        ]),
        ("Biologia", [
            "célula", "celula", "dna", "rna", "mitose", "meiose", "ecologia", "ecossistema",
            "fotossíntese", "fotossintese", "respiração celular", "respiracao celular",
            "evolução", "evolucao", "bioma", "homeostase"
        ]),
        ("Geografia", [
            "capital", "oceano", "continente", "clima", "bioma", "industrialização",
            "globalização", "mapa", "latitude", "longitude", "demografia", "urbanização",
            "relevo", "região", "regiao"
        ]),
        ("História", [
            "independência", "independencia", "guerra", "revolução", "revolucao", "império",
            "imperio", "ditadura", "era vargas", "primeira guerra", "segunda guerra",
            "período colonial", "periodo colonial", "idade média", "idade media", "renascimento"
        ]),
        ("Português", [
            "sintaxe", "morfologia", "ortografia", "acentuação", "acentuacao", "semântica",
            "semantica", "voz passiva", "oração", "oracao", "sujeito", "predicado", "crase",
            "coesão", "coerência", "interpret"
        ]),
        ("Literatura", [
            "romantismo", "modernismo", "realismo", "simbolismo", "machado de assis",
            "dom casmurro", "drummond", "clarice lispector", "oswald de andrade",
            "mário de andrade", "mario de andrade", "camões", "camoes", "soneto"
        ]),
        ("Filosofia", [
            "sócrates", "socrates", "platão", "platao", "aristóteles", "aristoteles",
            "ética", "etica", "epistemologia", "metafísica", "metafisica", "kant", "nietzsche"
        ]),
        ("Sociologia", [
            "marx", "durkheim", "weber", "cultura", "alienação", "alienacao",
            "estratificação", "estratificacao", "movimentos sociais", "desigualdade"
        ]),
        ("Inglês", ["texto em inglês", "ingles"]),
        ("Espanhol", ["texto em espanhol", "espanhol"]),
        ("Artes", ["vanguarda", "expressionismo", "cubismo", "barroco", "renascentista"]),
    ]

    for assunto, chaves in regras:
        for k in chaves:
            if k in txt:
                return assunto
    return "Outros"

# =========================================
# Desempenho do usuário
# =========================================
@app.route('/desempenho')
@login_required
def desempenho():
    # Totais
    total = db.session.query(func.count(ResultadoUsuario.id))\
        .filter_by(usuario_id=current_user.id).scalar() or 0

    acertos = db.session.query(func.count(ResultadoUsuario.id))\
        .filter(
            ResultadoUsuario.usuario_id == current_user.id,
            ResultadoUsuario.acertou == True
        ).scalar() or 0

    percentual = round((acertos / total * 100), 2) if total else 0.0

    # Quebra por ano
    por_ano_rows = db.session.query(
        QuestaoENEM.ano.label('ano'),
        func.count(ResultadoUsuario.id).label('total'),
        func.sum(case((ResultadoUsuario.acertou == True, 1), else_=0)).label('acertos')
    ).join(QuestaoENEM, ResultadoUsuario.questao_id == QuestaoENEM.id)\
     .filter(ResultadoUsuario.usuario_id == current_user.id)\
     .group_by(QuestaoENEM.ano)\
     .order_by(QuestaoENEM.ano).all()

    por_ano = [{
        "ano": r.ano,
        "total": r.total,
        "acertos": int(r.acertos or 0),
        "percentual": round(((r.acertos or 0) / r.total * 100), 2)
    } for r in por_ano_rows]

    # ---- Quebra por ASSUNTO (classificação por palavra-chave) ----
    rows = db.session.query(ResultadoUsuario, QuestaoENEM)\
        .join(QuestaoENEM, ResultadoUsuario.questao_id == QuestaoENEM.id)\
        .filter(ResultadoUsuario.usuario_id == current_user.id)\
        .all()

    by_assunto = {}
    for ru, q in rows:
        assunto = classificar_assunto(q)
        s = by_assunto.setdefault(assunto, {"total": 0, "acertos": 0})
        s["total"] += 1
        s["acertos"] += 1 if ru.acertou else 0

    por_assunto = []
    for assunto, s in by_assunto.items():
        pct = round((s["acertos"] / s["total"] * 100), 2) if s["total"] else 0.0
        por_assunto.append({"assunto": assunto, "total": s["total"], "acertos": s["acertos"], "percentual": pct})

    # Sugestões: assuntos com pior % (com pelo menos 2 tentativas)
    candidatos = [x for x in por_assunto if x["total"] >= 2]
    candidatos.sort(key=lambda x: (x["percentual"], -x["total"]))  # menor % primeiro
    sugestoes = candidatos[:3] if candidatos else []

    return render_template('desempenho.html',
                           total=total,
                           acertos=acertos,
                           percentual=percentual,
                           por_ano=por_ano,
                           por_assunto=por_assunto,
                           sugestoes=sugestoes)

# =========================================
# Main
# =========================================
if __name__ == '__main__':
    app.run(debug=True)
