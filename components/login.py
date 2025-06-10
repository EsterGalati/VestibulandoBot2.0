import streamlit as st
import db
import re

def validar_email(email: str) -> bool:
    """Valida o formato do e-mail de forma simples."""
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def login_screen():
    st.markdown(
        '<div class="main-header"><h1>🔐 Login</h1><p>Identifique-se para começar a usar o VestibulandoBot</p></div>',
        unsafe_allow_html=True
    )

    with st.form("login_form"):
        nome = st.text_input("👤 Nome completo")
        email = st.text_input("📧 E-mail")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            nome = nome.strip()
            email = email.strip()

            if not nome or not email:
                st.error("Por favor, preencha todos os campos.")
            elif not validar_email(email):
                st.error("E-mail inválido. Verifique o formato.")
            else:
                usuario_id = db.registrar_usuario(nome, email)
                db.iniciar_sessao(usuario_id)
                st.session_state["usuario_id"] = usuario_id
                st.session_state["usuario_nome"] = nome
                st.success("Login realizado com sucesso! ✅")
                st.rerun()
