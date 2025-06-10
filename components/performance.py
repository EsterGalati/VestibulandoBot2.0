import streamlit as st
import pandas as pd
import plotly.express as px
import db  # Importando o módulo do SQLite

def performance_analysis(_, __):  # Ignoramos os antigos parâmetros
    st.markdown('<div class="main-header"><h1>📊 Análise de Performance</h1><p>Acompanhe sua evolução real e veja onde melhorar</p></div>', unsafe_allow_html=True)

    usuario_id = st.session_state["usuario_id"]
    stats = db.obter_estatisticas_por_materia(usuario_id)

    if not stats:
        st.info("📌 Ainda não há estatísticas salvas. Responda questões no modo desafio.")
        return

    # Total geral
    total = sum(row[1] for row in stats)
    correct = sum(row[2] for row in stats)
    accuracy = round((correct / total) * 100) if total > 0 else 0

    # Estimativa simples de streak baseada na sessão
    streak = st.session_state.user_progress.streak if "user_progress" in st.session_state else 0

    # Cards principais
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <h3>📚 Questões</h3>
            <h2>{total}</h2>
            <p>Total respondidas</p>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <h3>🎯 Taxa de Acerto</h3>
            <h2>{accuracy}%</h2>
            <p>Aproveitamento geral</p>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <h3>🔥 Sequência</h3>
            <h2>{streak}</h2>
            <p>Acertos consecutivos</p>
        </div>""", unsafe_allow_html=True)

    with col4:
        nivel = "⭐" * min(5, accuracy // 20)
        st.markdown(f"""
        <div class="stat-card">
            <h3>🏆 Nível</h3>
            <h2>{nivel}</h2>
            <p>Baseado no aproveitamento</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ----- GRAFICO DE PERFORMANCE POR MATÉRIA -----
    st.subheader("📊 Desempenho por Matéria")

    data = []
    for materia, total_materia, acertos in stats:
        acc = round((acertos / total_materia) * 100) if total_materia > 0 else 0
        data.append({"Matéria": materia, "Aproveitamento": acc})

    df = pd.DataFrame(data)
    fig = px.bar(df, x="Aproveitamento", y="Matéria", orientation="h", color="Aproveitamento", color_continuous_scale="Viridis")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    # ----- RECOMENDAÇÕES -----
    st.subheader("💡 Recomendações Personalizadas")

    sorted_data = sorted(data, key=lambda x: x["Aproveitamento"])
    col1, col2 = st.columns(2)

    with col1:
        lowest = sorted_data[0]
        st.warning(f"⚠️ Foque mais em **{lowest['Matéria']}** – Aproveitamento de apenas {lowest['Aproveitamento']}%.")

    with col2:
        highest = sorted_data[-1]
        st.success(f"🎉 Excelente desempenho em **{highest['Matéria']}** – {highest['Aproveitamento']}% de acertos!")
