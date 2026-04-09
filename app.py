import streamlit as st
import pandas as pd

st.set_page_config(page_title="Futebol Brasil 2026", layout="wide")

# ========================
# ESTILO FLASHSCORE
# ========================
st.markdown("""
<style>
body {
    background-color: #0b0e11;
}
h1, h2, h3 {
    color: #00ffcc;
}
[data-testid="stMetric"] {
    background-color: #111;
    padding: 15px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ========================
# FUNÇÕES
# ========================
def limpar(df):
    df.columns = df.columns.str.strip().str.upper()
    return df

def formatar_time(nome):
    if isinstance(nome, str) and "-" in nome:
        partes = nome.split("-")
        return f"{partes[0].title()} ({partes[1]})"
    return nome

# ========================
# CARREGAR DADOS
# ========================
@st.cache_data
def carregar():
    cal = pd.read_excel("br26.xlsx", sheet_name="CAL")
    art = pd.read_excel("br26.xlsx", sheet_name="ART")
    cla = pd.read_excel("br26.xlsx", sheet_name="CLA")

    return limpar(cal), limpar(art), limpar(cla)

cal, art, cla = carregar()

# FORMATAR TIMES
cal["MANDANTE"] = cal["MANDANTE"].apply(formatar_time)
cla["EQUIPE"] = cla["EQUIPE"].apply(formatar_time)
art["CLUBE"] = art["CLUBE"].apply(formatar_time)

# ========================
# MENU
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

    art["GOLS"] = art["GOLS"].fillna(0).astype(int)
    top3 = art.sort_values(by="GOLS", ascending=False).head(3)

    cla["APROV"] = (cla["PTS"] / (cla["J"] * 3)) * 100
    lider = cla.sort_values(by="PTS", ascending=False).iloc[0]

    col1, col2 = st.columns(2)

    col1.metric("⚽ Total de Gols", total_gols)
    col2.metric("🏆 Líder", lider["EQUIPE"])

    st.divider()

    st.subheader("🥇 Top 3 Artilheiros")

    for i, row in top3.iterrows():
        st.markdown(f"""
        **{row['Z']}** - {row['CLUBE']}  
        ⚽ {row['GOLS']} gols
        """)
        st.divider()

# ========================
# 📊 RESULTADOS
# ========================
elif pagina == "📊 Resultados":

    st.subheader("Resultados")

    df = cal.copy()

    df["DATA"] = pd.to_datetime(df["DATA"]).dt.date

    time = st.selectbox(
        "Filtrar por time",
        ["Todos"] + sorted(df["MANDANTE"].unique())
    )

    if time != "Todos":
        df = df[df["MANDANTE"] == time]

    df["PLACAR"] = (
        df["MANDANTE"] + " " +
        df["GM"].fillna(0).astype(int).astype(str) +
        " x " +
        df["GV"].fillna(0).astype(int).astype(str)
    )

    df = df[["DATA", "PLACAR"]]

    st.dataframe(df, use_container_width=True)

# ========================
# 🥇 ARTILHEIROS
# ========================
elif pagina == "🥇 Artilheiros":

    st.subheader("Artilheiros")

    df = art.copy()

    df["GOLS"] = df["GOLS"].fillna(0).astype(int)
    df["JOGOS"] = df["JOGOS"].fillna(0).astype(int)

    df = df.rename(columns={
        "Z": "Jogador",
        "CLUBE": "Clube"
    })

    df = df.sort_values(by="GOLS", ascending=False)

    df["Pos"] = [f"{i}º" for i in range(1, len(df)+1)]

    # destaque top 3
    top3 = df.head(3)

    st.subheader("🔥 Destaque")
    st.dataframe(top3, use_container_width=True)

    st.subheader("📋 Ranking Completo")
    st.dataframe(df, use_container_width=True)

# ========================
# 📈 CLASSIFICAÇÃO
# ========================
elif pagina == "📈 Classificação":

    st.subheader("Classificação")

    df = cla.copy()

    df["APROV (%)"] = ((df["PTS"] / (df["J"] * 3)) * 100).round(1)

    df = df.sort_values(by="PTS", ascending=False)

    # coluna fixa posição
    df["Classificação"] = [f"{i}º" for i in range(1, len(df)+1)]

    df = df[[
        "Classificação", "EQUIPE", "PTS", "J", "V", "E", "D",
        "APROV (%)", "GL", "MG", "MD", "CL SH"
    ]]

    # destacar líder
    st.dataframe(
        df.style.apply(
            lambda x: ['background-color: #1f7a1f' if x.name == 0 else '' for _ in x],
            axis=1
        ),
        use_container_width=True
    )

    st.markdown("""
    **Legenda:**

    V - Vitórias  
    E - Empates  
    D - Derrotas  
    Aprov - Aproveitamento (%)  
    GL - Gols Levados  
    MG - Média de gols  
    MD - Média sofridos  
    CL SH - Clean Sheets
    """)
