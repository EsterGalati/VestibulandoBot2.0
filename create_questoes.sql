CREATE TABLE IF NOT EXISTS questoes (
    id INTEGER PRIMARY KEY,
    subject TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    question TEXT NOT NULL,
    options TEXT NOT NULL,          -- Será armazenado como JSON string
    correct_answer INTEGER NOT NULL,
    explanation TEXT,
    tags TEXT                       -- Também como JSON string
);
