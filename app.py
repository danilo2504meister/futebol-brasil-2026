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

def escudo_time(nome):
    if not isinstance(nome, str):
        return None
    nome = nome.lower().replace(" ", "").replace("(", "").replace(")", "")
    caminho = f"escudos/{nome}.png"
    return caminho if os.path.exists(caminho) else None

def bandeira(pais):
    flags = {
        "BRA": "🇧🇷","ARG": "🇦🇷","URU": "🇺🇾","PAR": "🇵🇾","COL": "🇨🇴",
        "CHI": "🇨🇱","PER": "🇵🇪","VEN": "🇻🇪","EQU": "🇪🇨","NIG": "🇳🇬",
        "GAN": "🇬🇭","FRA": "🇫🇷","BEL": "🇧🇪","TOG": "🇹🇬","ANG": "🇦🇴",
        "BOL": "🇧🇴","ESP": "🇪🇸","EUA": "🇺🇸","HAI": "🇭🇹","MEX": "🇲🇽","HOL": "🇳🇱"
    }
    return flags.get(pais, "")

def ordinal(x):
    return f"{int(x)}º"

def ranking(df, colunas, asc):
    df = df.sort_values(by=colunas, ascending=asc).reset_index(drop=True)
    df["POS"] = df[colunas].apply(tuple, axis=1).rank(method="min", ascending=asc[0]).astype(int)
    df = df.sort_values(by="POS")
    df["POS"] = df["POS"].apply(ordinal)
    return df

# ========================
# DADOS
# ========================
@st.cache_data(ttl=60)
def carregar():
    art = pd.read_excel("br26.xlsx", sheet_name="ART")
    cla = pd.read_excel("br26.xlsx", sheet_name="CLA")
    est = pd.read_excel("br26.xlsx", sheet_name="EST")
    cal = pd.read_excel("br26.xlsx", sheet_name="CAL")
    return limpar(art), limpar(cla), limpar(est), limpar(cal)

art, cla, est, cal = carregar()

# ========================
# TRATAMENTO
# ========================
cla["TIME"] = cla["TIME"].apply(formatar)
art["CLUBE"] = art["CLUBE"].apply(formatar)

art["GOLS"] = pd.to_numeric(art["GOLS"], errors="coerce").fillna(0)
art["JOGOS"] = pd.to_numeric(art["JOGOS"], errors="coerce").fillna(0)

# ========================
# MENU
# ========================
pagina = st.sidebar.radio(
    "Menu",
    [
        "🏠 Home",
        "🥇 Artilheiros",
        "🌍 Artilheiros Estrangeiros",
        "🌎 Gols por País",
        "📊 Invencibilidade",
        "🔥 Melhores Ataques",
        "📈 Média de Gols",
        "🏆 Vitórias",
        "🛡️ Média de Gols Levados",
        "📊 Aproveitamento",
        "🚫 Clean Sheets"
    ]
)

# ========================
# TÍTULOS DINÂMICOS
# ========================
titulos = {
    "🏠 Home": "⚽ Futebol Brasil 2026",
    "🥇 Artilheiros": "🥇 Artilheiros",
    "🌍 Artilheiros Estrangeiros": "🌍 Artilheiros Estrangeiros",
    "🌎 Gols por País": "🌎 Gols por País",
    "📊 Invencibilidade": "📊 Invencibilidade",
    "🔥 Melhores Ataques": "🔥 Melhores Ataques",
    "📈 Média de Gols": "📈 Média de Gols",
    "🏆 Vitórias": "🏆 Vitórias",
    "🛡️ Média de Gols Levados": "🛡️ Média de Gols Levados",
    "📊 Aproveitamento": "📊 Aproveitamento",
    "🚫 Clean Sheets": "🚫 Clean Sheets"
}

st.title(titulos.get(pagina, "⚽ Futebol Brasil 2026"))
st.markdown("🔄 Atualizado até: 13/04/2026")

# ========================
# HOME
# ========================
if pagina == "🏠 Home":

    total_gols = int((cal["GM"] + cal["GV"]).sum())
    total_jogos = len(cal)

    top_gols = cla.sort_values(by="GOL", ascending=False).iloc[0]
    top_vit = cla.sort_values(by="V", ascending=False).iloc[0]
    artilheiro = art.sort_values(by="GOLS", ascending=False).iloc[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("⚽ Gols", total_gols)
    col2.metric("📊 Jogos", total_jogos)
    col3.metric("🏆 Artilheiro", f"{artilheiro['JOGADOR']} - {int(artilheiro['GOLS'])}")

# ========================
# ARTILHEIROS
# ========================
elif pagina == "🥇 Artilheiros":

    df = art.copy()
    df = df.sort_values(by=["GOLS","JOGADOR"], ascending=[False, True])
    df["POS"] = df["GOLS"].rank(method="min", ascending=False).astype(int)
    df = df.sort_values(by=["POS","JOGADOR"])
    df["POS"] = df["POS"].apply(ordinal)

    st.dataframe(df[["POS","JOGADOR","CLUBE","GOLS"]], use_container_width=True, hide_index=True)

# ========================
# ARTILHEIROS ESTRANGEIROS
# ========================
elif pagina == "🌍 Artilheiros Estrangeiros":

    df = art.copy()
    df = df[df["PAIS"].notna()]
    df = df[df["PAIS"].str.strip() != ""]
    df = df[~df["PAIS"].str.upper().isin(["BRA","BRASIL"])]

    df["PAIS"] = df["PAIS"].apply(lambda x: f"{bandeira(x)} {x}")
    df = df.sort_values(by=["GOLS","JOGADOR"], ascending=[False, True])
    df["POS"] = df["GOLS"].rank(method="min", ascending=False).astype(int)
    df = df.sort_values(by=["POS","JOGADOR"])
    df["POS"] = df["POS"].apply(ordinal)

    st.dataframe(df[["POS","JOGADOR","CLUBE","GOLS","PAIS"]], use_container_width=True, hide_index=True)

# ========================
# GOLS POR PAÍS
# ========================
elif pagina == "🌎 Gols por País":

    df = est.copy()
    df = df[df["PAIS"].notna()]
    df = df[df["PAIS"].str.strip() != ""]
    df["PAIS"] = df["PAIS"].apply(lambda x: f"{bandeira(x)} {x}")

    df = ranking(df, ["GOLS"], [False])

    st.dataframe(df[["POS","PAIS","GOLS"]], use_container_width=True, hide_index=True)

# ========================
# INVENCIBILIDADE
# ========================
elif pagina == "📊 Invencibilidade":

    df = cla.copy()
    df = df[["TIME","INV","VIT","EMP"]]
    df = df[df["INV"].notna()]
    df = df.sort_values(by="INV", ascending=False)

    st.dataframe(df, use_container_width=True, hide_index=True)

# ========================
# MELHORES ATAQUES
# ========================
elif pagina == "🔥 Melhores Ataques":

    df = cla[["TIME","GOL","J"]].copy()
    df = ranking(df, ["GOL","J"], [False, True])

    st.dataframe(df[["POS","TIME","GOL","J"]], use_container_width=True, hide_index=True)

# ========================
# MÉDIA DE GOLS
# ========================
elif pagina == "📈 Média de Gols":

    df = cla.copy()
    df["MG"] = (df["GOL"] / df["J"]).round(2)

    df = ranking(df, ["MG","GOL","J"], [False, False, False])

    st.dataframe(df[["POS","TIME","MG","GOL","J"]], use_container_width=True, hide_index=True)

# ========================
# VITÓRIAS
# ========================
elif pagina == "🏆 Vitórias":

    df = cla[["TIME","V","J"]].copy()
    df = ranking(df, ["V","J"], [False, True])

    st.dataframe(df[["POS","TIME","V","J"]], use_container_width=True, hide_index=True)

# ========================
# MÉDIA DE GOLS LEVADOS
# ========================
elif pagina == "🛡️ Média de Gols Levados":

    df = cla.copy()
    df["MD"] = (df["GL"] / df["J"]).round(2)

    df = ranking(df, ["MD","GL","J"], [True, True, True])

    st.dataframe(df[["POS","TIME","MD","GL","J"]], use_container_width=True, hide_index=True)

# ========================
# APROVEITAMENTO
# ========================
elif pagina == "📊 Aproveitamento":

    df = cla.copy()
    df["APROVEITAMENTO"] = ((df["V"]*3 + df["E"]) / (df["J"]*3) * 100).round(2)

    df = ranking(df, ["APROVEITAMENTO","J"], [False, False])

    st.dataframe(df[["POS","TIME","APROVEITAMENTO","J","V","E","D"]], use_container_width=True, hide_index=True)

# ========================
# CLEAN SHEETS
# ========================
elif pagina == "🚫 Clean Sheets":

    df = cla[["TIME","CL_SH","J"]].copy()
    df = ranking(df, ["CL_SH","J"], [False, True])

    st.dataframe(df[["POS","TIME","CL_SH","J"]], use_container_width=True, hide_index=True)
