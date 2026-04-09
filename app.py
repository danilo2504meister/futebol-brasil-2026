import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Futebol Brasil 2026",
    page_icon="⚽",
    layout="wide"
)

# ========================
# CARREGAR DADOS
# ========================
@st.cache_data
def carregar():
    arquivo = "br26.xlsx"
    cal = pd.read_excel(arquivo, sheet_name="CAL")
    art = pd.read_excel(arquivo, sheet_name="ART")
    cla = pd.read_excel(arquivo, sheet_name="CLA")
    return cal, art, cla

cal, art, cla = carregar()

# ========================
# TÍTULO
# ========================
st.title("⚽ Futebol Brasil 2026")

pagina = st.sidebar.radio(
    "Menu",
    ["🏠 Home", "📊 Resultados", "🥇 Artilheiros", "📈 Classificação"]
)

# ========================
# 🏠 HOME
# ========================
if pagina == "🏠 Home":

    total_gols = int(cal["GM"].sum() + cal["GV"].sum())

    # Time com mais gols
    gols_time = cal.groupby("Mandante")["GM"].sum()
    top_gols_time = gols_time.idxmax()
    top_gols_valor = int(gols_time.max())

    # Classificação
    cla2 = cla.copy()

    # Melhor time (pontos)
    top_time = cla2.sort_values(by="PTS", ascending=False).iloc[0]["EQUIPE"]

    # Mais vitórias
    top_vitorias = cla2.sort_values(by="V", ascending=False).iloc[0]["EQUIPE"]

    # Melhor aproveitamento
    cla2["APROV"] = (cla2["PTS"] / (cla2["J"] * 3)) * 100
    top_aprov = cla2.sort_values(by="APROV", ascending=False).iloc[0]["EQUIPE"]

    # Artilheiro
    art2 = art.copy()
    art2["GOLS"] = art2["GOLS"].astype(int)
    artilheiro = art2.sort_values(by="GOLS", ascending=False).iloc[0]

    col1, col2, col3 = st.columns(3)
    col4, col5 = st.columns(2)

    col1.metric("⚽ Total de Gols", total_gols)
    col2.metric("🥇 Artilheiro", f"{artilheiro['z']} ({artilheiro['GOLS']})")
    col3.metric("🔥 Time + Gols", f"{top_gols_time} ({top_gols_valor})")

    col4.metric("🏆 Líder", top_time)
    col5.metric("📊 Melhor Aproveitamento", top_aprov)

    st.divider()

# ========================
# 📊 RESULTADOS
# ========================
elif pagina == "📊 Resultados":

    st.subheader("📊 Resultados")

    df = cal.copy()
    df["Data"] = pd.to_datetime(df["Data"]).dt.date

    df["Placar"] = (
        df["Mandante"] + " " +
        df["GM"].astype(int).astype(str) +
        " x " +
        df["GV"].astype(int).astype(str)
    )

    df = df[["Data", "Placar"]]

    st.dataframe(df, use_container_width=True)

# ========================
# 🥇 ARTILHEIROS
# ========================
elif pagina == "🥇 Artilheiros":

    st.subheader("🥇 Artilheiros")

    df = art.copy()

    df["GOLS"] = df["GOLS"].astype(int)
    df["JOGOS"] = df["JOGOS"].astype(int)

    df = df.rename(columns={
        "z": "Jogador",
        "CLUBE": "Clube"
    })

    df = df.sort_values(by="GOLS", ascending=False)

    # Ranking
    df.insert(0, "Pos", [f"{i}º" for i in range(1, len(df)+1)])

    df = df[["Pos", "Jogador", "Clube", "GOLS", "JOGOS"]]

    st.dataframe(df, use_container_width=True)

# ========================
# 📈 CLASSIFICAÇÃO
# ========================
elif pagina == "📈 Classificação":

    st.subheader("📈 Classificação")

    df = cla.copy()

    df = df.rename(columns={
        "EQUIPE": "Time"
    })

    # Aproveitamento %
    df["Aprov (%)"] = ((df["PTS"] / (df["J"] * 3)) * 100).round(1)

    # Ranking
    df = df.sort_values(by="PTS", ascending=False)
    df.insert(0, "Pos", [f"{i}º" for i in range(1, len(df)+1)])

    # Seleção de colunas (ajustada)
    colunas = [
        "Pos", "Time", "PTS", "J", "V", "E", "D",
        "Aprov (%)", "GL", "MG", "MD", "CL SH"
    ]

    df = df[colunas]

    st.dataframe(df, use_container_width=True)

    st.markdown("""
    **Legenda:**

    V - Vitórias  
    E - Empates  
    D - Derrotas  
    Aprov - Aproveitamento de Pontos (%)  
    GL - Gols Levados  
    MG - Média de Gols por jogo  
    MD - Média de Gols sofridos por jogo  
    CL SH - Clean Sheets (jogos sem sofrer gols)
    """)
