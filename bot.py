import streamlit as st
import datetime
import json
import os

from models import Message, Question, UserProgress
from components.study import study_mode
from components.challenge import challenge_mode
from components.performance import performance_analysis
from components.admin import admin_panel
from components.login import login_screen
import db

class VestibulandoBot:
    def __init__(self):
        self.load_css()
        self.knowledge_base = self.load_json("data/knowledge_base.json")
        self.questions_bank = self.load_questions_from_db()
        self.init_session_state()

    def load_css(self):
        try:
            with open("styles/custom.css") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        except FileNotFoundError:
            st.warning("⚠️ Arquivo de estilo 'custom.css' não encontrado.")

    def load_json(self, path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            st.error(f"❌ Arquivo não encontrado: {path}")
            return {}

    def load_questions_from_db(self):
        questions = db.carregar_questoes()
        return [Question(**q) for q in questions]

    def init_session_state(self):
        if 'messages' not in st.session_state:
            st.session_state.messages = [
                Message(
                    id="1",
                    type="bot",
                    content="Olá! Eu sou o VestibulandoBot 🤖 Pronto para estudar?",
                    timestamp=datetime.datetime.now()
                )
            ]

        if 'user_progress' not in st.session_state:
            if "usuario_id" in st.session_state:
                progresso = db.carregar_progresso(st.session_state.usuario_id)
                st.session_state.user_progress = UserProgress(**progresso)
            else:
                st.session_state.user_progress = UserProgress()

        if 'current_question' not in st.session_state:
            st.session_state.current_question = None

        if 'show_result' not in st.session_state:
            st.session_state.show_result = False

        if 'session_stats' not in st.session_state:
            st.session_state.session_stats = {'correct': 0, 'incorrect': 0, 'total': 0}

    def run(self):
        if "usuario_id" not in st.session_state:
            login_screen()
            return

        with st.sidebar:
            st.image("imagem1.png", width=150)
            st.markdown("---")

            if "usuario_nome" in st.session_state:
                st.markdown(f"👤 **Usuário:** {st.session_state.usuario_nome}")
                if st.button("🔒 Sair"):
                    if "usuario_id" in st.session_state:
                        db.encerrar_sessao(st.session_state["usuario_id"])
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()

            mode = st.radio(
                "📍 Navegação:",
                ["🧠 Modo Estudo", "🏆 Modo Desafio", "📊 Performance", "⚙️ Administração"],
                index=0
            )

            st.markdown("---")
            st.subheader("🎯 Meta Diária")
            value = min(50, st.session_state.session_stats['total'] * 10)
            st.progress(value)
            st.write(f"**{st.session_state.session_stats['total']}/10** questões hoje")

            st.markdown("---")
            st.subheader("📡 Status")
            st.success("🟢 Online")
            st.write("*Última sync: agora*")

        if mode == "🧠 Modo Estudo":
            study_mode(self.knowledge_base)
        elif mode == "🏆 Modo Desafio":
            challenge_mode(self.questions_bank)
        elif mode == "📊 Performance":
            performance_analysis(
                st.session_state.user_progress,
                st.session_state.session_stats
            )
        elif mode == "⚙️ Administração":
            admin_panel(self.questions_bank)
