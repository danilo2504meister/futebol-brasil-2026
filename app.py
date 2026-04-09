import streamlit as st
import pandas as pd

st.set_page_config(page_title="Futebol Brasil 2026", layout="wide")

# ========================
# ESTILO MODERNO
# ========================
st.markdown("""
<style>
body {
    background-color: #f4f6f9;
}
.block-container {
    padding-top: 2rem;
}
.card {
    background: white;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 12px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
}
.score {
    font-size: 22px;
    font-weight: bold;
    text-align: center;
}
.team {
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ========================
# FUNÇÕES
# ========================
def limpar(df):
    df.columns = df.columns.str.strip().str.upper()
    return df

def formatar(nome):
    if isinstance(nome, str) and "-" in nome:
        nome, uf = nome.split("-")
        return f"{nome.title()} ({uf})"
    return nome

# ========================
# DADOS
# ========================
@st.cache_data(ttl=60)
def carregar():
    cal = pd.read_excel("br26.xlsx", sheet_name="CAL")
    art = pd.read_excel("br26.xlsx", sheet_name="ART")
    cla = pd.read_excel("br26.xlsx", sheet_name="CLA")
    return limpar(cal), limpar(art), limpar(cla)

cal, art, cla = carregar()

cal["MANDANTE"] = cal["MANDANTE"].apply(formatar)
cal["VISITANTE"] = cal["VISITANTE"].apply(formatar)

st.title("⚽ Futebol Brasil 2026")

pagina = st.sidebar.radio(
    "Menu",
    ["🏠 Home", "📊 Jogos", "🥇 Artilheiros", "📈 Classificação"]
)

# ========================
# HOME
# ========================
if pagina == "🏠 Home":

    total_gols = int(cal["GM"].sum() + cal["GV"].sum())
    total_jogos = len(cal)
    media = round(total_gols / total_jogos, 2)

    col1, col2, col3 = st.columns(3)
    col1.metric("Gols", total_gols)
    col2.metric("Jogos", total_jogos)
    col3.metric("Média", media)

    st.markdown('<div class="card">Espaço para publicidade</div>', unsafe_allow_html=True)

# ========================
# JOGOS (ESTILO APP)
# ========================
elif pagina == "📊 Jogos":

    df = cal.copy()

    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce").dt.date
    df["GM"] = pd.to_numeric(df["GM"], errors="coerce").fillna(0).astype(int)
    df["GV"] = pd.to_numeric(df["GV"], errors="coerce").fillna(0).astype(int)

    col1, col2 = st.columns(2)

    with col1:
        data = st.date_input("Data")

    with col2:
        time = st.selectbox(
            "Time",
            ["Todos"] + sorted(df["MANDANTE"].dropna().unique())
        )

    if data:
        df = df[df["DATA"] == data]

    if time != "Todos":
        df = df[(df["MANDANTE"] == time) | (df["VISITANTE"] == time)]

    df = df.sort_values(by="DATA", ascending=False)

    for _, row in df.iterrows():
        st.markdown(f"""
        <div class="card">
            <div style="display:flex; justify-content:space-between;">
                <div class="team">{row['MANDANTE']}</div>
                <div class="score">{row['GM']} x {row['GV']}</div>
                <div class="team">{row['VISITANTE']}</div>
            </div>
            <div style="text-align:center; font-size:12px; color:gray;">
                {row['DATA']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ========================
# ARTILHEIROS
# ========================
elif pagina == "🥇 Artilheiros":

    df = art.copy()

    df["GOLS"] = pd.to_numeric(df["GOLS"], errors="coerce").fillna(0).astype(int)
    df["JOGOS"] = pd.to_numeric(df["JOGOS"], errors="coerce").fillna(0).astype(int)

    df = df.rename(columns={"Z": "Jogador"})
    df = df.sort_values(by="GOLS", ascending=False)

    df.insert(0, "Pos", [f"{i}º" for i in range(1, len(df)+1)])

    df = df[["Pos", "Jogador", "CLUBE", "GOLS", "JOGOS"]]

    st.dataframe(df, use_container_width=True)

# ========================
# CLASSIFICAÇÃO
# ========================
elif pagina == "📈 Classificação":

    df = cla.copy()

    df["APROV"] = ((df["PTS"] / (df["J"] * 3)) * 100).round(2)
    df["MG"] = df["MG"].round(2)

    df = df.sort_values(by="PTS", ascending=False)
    df.insert(0, "Pos", [f"{i}º" for i in range(1, len(df)+1)])

    df = df[["Pos", "EQUIPE", "PTS", "J", "V", "E", "D", "APROV", "GL", "MG"]]

    st.dataframe(df, use_container_width=True)
