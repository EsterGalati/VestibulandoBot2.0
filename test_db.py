import db

# 1. Registrar um novo usuário
usuario_id = db.registrar_usuario("Ester Luiza", "ester@email.com")
print(f"Usuário registrado com ID: {usuario_id}")

# 2. Iniciar uma sessão para o usuário
db.iniciar_sessao(usuario_id)
print("Sessão iniciada.")

# 3. Registrar uma resposta para uma questão
questao_id = "MAT001"
materia = "Matemática"
acertou = True
db.registrar_resposta(usuario_id, questao_id, materia, acertou)
print("Resposta registrada.")

# 4. Atualizar as estatísticas para essa matéria
db.atualizar_estatisticas(usuario_id, materia, acertou)
print("Estatísticas atualizadas.")

# 5. Ver estatísticas por matéria
estatisticas = db.obter_estatisticas_por_materia(usuario_id)
print("\n📊 Estatísticas por matéria:")
for materia, total, acertos in estatisticas:
    print(f"- {materia}: {acertos}/{total} acertos")
