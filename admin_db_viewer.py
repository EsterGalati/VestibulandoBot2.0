import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "vestibulando.db"

def conectar():
    return sqlite3.connect(DB_PATH)

def carregar_tabelas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tabelas = [linha[0] for linha in cursor.fetchall()]
    conn.close()
    return tabelas

def visualizar_tabela(tabela):
    conn = conectar()
    df = pd.read_sql_query(f"SELECT * FROM {tabela}", conn)
    conn.close()
    return df

def apagar_registro(tabela, id_coluna, id_valor):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {tabela} WHERE {id_coluna} = ?", (id_valor,))
    conn.commit()
    conn.close()

st.title("📋 Editor de Banco de Dados - VestibulandoBot")

tabelas = carregar_tabelas()
tabela_selecionada = st.selectbox("Selecione a tabela:", tabelas)

if tabela_selecionada:
    df = visualizar_tabela(tabela_selecionada)
    st.dataframe(df, use_container_width=True)

    # Exclusão de registros simples (opcional)
    if not df.empty:
        st.markdown("### ❌ Excluir Registro")
        id_coluna = df.columns[0]
        id_valor = st.selectbox("Selecione o ID a excluir:", df[id_coluna].tolist())
        if st.button("Excluir"):
            apagar_registro(tabela_selecionada, id_coluna, id_valor)
            st.success(f"Registro {id_valor} excluído com sucesso.")
            st.rerun()
