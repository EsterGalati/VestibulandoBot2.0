-- Tabela de usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
);

-- Tabela de sessões
CREATE TABLE IF NOT EXISTS sessoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    inicio DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabela de estatísticas por matéria
CREATE TABLE IF NOT EXISTS estatisticas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    materia TEXT NOT NULL,
    total_respondidas INTEGER DEFAULT 0,
    acertos INTEGER DEFAULT 0,
    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabela de respostas dos usuários
CREATE TABLE IF NOT EXISTS historico_respostas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    questao_id INTEGER,
    materia TEXT NOT NULL,
    acertou BOOLEAN,
    respondido_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabela de interações no modo Estudo
CREATE TABLE IF NOT EXISTS interacoes_estudo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    assunto TEXT NOT NULL,
    interagido_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabela de questões (banco de dados em vez de JSON)
CREATE TABLE IF NOT EXISTS questoes (
    id INTEGER PRIMARY KEY,
    subject TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    question TEXT NOT NULL,
    options TEXT NOT NULL,           -- Armazenado como JSON string
    correct_answer INTEGER NOT NULL,
    explanation TEXT,
    tags TEXT                        -- Também como JSON string
);

CREATE TABLE IF NOT EXISTS progresso_usuario (
    usuario_id INTEGER PRIMARY KEY,
    total_questions INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    streak INTEGER DEFAULT 0,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
