import streamlit as st
import random
import db  # Módulo de persistência SQLite

def challenge_mode(questions_bank):
    st.markdown('<div class="main-header"><h1>🏆 Modo Desafio</h1><p>Teste seus conhecimentos com questões práticas</p></div>', unsafe_allow_html=True)

    if 'questoes_respondidas' not in st.session_state:
        st.session_state.questoes_respondidas = set()

    usuario_id = st.session_state.get("usuario_id")

    # 🔽 Selecione o simulado ativo uma vez
    if "simulado_id" not in st.session_state:
        simulados = db.listar_simulados()
        if not simulados:
            st.warning("⚠️ Nenhum simulado cadastrado. Cadastre pelo painel administrativo.")
            return
        nomes = [s[1] for s in simulados]
        simulado_nome = st.selectbox("🧪 Escolha o Simulado:", nomes)
        st.session_state["simulado_id"] = next((s[0] for s in simulados if s[1] == simulado_nome), None)

    simulado_id = st.session_state.get("simulado_id")

    st.markdown("---")

    # 🔄 Opção de recomeçar manualmente
    with st.expander("⚙️ Opções de Sessão"):
        st.info("Você pode continuar de onde parou ou reiniciar o desafio.")
        if st.button("🔄 Começar do Zero"):
            st.session_state.questoes_respondidas = set()
            st.session_state.current_question = None
            st.session_state.show_result = False
            if usuario_id:
                db.salvar_questao_em_andamento(usuario_id, None)
            st.rerun()

    questoes_disponiveis = [q for q in questions_bank if q.id not in st.session_state.questoes_respondidas]

    if not questoes_disponiveis:
        st.success("✅ Você respondeu todas as questões disponíveis desta sessão!")
        if st.button("🔁 Reiniciar Sessão"):
            st.session_state.questoes_respondidas = set()
            st.session_state.current_question = None
            st.session_state.show_result = False
            if usuario_id:
                db.salvar_questao_em_andamento(usuario_id, None)
            st.rerun()
        return

    if st.session_state.current_question is None:
        if usuario_id:
            questao_id = db.carregar_questao_em_andamento(usuario_id)
            if questao_id:
                for q in questions_bank:
                    if q.id == questao_id:
                        st.session_state.current_question = q
                        break

        if st.session_state.current_question is None:
            st.markdown("### 🚀 Pronto para o desafio?")
            st.write("Teste seus conhecimentos com questões do banco de dados educacional.")
            if st.button("🎯 Iniciar Nova Questão", type="primary", use_container_width=True):
                nova = random.choice(questoes_disponiveis)
                st.session_state.current_question = nova
                st.session_state.show_result = False
                if usuario_id:
                    db.salvar_questao_em_andamento(usuario_id, nova.id)
                st.rerun()

    else:
        question = st.session_state.current_question

        st.markdown(f"""
        <div class="question-card">
            <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                <span style="background: #4F46E5; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px;">{question.subject}</span>
                <span style="background: #8B5CF6; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px;">{question.difficulty}</span>
            </div>
            <h3>{question.question}</h3>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.show_result:
            selected_answer = st.radio("Escolha sua resposta:", question.options, key="answer_radio")

            if st.button("✅ Confirmar Resposta", type="primary"):
                selected_index = question.options.index(selected_answer)
                is_correct = selected_index == question.correct_answer

                # Atualiza progresso do usuário
                st.session_state.user_progress.total_questions += 1
                if is_correct:
                    st.session_state.user_progress.correct_answers += 1
                    st.session_state.user_progress.streak += 1
                else:
                    st.session_state.user_progress.streak = 0

                subject = question.subject
                if subject not in st.session_state.user_progress.subjects:
                    st.session_state.user_progress.subjects[subject] = {"total": 0, "correct": 0}
                st.session_state.user_progress.subjects[subject]["total"] += 1
                if is_correct:
                    st.session_state.user_progress.subjects[subject]["correct"] += 1

                if usuario_id:
                    db.registrar_resposta(usuario_id, question.id, subject, is_correct, simulado_id)
                    db.atualizar_estatisticas(usuario_id, subject, is_correct)
                    db.atualizar_progresso(usuario_id, is_correct)
                    db.salvar_questao_em_andamento(usuario_id, None)

                st.session_state.questoes_respondidas.add(question.id)
                st.session_state.show_result = True
                st.session_state.selected_answer_index = selected_index
                st.rerun()

        else:
            is_correct = st.session_state.selected_answer_index == question.correct_answer

            if is_correct:
                st.success("🎉 Parabéns! Resposta correta!")
            else:
                st.error("❌ Resposta incorreta.")
                st.info(f"✅ Resposta correta: {question.options[question.correct_answer]}")

            st.info(f"📚 **Explicação:** {question.explanation}")

            if question.tags:
                tags_html = " ".join([
                    f'<span style="background: #E2E8F0; padding: 3px 8px; border-radius: 10px; font-size: 12px; margin: 2px;">{tag}</span>'
                    for tag in question.tags
                ])
                st.markdown(f"**Tags:** {tags_html}", unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("➡️ Próxima Questão", type="primary"):
                    nova_disponivel = [q for q in questions_bank if q.id not in st.session_state.questoes_respondidas]
                    if nova_disponivel:
                        nova = random.choice(nova_disponivel)
                        st.session_state.current_question = nova
                        st.session_state.show_result = False
                        if usuario_id:
                            db.salvar_questao_em_andamento(usuario_id, nova.id)
                    else:
                        st.session_state.current_question = None
                        st.success("🎉 Você concluiu todas as questões!")
                    st.rerun()
            with col2:
                if st.button("🏠 Voltar ao Início"):
                    st.session_state.current_question = None
                    st.rerun()
