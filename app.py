import streamlit as st

# CONFIG
st.set_page_config(page_title="Futebol Brasil", layout="centered")

# DATA (EDITAR TODO DIA)
data_atualizacao = "10/04/2026"

# MENU
pagina = st.sidebar.radio(
    "Menu",
    ["🏠 Início", "📈 Classificação"]
)

# PÁGINA INICIAL
if pagina == "🏠 Início":
    st.title("⚽ Futebol Brasil")

    st.markdown(f"""
    <p style='color: gray;'>🔄 Atualizado em: {data_atualizacao}</p>
    """, unsafe_allow_html=True)

    st.write("---")

    st.write("Bem-vindo ao seu site de resultados 👊")

# CLASSIFICAÇÃO
elif pagina == "📈 Classificação":
    st.title("📈 Classificação")

    st.markdown(f"""
    <p style='color: gray;'>🔄 Atualizado em: {data_atualizacao}</p>
    """, unsafe_allow_html=True)

    st.write("---")

    st.write("Aqui vai sua tabela depois...")
