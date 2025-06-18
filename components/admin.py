import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import db  # Banco SQLite
import json

def admin_panel(questions_bank):
    st.markdown('<div class="main-header"><h1>⚙️ Painel Administrativo</h1><p>Visualize estatísticas, usuários e gerencie o conteúdo</p></div>', unsafe_allow_html=True)

    usuario_id = st.session_state.get("usuario_id")

    # VISÃO GERAL
    total_usuarios = db.total_usuarios()
    total_sessoes = db.total_sessoes()
    total_respostas = db.total_respostas()

    # Estatísticas filtradas por usuário logado
    estatisticas = db.estatisticas_por_materia_usuario(usuario_id) if usuario_id else []
    estat_simulados = db.estatisticas_por_simulado_usuario(usuario_id) if usuario_id else []

    st.subheader("📌 Visão Geral")
    col1, col2, col3 = st.columns(3)
    col1.metric("👥 Usuários Registrados", total_usuarios)
    col2.metric("📊 Respostas Registradas", total_respostas)
    col3.metric("⏱️ Sessões Iniciadas", total_sessoes)

    st.markdown("---")
    st.subheader("📚 Estatísticas por Matéria")

    if estatisticas:
        df = pd.DataFrame(estatisticas, columns=["Matéria", "Total Respondidas", "Acertos"])
        df["Uso (%)"] = round((df["Total Respondidas"] / df["Total Respondidas"].sum()) * 100, 1)
        df["Aproveitamento (%)"] = round((df["Acertos"] / df["Total Respondidas"]) * 100, 1)

        st.dataframe(
            df.style
            .format({"Uso (%)": "{:.1f}%", "Aproveitamento (%)": "{:.1f}%"}),
            use_container_width=True
        )

        st.subheader("📈 Distribuição de Uso por Matéria")
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(df["Uso (%)"], labels=df["Matéria"], autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)
    else:
        st.info("Ainda não há estatísticas registradas.")

    st.markdown("---")
    st.subheader("🧪 Estatísticas por Simulado")

    if estat_simulados:
        df_sim = pd.DataFrame(estat_simulados, columns=["Simulado", "Total Respondidas", "Acertos"])
        df_sim["Aproveitamento (%)"] = round((df_sim["Acertos"] / df_sim["Total Respondidas"]) * 100, 1)

        st.dataframe(
            df_sim.style.format({"Aproveitamento (%)": "{:.1f}%"}),
            use_container_width=True
        )

        fig_sim, ax_sim = plt.subplots(figsize=(6, 4))
        ax_sim.barh(df_sim["Simulado"], df_sim["Aproveitamento (%)"], color="#4F46E5")
        ax_sim.set_xlabel("Aproveitamento (%)")
        ax_sim.set_title("Desempenho por Simulado")
        st.pyplot(fig_sim)

    else:
        st.info("👭 Ainda não há respostas associadas a simulados.")

    st.markdown("---")
    st.subheader("➕ Cadastrar Nova Questão")

    with st.form("nova_questao_form"):
        subject = st.text_input("📘 Matéria:")
        difficulty = st.selectbox("🎯 Dificuldade:", ["Básico", "Intermediário", "Avançado"])
        question_text = st.text_area("❓ Enunciado da questão:")
        options = [st.text_input(f"Opção {i+1}:", key=f"opt_{i}") for i in range(4)]
        correct_index = st.selectbox("✅ Índice da resposta correta (0 a 3):", [0, 1, 2, 3])
        explanation = st.text_area("📖 Explicação:")
        tags = st.text_input("🏷️ Tags (separadas por vírgula):")
        enviar = st.form_submit_button("Cadastrar Questão")

        if enviar:
            if subject and question_text and all(opt.strip() for opt in options):
                db.inserir_questao(
                    subject=subject.strip(),
                    difficulty=difficulty,
                    question=question_text.strip(),
                    options=options,
                    correct_answer=correct_index,
                    explanation=explanation.strip(),
                    tags=[t.strip() for t in tags.split(",") if t.strip()]
                )
                st.success("✅ Questão adicionada com sucesso!")
                st.rerun()
            else:
                st.error("⚠️ Todos os campos obrigatórios devem ser preenchidos.")
