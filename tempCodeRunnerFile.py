import sqlite3
import json

with open("data/knowledge_base.json", encoding="utf-8") as f:
    base = json.load(f)

conn = sqlite3.connect("vestibulando.db")
cursor = conn.cursor()

for materia, topicos in base.items():
    for topico, explicacao in topicos.items():
        cursor.execute("""
            INSERT INTO conhecimentos (materia, topico, explicacao)
            VALUES (?, ?, ?)
        """, (materia.capitalize(), topico.lower(), explicacao))

conn.commit()
conn.close()
print("✅ Base de conhecimento migrada com sucesso.")
