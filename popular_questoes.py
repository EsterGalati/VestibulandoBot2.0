import sqlite3
import json

DB_PATH = "vestibulando.db"

def conectar():
    return sqlite3.connect(DB_PATH)

def inserir_questoes_enem(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        questoes = json.load(f)

    conn = conectar()
    cursor = conn.cursor()

    for q in questoes:
        try:
            id = int(q["id"])  # Corrigido: ID já é inteiro

            cursor.execute("""
                INSERT OR REPLACE INTO questoes (
                    id, subject, difficulty, question,
                    options, correct_answer, explanation, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                id,
                q["subject"],
                q["difficulty"],
                q["question"],
                json.dumps(q["options"], ensure_ascii=False),
                int(q["correct_answer"]),
                q["explanation"],
                json.dumps(q.get("tags", []), ensure_ascii=False)
            ))

        except Exception as e:
            print(f"Erro na questão ID {q['id']}: {e}")

    conn.commit()
    conn.close()
    print("Importação concluída.")

if __name__ == "__main__":
    inserir_questoes_enem("data/questoes_enem.json")
