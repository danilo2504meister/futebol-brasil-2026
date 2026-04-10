import streamlit as st
import pandas as pd
import pandas as pd

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS8FNFEix6fpe4BjPHxJochxu1WfhugBQJ-1jMg_Y0N5CE5XaCHqqzKe2TMrEFwIA/pubhtml"

df = pd.read_csv(url)

print(df.head())

st.set_page_config(page_title="Futebol Brasil 2026", layout="wide")

# ========================
# ESTILO DARK PROFISSIONAL
# ========================
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: white;
}
.block-container {
    padding-top: 2rem;
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
# CARREGAR DADOS
# ========================
@st.cache_data(ttl=60)
def carregar():
    cal = pd.read_excel("br26.xlsx", sheet_name="CAL")
    art = pd.read_excel("br26.xlsx", sheet_name="ART")
    cla = pd.read_excel("br26.xlsx", sheet_name="CLA")
    return limpar(cal), limpar(art), limpar(cla)

cal, art, cla = carregar()

# formatar nomes
cal["MANDANTE"] = cal["MANDANTE"].apply(formatar)
cal["VISITANTE"] = cal["VISITANTE"].apply(formatar)
cla["EQUIPE"] = cla["EQUIPE"].apply(formatar)
art["CLUBE"] = art["CLUBE"].apply(formatar)

# ========================
# MENU
# ========================
st.title("⚽ Futebol Brasil 2026")

pagina = st.sidebar.radio(
    "Menu",
    ["🏠 Home", "📊 Jogos", "🥇 Artilheiros", "📈 Classificação"]
)

# ========================
# 🏠 HOME
# ========================
if pagina == "🏠 Home":

    total_gols = int(cal["GM"].sum() + cal["GV"].sum())
    total_jogos = len(cal)
    media = round(total_gols / total_jogos, 2)

    col1, col2, col3 = st.columns(3)
    col1.metric("⚽ Gols", total_gols)
    col2.metric("📊 Jogos", total_jogos)
    col3.metric("📈 Média", media)

    st.divider()

    # destaques
    time_jogos = cla.sort_values(by="J", ascending=False).iloc[0]["EQUIPE"]
    time_vitorias = cla.sort_values(by="V", ascending=False).iloc[0]["EQUIPE"]

    gols_time = cal.groupby("MANDANTE")["GM"].sum()
    time_gols = gols_time.idxmax()

    art["GOLS"] = pd.to_numeric(art["GOLS"], errors="coerce").fillna(0).astype(int)
    artilheiro = art.sort_values(by="GOLS", ascending=False).iloc[0]

    col4, col5 = st.columns(2)
    col6, col7 = st.columns(2)

    col4.metric("Mais Jogos", time_jogos)
    col5.metric("Mais Vitórias", time_vitorias)
    col6.metric("Mais Gols", time_gols)
    col7.metric("Artilheiro", f"{artilheiro['Z']} ({artilheiro['GOLS']})")

# ========================
# 📊 JOGOS
# ========================
elif pagina == "📊 Jogos":

    st.subheader("Resultados")

    df = cal.copy()

    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce").dt.date
    df["GM"] = pd.to_numeric(df["GM"], errors="coerce").fillna(0).astype(int)
    df["GV"] = pd.to_numeric(df["GV"], errors="coerce").fillna(0).astype(int)

    col1, col2 = st.columns(2)

    with col1:
        data = st.date_input("Filtrar por data")

    with col2:
        time = st.selectbox(
            "Buscar time",
            ["Todos"] + sorted(df["MANDANTE"].dropna().unique())
        )

    if data:
        df = df[df["DATA"] == data]

    if time != "Todos":
        df = df[(df["MANDANTE"] == time) | (df["VISITANTE"] == time)]

    df = df.sort_values(by="DATA", ascending=False)

    for _, row in df.iterrows():

        col1, col2, col3 = st.columns([3,1,3])

        col1.markdown(f"**{row['MANDANTE']}**")
        col2.markdown(f"### {row['GM']} x {row['GV']}")
        col3.markdown(f"**{row['VISITANTE']}**")

        st.caption(f"{row['DATA']} | {row.get('CAMPEONATO','')}")
        st.divider()

# ========================
# 🥇 ARTILHEIROS
# ========================
elif pagina == "🥇 Artilheiros":

    df = art.copy()

    df["GOLS"] = pd.to_numeric(df["GOLS"], errors="coerce").fillna(0).astype(int)
    df["JOGOS"] = pd.to_numeric(df["JOGOS"], errors="coerce").fillna(0).astype(int)

    df = df.rename(columns={"Z": "Jogador"})
    df = df.sort_values(by="GOLS", ascending=False)

    df.insert(0, "Pos", [f"{i}º" for i in range(1, len(df)+1)])

    remover = ["COD", "COLUNA1", "HORA DE NASCIMENTO"]
    df = df.drop(columns=[c for c in remover if c in df.columns], errors="ignore")

    df = df[["Pos", "Jogador", "CLUBE", "GOLS", "JOGOS"]]

    st.dataframe(df, use_container_width=True)

# ========================
# 📈 CLASSIFICAÇÃO
# ========================
elif pagina == "📈 Classificação":

    df = cla.copy()

    df["APROV"] = ((df["PTS"] / (df["J"] * 3)) * 100).round(2)
    df["MG"] = df["MG"].round(2)

    df = df.sort_values(by="PTS", ascending=False)
    df.insert(0, "Pos", [f"{i}º" for i in range(1, len(df)+1)])

    df = df[["Pos", "EQUIPE", "PTS", "J", "V", "E", "D", "APROV", "GL", "MG"]]

    # zebra
    def zebra(row):
        return ['background-color: #1a1a1a' if row.name % 2 == 0 else '' for _ in row]

    st.dataframe(
        df.style.apply(zebra, axis=1),
        use_container_width=True
    )

    st.markdown("""
    V - Vitórias | E - Empates | D - Derrotas  
    Aprov - Aproveitamento (%)  
    GL - Gols Levados | MG - Média de gols  
    """)
