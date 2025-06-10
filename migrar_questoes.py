import sqlite3
import json

with open("data/questions.json", encoding="utf-8") as f:
    questoes = json.load(f)

conn = sqlite3.connect("vestibulando.db")
cursor = conn.cursor()

for q in questoes:
    cursor.execute("""
        INSERT OR REPLACE INTO questoes (id, subject, difficulty, question, options, correct_answer, explanation, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        q["id"],
        q["subject"],
        q["difficulty"],
        q["question"],
        json.dumps(q["options"], ensure_ascii=False),
        q["correct_answer"],
        q.get("explanation", ""),
        json.dumps(q.get("tags", []), ensure_ascii=False)
    ))

conn.commit()
conn.close()
print("✅ Questões migradas com sucesso.")
