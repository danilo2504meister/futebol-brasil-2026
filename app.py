import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Futebol Brasil 2026", layout="wide")

# ========================
# ESTILO
# ========================
st.markdown("""
<style>
body { background-color: #0e1117; color: white; }
[data-testid="stDataFrame"] { background-color: #0e1117; color: white; }
th, td { text-align: center !important; }
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
        partes = nome.split("-")
        if len(partes) == 2:
            return f"{partes[0].title()} ({partes[1]})"
    return nome

# 🔥 FUNÇÃO DE ESCUDO (PADRÃO COM UF)
def escudo_time(nome):
    if not isinstance(nome, str):
        return None

    nome = nome.lower()
    nome = nome.replace(" ", "").replace("(", "").replace(")", "")

    caminho = f"escudos/{nome}.png"

    if os.path.exists(caminho):
        return caminho
    else:
        return None

def bandeira(pais):
    flags = {
        "BRA": "🇧🇷", "ARG": "🇦🇷", "URU": "🇺🇾",
        "PAR": "🇵🇾", "COL": "🇨🇴", "CHI": "🇨🇱",
        "PER": "🇵🇪", "VEN": "🇻🇪"
    }
    return flags.get(pais, "")

# ========================
# DADOS
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
cla["TIME"] = cla["TIME"].apply(formatar)
art["CLUBE"] = art["CLUBE"].apply(formatar)

art["GOLS"] = pd.to_numeric(art["GOLS"], errors="coerce").fillna(0)
art["JOGOS"] = pd.to_numeric(art["JOGOS"], errors="coerce").fillna(0)

# ========================
# HEADER
# ========================
st.title("⚽ Futebol Brasil 2026")
data_atualizacao = "10/04/2026"
st.markdown(f"🔄 Atualizado até: {data_atualizacao}")

pagina = st.sidebar.radio(
    "Menu",
    ["🏠 Home", "📈 Classificação", "🥇 Artilheiros", "🌍 Gols Estrangeiros", "📊 Invencibilidade"]
)

# ========================
# 🏠 HOME
# ========================
if pagina == "🏠 Home":

    total_gols = int(art["GOLS"].sum())
    total_jogos = int(cla["J"].sum())

    top_gols = cla.sort_values(by="GOL", ascending=False).iloc[0]
    top_vit = cla.sort_values(by="V", ascending=False).iloc[0]

    artilheiro = art.sort_values(by="GOLS", ascending=False).iloc[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("⚽ Gols", total_gols)
    col2.metric("📊 Jogos", total_jogos)
    col3.metric("🏆 Artilheiro", f"{artilheiro['JOGADOR']} - {int(artilheiro['GOLS'])}")

    st.divider()

    col4, col5 = st.columns(2)

    # MAIS GOLS
    with col4:
        c1, c2 = st.columns([1, 4])

        with c1:
            escudo = escudo_time(top_gols["TIME"])
            if escudo:
                st.image(escudo, width=50)

        with c2:
            st.markdown("🔥 **Mais gols**")
            st.markdown(f"### {top_gols['TIME']} - {int(top_gols['GOL'])}")

    # MAIS VITÓRIAS
    with col5:
        c1, c2 = st.columns([1, 4])

        with c1:
            escudo = escudo_time(top_vit["TIME"])
            if escudo:
                st.image(escudo, width=50)

        with c2:
            st.markdown("🥇 **Mais vitórias**")
            st.markdown(f"### {top_vit['TIME']} - {int(top_vit['V'])}")

# ========================
# 📈 CLASSIFICAÇÃO
# ========================
elif pagina == "📈 Classificação":

    df = cla.copy()

    df = df.sort_values(by=["PTS","V","SALDO","GOL"], ascending=False)

    col_remover = ["UNNAMED: 0","EQUIPE","INV","VIT","EMP","DIVISÃO NACIONAL","CIDADE","UF"]
    df = df.drop(columns=[c for c in col_remover if c in df.columns])

    df["APROVEITAMENTO"] = df["APROVEITAMENTO"].astype(float).round(2)
    df["MG"] = df["MG"].astype(float).round(2)
    df["MD"] = df["MD"].astype(float).round(2)

    df.insert(0, "POS", range(1, len(df)+1))

    st.dataframe(df, use_container_width=True, hide_index=True)

# ========================
# 🥇 ARTILHEIROS
# ========================
elif pagina == "🥇 Artilheiros":

    df = art.copy()
    df = df.sort_values(by="GOLS", ascending=False)

    df["POS"] = df["GOLS"].rank(method="min", ascending=False).astype(int)

    df = df[["POS","JOGADOR","CLUBE","GOLS"]]

    st.dataframe(df, use_container_width=True, hide_index=True)

# ========================
# 🌍 GOLS ESTRANGEIROS
# ========================
elif pagina == "🌍 Gols Estrangeiros":

    df = est.copy()

    if "PAIS" in df.columns:
        df["PAIS"] = df["PAIS"].apply(lambda x: f"{bandeira(x)} {x}")

    df = df.sort_values(by="GOLS", ascending=False)

    st.dataframe(df, use_container_width=True, hide_index=True)

# ========================
# 📊 INVENCIBILIDADE
# ========================
elif pagina == "📊 Invencibilidade":

    df = cla.copy()

    df = df[["TIME","INV","VIT","EMP"]]
    df = df[df["INV"].notna()]

    df = df.sort_values(by="INV", ascending=False)

    st.dataframe(df, use_container_width=True, hide_index=True)
