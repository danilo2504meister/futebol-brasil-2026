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

.card {
    background-color: #161a23;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 10px;
    border: 1px solid #2a2f3a;
}
.card:hover {
    border: 1px solid #4CAF50;
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

def card(titulo, conteudo, pagina_destino, icone="", escudo=None):
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)

        col1, col2 = st.columns([1,4])

        with col1:
            if escudo:
                st.image(escudo, width=50)

        with col2:
            st.markdown(f"**{icone} {titulo}**")
            st.markdown(f"### {conteudo}")

        if st.button(f"Acessar {titulo}", key=titulo):
            st.session_state["pagina"] = pagina_destino

        st.markdown('</div>', unsafe_allow_html=True)

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
# MENU COM CONTROLE
# ========================
menu_opcoes = [
    "🏠 Home",
    "🥇 Artilheiros",
    "🌍 Artilheiros Estrangeiros",
    "🌎 Gols por País",
    "📊 Invencibilidade Atual",
    "🔥 Melhores Ataques",
    "📈 Média de Gols",
    "🏆 Vitórias",
    "🛡️ Média de Gols Levados",
    "📊 Aproveitamento de Pontos",
    "🚫 Clean Sheets"
]

if "pagina" not in st.session_state:
    st.session_state["pagina"] = "🏠 Home"

pagina = st.sidebar.radio(
    "Menu",
    menu_opcoes,
    index=menu_opcoes.index(st.session_state["pagina"])
)

st.session_state["pagina"] = pagina

# ========================
# TÍTULO
# ========================
st.title(pagina)
st.markdown("🔄 Atualizado até: 13/04/2026")

# ========================
# HOME (CARDS)
# ========================
if pagina == "🏠 Home":

    total_gols = int((cal["GM"] + cal["GV"]).sum())
    total_jogos = len(cal)

    artilheiro = art.sort_values(by=["GOLS","JOGADOR"], ascending=[False, True]).iloc[0]

    estrangeiros = art.copy()
    estrangeiros = estrangeiros[estrangeiros["PAIS"].notna()]
    estrangeiros = estrangeiros[estrangeiros["PAIS"].str.strip() != ""]
    estrangeiros = estrangeiros[~estrangeiros["PAIS"].str.upper().isin(["BRA","BRASIL"])]
    artilheiro_ext = estrangeiros.sort_values(by=["GOLS","JOGADOR"], ascending=[False, True]).iloc[0]

    pais_gols = est.copy()
    pais_gols = pais_gols[pais_gols["PAIS"].notna()]
    pais_gols = pais_gols[pais_gols["PAIS"].str.strip() != ""]
    top_pais = pais_gols.sort_values(by="GOLS", ascending=False).iloc[0]

    inv = cla.sort_values(by="INV", ascending=False).iloc[0]
    ataque = cla.sort_values(by=["GOL","J"], ascending=[False, True]).iloc[0]

    cla["MG"] = (cla["GOL"] / cla["J"]).round(2)
    mg = cla.sort_values(by=["MG","GOL","J"], ascending=[False, False, False]).iloc[0]

    vit = cla.sort_values(by=["V","J"], ascending=[False, True]).iloc[0]

    cla["MD"] = (cla["GL"] / cla["J"]).round(2)
    md = cla.sort_values(by=["MD","GL","J"], ascending=[True, True, True]).iloc[0]

    cla["APROVEITAMENTO"] = ((cla["V"]*3 + cla["E"]) / (cla["J"]*3) * 100).round(2)
    apr = cla.sort_values(by=["APROVEITAMENTO","J"], ascending=[False, False]).iloc[0]

    cs = cla.sort_values(by=["CL_SH","J"], ascending=[False, True]).iloc[0]

    col1, col2 = st.columns(2)
    col1.metric("⚽ Gols", total_gols)
    col2.metric("📊 Jogos", total_jogos)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        card("Artilheiros", f"{artilheiro['JOGADOR']} - {int(artilheiro['GOLS'])}", "🥇 Artilheiro", "🥇")
        card("Artilheiro Estrangeiros", f"{artilheiro_ext['JOGADOR']} - {int(artilheiro_ext['GOLS'])}", "🌍 Artilheiro Estrangeiro", "🌍")
        card("Gols por País", f"{bandeira(top_pais['PAIS'])} {top_pais['PAIS']} - {int(top_pais['GOLS'])}", "🌎 País Estrangeiro com mais Gols", "🌎")
        card("Invencibilidade", f"{inv['TIME']} - {int(inv['INV'])}", "📊 Maior Invencibilidade Atual", "📊", escudo_time(inv["TIME"]))
        card("Melhores Ataques", f"{ataque['TIME']} - {int(ataque['GOL'])}", "🔥 Melhor Ataque", "🔥", escudo_time(ataque["TIME"]))

    with col2:
        card("Média de Gols", f"{mg['TIME']} - {mg['MG']}", "📈 Melhor Média de Gols", "📈", escudo_time(mg["TIME"]))
        card("Vitórias", f"{vit['TIME']} - {int(vit['V'])}", "🏆 Mais Vitórias", "🏆", escudo_time(vit["TIME"]))
        card("Média de Gols Levados", f"{md['TIME']} - {md['MD']}", "🛡️ Menor Média de Gols Levados", "🛡️", escudo_time(md["TIME"]))
        card("Aproveitamento", f"{apr['TIME']} - {apr['APROVEITAMENTO']}%", "📊 Melhor Aproveitamento de Pontos", "📊", escudo_time(apr["TIME"]))
        card("Clean Sheets", f"{cs['TIME']} - {int(cs['CL_SH'])}", "🚫 Mais Clean Sheets", "🚫", escudo_time(cs["TIME"]))

# ========================
# RESTANTE DAS PÁGINAS (mantidas)
# ========================
elif pagina == "🥇 Artilheiros":

    df = art.copy()
    df = df.sort_values(by=["GOLS","JOGADOR"], ascending=[False, True])
    df["POS"] = df["GOLS"].rank(method="min", ascending=False).astype(int)
    df = df.sort_values(by=["POS","JOGADOR"])
    df["POS"] = df["POS"].apply(ordinal)

    st.dataframe(df[["POS","JOGADOR","CLUBE","GOLS"]], use_container_width=True, hide_index=True)

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

elif pagina == "🌎 Gols por País":

    df = est.copy()
    df = df[df["PAIS"].notna()]
    df = df[df["PAIS"].str.strip() != ""]
    df["PAIS"] = df["PAIS"].apply(lambda x: f"{bandeira(x)} {x}")

    df = ranking(df, ["GOLS"], [False])

    st.dataframe(df[["POS","PAIS","GOLS"]], use_container_width=True, hide_index=True)

elif pagina == "📊 Invencibilidade":

    df = cla.copy()
    df = df[["TIME","INV","VIT","EMP"]]
    df = df[df["INV"].notna()]
    df = df.sort_values(by="INV", ascending=False)

    st.dataframe(df, use_container_width=True, hide_index=True)

elif pagina == "🔥 Melhores Ataques":

    df = cla[["TIME","GOL","J"]].copy()
    df = ranking(df, ["GOL","J"], [False, True])

    st.dataframe(df[["POS","TIME","GOL","J"]], use_container_width=True, hide_index=True)

elif pagina == "📈 Média de Gols":

    df = cla.copy()
    df["MG"] = (df["GOL"] / df["J"]).round(2)
    df = ranking(df, ["MG","GOL","J"], [False, False, False])

    st.dataframe(df[["POS","TIME","MG","GOL","J"]], use_container_width=True, hide_index=True)

elif pagina == "🏆 Vitórias":

    df = cla[["TIME","V","J"]].copy()
    df = ranking(df, ["V","J"], [False, True])

    st.dataframe(df[["POS","TIME","V","J"]], use_container_width=True, hide_index=True)

elif pagina == "🛡️ Média de Gols Levados":

    df = cla.copy()
    df["MD"] = (df["GL"] / df["J"]).round(2)
    df = ranking(df, ["MD","GL","J"], [True, True, True])

    st.dataframe(df[["POS","TIME","MD","GL","J"]], use_container_width=True, hide_index=True)

elif pagina == "📊 Aproveitamento":

    df = cla.copy()
    df["APROVEITAMENTO"] = ((df["V"]*3 + df["E"]) / (df["J"]*3) * 100).round(2)
    df = ranking(df, ["APROVEITAMENTO","J"], [False, False])

    st.dataframe(df[["POS","TIME","APROVEITAMENTO","J","V","E","D"]], use_container_width=True, hide_index=True)

elif pagina == "🚫 Clean Sheets":

    df = cla[["TIME","CL_SH","J"]].copy()
    df = ranking(df, ["CL_SH","J"], [False, True])

    st.dataframe(df[["POS","TIME","CL_SH","J"]], use_container_width=True, hide_index=True)
