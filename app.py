import streamlit as st
import pandas as pd

st.set_page_config(page_title="Futebol Brasil 2026", layout="wide")

# ========================
# ESTILO DARK
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
    if not isinstance(nome, str):
        return nome

    if "-" in nome:
        partes = nome.split("-")
        
        if len(partes) == 2:
            nome, uf = partes
            return f"{nome.title()} ({uf})"
    
    return nome

# ========================
# CARREGAR DADOS
# ========================
@st.cache_data(ttl=60)
def carregar():
    art = pd.read_excel("br26.xlsx", sheet_name="ART")
    cla = pd.read_excel("br26.xlsx", sheet_name="CLA")
    est = pd.read_excel("br26.xlsx", sheet_name="EST")
    return limpar(art), limpar(cla), limpar(est)

art, cla, est = carregar()

# ========================
# TRATAMENTO
# ========================

# CLASSIFICAÇÃO
cla["TIME"] = cla["TIME"].apply(formatar)

# ARTILHEIROS
art["CLUBE"] = art["CLUBE"].apply(formatar)
art["GOLS"] = pd.to_numeric(art["GOLS"], errors="coerce").fillna(0).astype(int)
art["JOGOS"] = pd.to_numeric(art["JOGOS"], errors="coerce").fillna(0).astype(int)

# ESTRANGEIROS
est["GOLS"] = pd.to_numeric(est["GOLS"], errors="coerce").fillna(0).astype(int)

# ========================
# MENU
# ========================
st.title("⚽ Futebol Brasil 2026")

data_atualizacao = "10/04/2026"

st.markdown(
    f"<p style='color: #aaa; font-size: 13px;'>🔄 Atualizado até: {data_atualizacao}</p>",
    unsafe_allow_html=True
)
pagina = st.sidebar.radio(
    "Menu",
    ["🏠 Home", "📈 Classificação", "🥇 Artilheiros", "🌍 Gols Estrangeiros"]
)

# ========================
# 🏠 HOME
# ========================
if pagina == "🏠 Home":

    total_gols = art["GOLS"].sum()
    total_jogos = int(cla["J"].max())

    time_gols = cla.sort_values(by="GOL", ascending=False).iloc[0]["TIME"]
    time_vitorias = cla.sort_values(by="V", ascending=False).iloc[0]["TIME"]

    artilheiro = art.sort_values(by="GOLS", ascending=False).iloc[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("⚽ Gols", total_gols)
    col2.metric("📊 Jogos", total_jogos)
    col3.metric("🏆 Artilheiro", f"{artilheiro['JOGADOR']} ({artilheiro['GOLS']})")

    st.divider()

    col4, col5 = st.columns(2)
    col4.metric("🔥 Time com mais gols", time_gols)
    col5.metric("🥇 Mais vitórias", time_vitorias)
    st.subheader("🏆 Top 5 Times")

top5 = cla.sort_values(by="PTS", ascending=False).head(5)

st.dataframe(
    top5[["TIME", "PTS", "J", "V", "GOL"]],
    use_container_width=True,
    hide_index=True
)
st.subheader("🥇 Top 5 Artilheiros")

top_art = art.sort_values(by="GOLS", ascending=False).head(5)

st.dataframe(
    top_art[["JOGADOR", "CLUBE", "GOLS"]],
    use_container_width=True,
    hide_index=True
)

# ========================
# 📈 CLASSIFICAÇÃO
# ========================
elif pagina == "📈 Classificação":

    df = cla.copy()

    df = df.sort_values(by="PTS", ascending=False)
    df.insert(0, "POS", [f"{i}º" for i in range(1, len(df)+1)])

    df = df[[
        "POS","TIME","PTS","J","V","E","D",
        "APROVEITAMENTO","GOL","GL","SALDO","MG","MD","CL_SH"
    ]]

    st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

# destaque simples
st.markdown("""
<style>
[data-testid="stDataFrame"] {
    background-color: #0e1117;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ========================
# 🥇 ARTILHEIROS
# ========================
elif pagina == "🥇 Artilheiros":

    df = art.copy()

    df = df.rename(columns={"JOGADOR": "Jogador"})
    df = df.sort_values(by="GOLS", ascending=False)

    df["POS"] = [f"{i}º" for i in range(1, len(df)+1)]
    df = df[["POS"] + [col for col in df.columns if col != "POS"]]

    df = df[["POS", "Jogador", "CLUBE", "GOLS"]]

    st.dataframe(df, use_container_width=True, hide_index=True)

# ========================
# 🌍 GOLS ESTRANGEIROS
# ========================
elif pagina == "🌍 Gols Estrangeiros":

    df = est.copy()
    df = df.sort_values(by="GOLS", ascending=False)

    st.dataframe(df, use_container_width=True, hide_index=True)
