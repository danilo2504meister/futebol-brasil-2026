import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Futebol Brasil 2026",
    page_icon="⚽",
    layout="wide"
)

# ========================
# ESTILO
# ========================
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
h1, h2, h3 {
    color: #00ff88;
}
.block-container {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ========================
# CARREGAMENTO
# ========================
@st.cache_data
def carregar_dados():
    arquivo = "br26.xlsx"
    cal = pd.read_excel(arquivo, sheet_name="CAL")
    art = pd.read_excel(arquivo, sheet_name="ART")
    cla = pd.read_excel(arquivo, sheet_name="CLA")
    return cal, art, cla

cal, art, cla = carregar_dados()

# ========================
# TÍTULO
# ========================
st.title("⚽ Futebol Brasil 2026")
st.caption("Resultados • Estatísticas • Artilheiros • Classificação")

# ========================
# MENU
# ========================
pagina = st.sidebar.radio(
    "📌 Menu",
    ["🏠 Início", "📅 Jogos do Dia", "📊 Resultados", "🥇 Artilheiros", "📈 Classificação"]
)

# ========================
# INÍCIO
# ========================
if pagina == "🏠 Início":

    total_jogos = len(cal)
    total_gols = cal["GM"].sum() + cal["GV"].sum()
    media = round(total_gols / total_jogos, 2)

    col1, col2, col3 = st.columns(3)
    col1.metric("Jogos", total_jogos)
    col2.metric("Gols", total_gols)
    col3.metric("Média", media)

    st.divider()

    st.subheader("🔥 Top 10 Artilheiros")
    top = art.sort_values(by="GOLS", ascending=False).head(10)

    st.dataframe(top, use_container_width=True)

# ========================
# JOGOS DO DIA
# ========================
elif pagina == "📅 Jogos do Dia":

    st.subheader("📅 Jogos do Dia")

    data_escolhida = st.date_input("Escolha a data")

    df = cal.copy()
    df["Data"] = pd.to_datetime(df["Data"]).dt.date

    df = df[df["Data"] == data_escolhida]

    if df.empty:
        st.warning("Nenhum jogo nesta data.")
    else:
        df = df[["Data", "Mandante", "GM", "GV"]]
        df.columns = ["Data", "Time", "Gols Casa", "Gols Fora"]
        st.dataframe(df, use_container_width=True)

# ========================
# RESULTADOS
# ========================
elif pagina == "📊 Resultados":

    st.subheader("📊 Resultados")

    col1, col2 = st.columns(2)

    with col1:
        time = st.selectbox(
            "Time",
            ["Todos"] + sorted(cal["Mandante"].unique())
        )

    with col2:
        data = st.date_input("Filtrar por data")

    df = cal.copy()
    df["Data"] = pd.to_datetime(df["Data"]).dt.date

    if time != "Todos":
        df = df[df["Mandante"] == time]

    if data:
        df = df[df["Data"] == data]

    df = df[["Data", "Mandante", "GM", "GV"]]
    df.columns = ["Data", "Time", "Gols Casa", "Gols Fora"]

    st.dataframe(df, use_container_width=True)

# ========================
# ARTILHEIROS
# ========================
elif pagina == "🥇 Artilheiros":

    st.subheader("🥇 Artilheiros")

    df = art.rename(columns={
        "z": "Jogador",
        "CLUBE": "Clube"
    })

    df = df.sort_values(by="GOLS", ascending=False)

    top_n = st.slider("Top", 5, 50, 10)

    for i, row in df.head(top_n).iterrows():
        st.markdown(f"""
        **{row['Jogador']}** ({row['Clube']})  
        ⚽ {row['GOLS']} gols | 🎮 {row['JOGOS']} jogos
        """)
        st.divider()

# ========================
# CLASSIFICAÇÃO
# ========================
elif pagina == "📈 Classificação":

    st.subheader("📈 Classificação")

    df = cla.rename(columns={
        "EQUIPE": "Time",
        "PTS": "Pontos",
        "J": "Jogos"
    })

    df = df.sort_values(by="Pontos", ascending=False)

    st.dataframe(df, use_container_width=True)