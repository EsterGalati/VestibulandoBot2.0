import streamlit as st
import datetime
import time
import db  # <-- importa seu módulo de banco de dados
from models import Message

def study_mode(knowledge_base):
    st.markdown('<div class="main-header"><h1>🧠 Modo Estudo</h1><p>Tire suas dúvidas e aprofunde seus conhecimentos</p></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("💬 Chat com o Assistente")

        with st.container():
            for message in st.session_state.messages:
                css_class = "user-message" if message.type == "user" else "bot-message"
                st.markdown(f"""
                <div class="chat-message {css_class}">
                    <strong>{'Você' if message.type == "user" else '🤖 VestibulandoBot'}:</strong><br>
                    {message.content}<br>
                    <small>{message.timestamp.strftime('%H:%M')}</small>
                </div>
                """, unsafe_allow_html=True)

        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_area("Digite sua dúvida:", placeholder="Ex: O que é função quadrática?", height=100)
            submitted = st.form_submit_button("Enviar 📤")

            if submitted and user_input.strip():
                user_msg = Message(
                    id=str(len(st.session_state.messages)),
                    type="user",
                    content=user_input,
                    timestamp=datetime.datetime.now()
                )
                st.session_state.messages.append(user_msg)

                with st.spinner("Pensando... 🤔"):
                    time.sleep(1)
                    bot_response = find_answer(user_input, knowledge_base)

                bot_msg = Message(
                    id=str(len(st.session_state.messages)),
                    type="bot",
                    content=bot_response,
                    timestamp=datetime.datetime.now()
                )
                st.session_state.messages.append(bot_msg)
                st.rerun()

    with col2:
        st.subheader("💡 Perguntas Rápidas")
        quick_questions = [
            "Como resolver equações do segundo grau?",
            "Quais são as figuras de linguagem?",
            "Como funciona a cinemática?",
            "Estrutura da redação ENEM",
            "O que são logaritmos?",
            "Leis da termodinâmica",
            "Organelas celulares",
            "Revolução Industrial"
        ]

        for q in quick_questions:
            if st.button(f"❓ {q}", key=f"quick_{q}", use_container_width=True):
                st.session_state.messages.append(Message(
                    id=str(len(st.session_state.messages)),
                    type="user",
                    content=q,
                    timestamp=datetime.datetime.now()
                ))
                st.session_state.messages.append(Message(
                    id=str(len(st.session_state.messages)),
                    type="bot",
                    content=find_answer(q, knowledge_base),
                    timestamp=datetime.datetime.now()
                ))
                st.rerun()

        st.subheader("📊 Status do Sistema")
        st.success("✅ Base Local Ativa")
        st.warning("⚠️ IA Externa Desabilitada")
        st.info("📡 Modo Offline Disponível")


# 🔍 Lógica de busca de conteúdo e registro da interação no banco
def find_answer(question: str, knowledge_base: dict) -> str:
    q_lower = question.lower()
    for subject in knowledge_base:
        for topic in knowledge_base[subject]:
            if topic.lower() in q_lower or subject.lower() in q_lower:
                if "usuario_id" in st.session_state:
                    db.registrar_interacao_estudo(st.session_state["usuario_id"], topic)
                return f"{knowledge_base[subject][topic]} 📚 Precisa de mais detalhes? Posso explicar com exemplos!"
    return "🤔 Não encontrei essa informação. Tente reformular sua dúvida ou consulte um material de apoio."
