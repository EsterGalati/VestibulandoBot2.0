import streamlit as st
import random
import db  # Módulo de persistência SQLite

def challenge_mode(questions_bank):
    st.markdown('<div class="main-header"><h1>🏆 Modo Desafio</h1><p>Teste seus conhecimentos com questões práticas</p></div>', unsafe_allow_html=True)

    # Inicializa lista de questões respondidas na sessão
    if 'questoes_respondidas' not in st.session_state:
        st.session_state.questoes_respondidas = set()

    # Estatísticas rápidas
    col1, col2, col3, col4 = st.columns(4)
    correct = st.session_state.session_stats.get('correct', 0)
    incorrect = st.session_state.session_stats.get('incorrect', 0)
    total = st.session_state.session_stats.get('total', 0)
    accuracy = round((correct / total) * 100) if total > 0 else 0

    with col1:
        st.markdown(f"""<div class="stat-card"><h3>🎯 Acertos</h3><h2>{correct}</h2></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="stat-card"><h3>❌ Erros</h3><h2>{incorrect}</h2></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="stat-card"><h3>📝 Total</h3><h2>{total}</h2></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="stat-card"><h3>📊 Aproveitamento</h3><h2>{accuracy}%</h2></div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Lista de questões ainda não respondidas
    questoes_disponiveis = [q for q in questions_bank if q.id not in st.session_state.questoes_respondidas]

    # Fim das questões
    if not questoes_disponiveis:
        st.success("✅ Você respondeu todas as questões disponíveis desta sessão!")
        if st.button("🔁 Reiniciar Sessão"):
            st.session_state.questoes_respondidas = set()
            st.session_state.current_question = None
            st.session_state.show_result = False
            st.rerun()
        return

    # Início do desafio
    if st.session_state.current_question is None:
        st.markdown("### 🚀 Pronto para o desafio?")
        st.write("Teste seus conhecimentos com questões do banco de dados educacional.")
        if st.button("🎯 Iniciar Nova Questão", type="primary", use_container_width=True):
            st.session_state.current_question = random.choice(questoes_disponiveis)
            st.session_state.show_result = False
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

                # Atualiza estatísticas da sessão
                st.session_state.session_stats['total'] += 1
                st.session_state.user_progress.total_questions += 1

                if is_correct:
                    st.session_state.session_stats['correct'] += 1
                    st.session_state.user_progress.correct_answers += 1
                    st.session_state.user_progress.streak += 1
                else:
                    st.session_state.session_stats['incorrect'] += 1
                    st.session_state.user_progress.streak = 0

                # Atualiza progresso por matéria
                subject = question.subject
                if subject not in st.session_state.user_progress.subjects:
                    st.session_state.user_progress.subjects[subject] = {"total": 0, "correct": 0}
                st.session_state.user_progress.subjects[subject]["total"] += 1
                if is_correct:
                    st.session_state.user_progress.subjects[subject]["correct"] += 1

                # Salva no banco
                usuario_id = st.session_state.get("usuario_id")
                if usuario_id:
                    db.registrar_resposta(usuario_id, question.id, subject, is_correct)
                    db.atualizar_estatisticas(usuario_id, subject, is_correct)
                    db.atualizar_progresso(usuario_id, is_correct)

                # Marca como respondida
                st.session_state.questoes_respondidas.add(question.id)

                # Mostra resultado
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

            # Exibir tags
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
                        st.session_state.current_question = random.choice(nova_disponivel)
                        st.session_state.show_result = False
                    else:
                        st.session_state.current_question = None
                        st.success("🎉 Você concluiu todas as questões!")
                    st.rerun()
            with col2:
                if st.button("🏠 Voltar ao Início"):
                    st.session_state.current_question = None
                    st.rerun()
