import streamlit as st
import pandas as pd

st.set_page_config(page_title="Futebol Brasil 2026", layout="wide")

# ========================
# ESTILO
# ========================
st.markdown("""
<style>
body { background-color: #0e1117; color: white; }

.card {
    background-color: #161a23;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 15px;
}

.card h3 {
    margin-bottom: 10px;
}

.card p {
    font-size: 20px;
    font-weight: bold;
}

.card span {
    font-size: 16px;
    color: #aaa;
}
</style>
""", unsafe_allow_html=True)

# ========================
# CARREGAR DADOS
# ========================
df_classificacao = pd.read_excel("dados.xlsx", sheet_name="CLASSIFICACAO")

# ========================
# TRATAMENTOS
# ========================

# Média de gols
df_classificacao["MG"] = df_classificacao["GOLS_PRO"] / df_classificacao["JOGOS"]
df_classificacao["MD"] = df_classificacao["GOLS_CONTRA"] / df_classificacao["JOGOS"]

# Aproveitamento (%)
df_classificacao["APROVEITAMENTO"] = (df_classificacao["PONTOS"] / (df_classificacao["JOGOS"] * 3)) * 100

# ========================
# CARDS - CÁLCULOS
# ========================

# Melhor Ataque
df_ataque = df_classificacao.sort_values(by="GOLS_PRO", ascending=False)
top_ataque = df_ataque.iloc[0]

# Menor Média de Gols Levados (critério desempate: mais jogos)
df_defesa = df_classificacao.sort_values(by=["MD", "JOGOS"], ascending=[True, False])
top_defesa = df_defesa.iloc[0]

# Melhor Aproveitamento (critério desempate: mais jogos)
df_aproveitamento = df_classificacao.sort_values(by=["APROVEITAMENTO", "JOGOS"], ascending=[False, False])
top_aproveitamento = df_aproveitamento.iloc[0]

# ========================
# MENU
# ========================
menu = st.sidebar.selectbox("Menu", ["Home", "Média de Gols", "Média de Gols Levados"])

# ========================
# HOME
# ========================
if menu == "Home":

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="card">
            <h3>🔥 Melhor Ataque</h3>
            <p>{top_ataque["CLUBE"]}</p>
            <span>{top_ataque["GOLS_PRO"]} gols</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="card">
            <h3>🛡️ Menor Média de Gols Levados</h3>
            <p>{top_defesa["CLUBE"]}</p>
            <span>{top_defesa["MD"]:.2f}</span>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="card">
            <h3>📊 Melhor Aproveitamento</h3>
            <p>{top_aproveitamento["CLUBE"]}</p>
            <span>{top_aproveitamento["APROVEITAMENTO"]:.2f}%</span>
        </div>
        """, unsafe_allow_html=True)

# ========================
# MÉDIA DE GOLS
# ========================
elif menu == "Média de Gols":

    df_mg = df_classificacao.sort_values(by="MG", ascending=False)

    # formatar duas casas
    df_mg["MG"] = df_mg["MG"].map("{:.2f}".format)

    st.title("⚽ Média de Gols")
    st.dataframe(df_mg[["CLUBE", "MG", "GOLS_PRO", "JOGOS"]], use_container_width=True)

# ========================
# MÉDIA DE GOLS LEVADOS
# ========================
elif menu == "Média de Gols Levados":

    df_md = df_classificacao.sort_values(by="MD", ascending=True)

    # formatar duas casas
    df_md["MD"] = df_md["MD"].map("{:.2f}".format)

    st.title("🛡️ Média de Gols Levados")
    st.dataframe(df_md[["CLUBE", "MD", "GOLS_CONTRA", "JOGOS"]], use_container_width=True)
