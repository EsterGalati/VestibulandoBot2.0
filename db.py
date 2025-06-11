import sqlite3
import json
from datetime import datetime

DB_PATH = "vestibulando.db"

def conectar():
    return sqlite3.connect(DB_PATH)

# Usuários
def registrar_usuario(nome, email):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO usuarios (nome, email) VALUES (?, ?)", (nome, email))
    conn.commit()
    cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
    usuario_id = cursor.fetchone()[0]
    conn.close()
    return usuario_id

def listar_usuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nome, email, criado_em FROM usuarios
        ORDER BY criado_em DESC
    """)
    usuarios = cursor.fetchall()
    conn.close()
    return usuarios

# Sessões
def iniciar_sessao(usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sessoes (usuario_id) VALUES (?)", (usuario_id,))
    conn.commit()
    conn.close()

def encerrar_sessao(usuario_id):
    conn = conectar()
    cursor = conn.cursor()

    # Pega o ID da última sessão iniciada e ainda sem fim
    cursor.execute("""
        SELECT id FROM sessoes
        WHERE usuario_id = ? AND fim IS NULL
        ORDER BY inicio DESC
        LIMIT 1
    """, (usuario_id,))
    sessao = cursor.fetchone()

    if sessao:
        sessao_id = sessao[0]
        cursor.execute("""
            UPDATE sessoes
            SET fim = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (sessao_id,))
        conn.commit()

    conn.close()


def total_sessoes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sessoes")
    resultado = cursor.fetchone()[0]
    conn.close()
    return resultado

def sessoes_ativas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(DISTINCT usuario_id) FROM sessoes
        WHERE DATE(inicio) = DATE('now')
    """)
    total_ativas = cursor.fetchone()[0]
    conn.close()
    return total_ativas

# Estatísticas
def atualizar_estatisticas(usuario_id, materia, acertou):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, total_respondidas, acertos FROM estatisticas
        WHERE usuario_id = ? AND materia = ?
    """, (usuario_id, materia))
    row = cursor.fetchone()

    if row:
        estat_id, total, acertos = row
        total += 1
        if acertou:
            acertos += 1
        cursor.execute("""
            UPDATE estatisticas
            SET total_respondidas = ?, acertos = ?, atualizado_em = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (total, acertos, estat_id))
    else:
        cursor.execute("""
            INSERT INTO estatisticas (usuario_id, materia, total_respondidas, acertos)
            VALUES (?, ?, 1, ?)
        """, (usuario_id, materia, 1 if acertou else 0))

    conn.commit()
    conn.close()

def estatisticas_gerais():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT materia, COUNT(*) as total, SUM(acertou) as acertos
        FROM historico_respostas
        GROUP BY materia
    """)
    dados = cursor.fetchall()
    conn.close()
    return dados

def obter_estatisticas_por_materia(usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT materia, total_respondidas, acertos FROM estatisticas
        WHERE usuario_id = ?
    """, (usuario_id,))
    data = cursor.fetchall()
    conn.close()
    return data

# Histórico de respostas
def registrar_resposta(usuario_id, questao_id, materia, acertou, simulado_id=None):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO historico_respostas (usuario_id, questao_id, materia, acertou, simulado_id)
        VALUES (?, ?, ?, ?, ?)
    """, (usuario_id, questao_id, materia, acertou, simulado_id))
    conn.commit()
    conn.close()


def total_respostas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM historico_respostas")
    resultado = cursor.fetchone()[0]
    conn.close()
    return resultado

# Modo estudo
def registrar_interacao_estudo(usuario_id, assunto):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO interacoes_estudo (usuario_id, assunto)
        VALUES (?, ?)
    """, (usuario_id, assunto))
    conn.commit()
    conn.close()

# Progresso do usuário
def carregar_progresso(usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT total_questions, correct_answers, streak
        FROM progresso_usuario
        WHERE usuario_id = ?
    """, (usuario_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        total, acertos, streak = row
        return {
            "total_questions": total,
            "correct_answers": acertos,
            "streak": streak,
            "subjects": {}
        }
    else:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO progresso_usuario (usuario_id) VALUES (?)", (usuario_id,))
        conn.commit()
        conn.close()
        return {
            "total_questions": 0,
            "correct_answers": 0,
            "streak": 0,
            "subjects": {}
        }

def atualizar_progresso(usuario_id, acertou):
    conn = conectar()
    cursor = conn.cursor()

    if acertou:
        cursor.execute("""
            UPDATE progresso_usuario
            SET total_questions = total_questions + 1,
                correct_answers = correct_answers + 1,
                streak = streak + 1
            WHERE usuario_id = ?
        """, (usuario_id,))
    else:
        cursor.execute("""
            UPDATE progresso_usuario
            SET total_questions = total_questions + 1,
                streak = 0
            WHERE usuario_id = ?
        """, (usuario_id,))

    conn.commit()
    conn.close()

# Questões
def carregar_questoes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questoes")
    rows = cursor.fetchall()
    conn.close()

    questoes = []
    for row in rows:
        questoes.append({
            "id": row[0],
            "subject": row[1],
            "difficulty": row[2],
            "question": row[3],
            "options": json.loads(row[4]),
            "correct_answer": row[5],
            "explanation": row[6],
            "tags": json.loads(row[7]) if row[7] else []
        })
    return questoes

def inserir_questao(subject, difficulty, question, options, correct_answer, explanation, tags):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO questoes (subject, difficulty, question, options, correct_answer, explanation, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        subject, difficulty, question,
        json.dumps(options, ensure_ascii=False),
        correct_answer,
        explanation,
        json.dumps(tags, ensure_ascii=False)
    ))
    conn.commit()
    conn.close()

# Contagem total de usuários
def total_usuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    resultado = cursor.fetchone()[0]
    conn.close()
    return resultado
# Questão atual em andamento (Modo Desafio)
def salvar_questao_em_andamento(usuario_id, questao_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sessao_usuario (usuario_id, questao_atual_id)
        VALUES (?, ?)
        ON CONFLICT(usuario_id)
        DO UPDATE SET questao_atual_id = excluded.questao_atual_id
    """, (usuario_id, questao_id))
    conn.commit()
    conn.close()

def carregar_questao_em_andamento(usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT questao_atual_id FROM sessao_usuario WHERE usuario_id = ?
    """, (usuario_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

def estatisticas_por_simulado():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.nome, COUNT(hr.id) AS total, SUM(hr.acertou) AS acertos
        FROM historico_respostas hr
        JOIN simulados s ON hr.simulado_id = s.id
        GROUP BY s.nome
        ORDER BY s.nome
    """)
    dados = cursor.fetchall()
    conn.close()
    return dados
# Listar simulados disponíveis
def listar_simulados():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nome FROM simulados ORDER BY criado_em DESC
    """)
    simulados = cursor.fetchall()
    conn.close()
    return simulados
