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

.card {
    background-color: #161a23;
    padding: 18px;
    border-radius: 12px;
    margin-bottom: 12px;
    border: 1px solid #2a2f3a;
}

.card:hover {
    border: 1px solid #555;
}

div.stButton > button {
    width: 100%;
    border-radius: 8px;
    border: 1px solid #3a3f4b;
    background-color: #1f2430;
    color: white;
    padding: 8px;
    font-weight: 500;
}

div.stButton > button:hover {
    background-color: #2a2f3a;
    border: 1px solid #777;
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
        "CHI": "🇨🇱","PER": "🇵🇪","VEN": "🇻🇪","EQU": "🇪🇨"
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

        # BOTÃO COM KEY ÚNICA
        if st.button(pagina_destino, key=f"{titulo}_{pagina_destino}"):
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
# MENU PADRONIZADO
# ========================
menu_opcoes = [
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
    "🚫 Clean Sheets",
    "📅 Jogos por equipe"
]

if "pagina" not in st.session_state:
    st.session_state["pagina"] = "🏠 Home"

pagina = st.sidebar.radio("Menu", menu_opcoes)

st.session_state["pagina"] = pagina

# ========================
# TÍTULO
# ========================
st.title(pagina)
st.markdown("🔄 Atualizado até: 13/04/2026")

# ========================
# HOME
# ========================
if pagina == "🏠 Home":

    artilheiro = art.sort_values(by=["GOLS","JOGADOR"], ascending=[False, True]).iloc[0]

    estrangeiros = art[
        art["PAIS"].notna() &
        (art["PAIS"].str.strip() != "") &
        (~art["PAIS"].str.upper().isin(["BRA","BRASIL"]))
    ]

    artilheiro_ext = estrangeiros.sort_values(by=["GOLS","JOGADOR"], ascending=[False, True]).iloc[0]

    pais_gols = estrangeiros.copy()
    pais_gols["PAIS"] = pais_gols["PAIS"].str.strip().str.upper()

    ranking_pais = (
        pais_gols.groupby("PAIS")["GOLS"]
        .sum()
        .reset_index()
        .sort_values(by="GOLS", ascending=False)
    )

    top_pais = ranking_pais.iloc[0]

    inv = cla.sort_values(by="INV", ascending=False).iloc[0]
    vit = cla.sort_values(by=["V","J"], ascending=[False, True]).iloc[0]

    cla["MG"] = (cla["GOL"] / cla["J"].replace(0,1)).round(2)
    mg = cla.sort_values(by="MG", ascending=False).iloc[0]

    cla["MD"] = (cla["GL"] / cla["J"].replace(0,1)).round(2)
    md = cla.sort_values(by="MD", ascending=True).iloc[0]

    cla["AP"] = ((cla["V"]*3 + cla["E"]) / (cla["J"].replace(0,1)*3) * 100).round(2)
    apr = cla.sort_values(by="AP", ascending=False).iloc[0]

    jogos = cla.sort_values(by="J", ascending=False).iloc[0]

    col1, col2 = st.columns([1,1])

    with col1:
        card("Artilheiro", f"{artilheiro['JOGADOR']} - {int(artilheiro['GOLS'])} gols", "🥇 Artilheiros", "🥇")
        card("Artilheiro Estrangeiro", f"{artilheiro_ext['JOGADOR']} - {int(artilheiro_ext['GOLS'])} gols", "🌍 Artilheiros Estrangeiros", "🌍")
        card("País com mais gols", f"{bandeira(top_pais['PAIS'])} {top_pais['PAIS']} - {int(top_pais['GOLS'])} gols", "🌎 Gols por País", "🌎")
        card("Maior Invencibilidade", f"{inv['TIME']} - {int(inv['INV'])} jogos", "📊 Invencibilidade", "📊", escudo_time(inv["TIME"]))
        card("Mais jogos disputados", f"{jogos['TIME']} - {int(jogos['J'])} jogos", "📅 Jogos por equipe", "📅", escudo_time(jogos["TIME"]))

    with col2:
        card("Maior média de gols", f"{mg['TIME']} - {mg['MG']} gols/jogo", "📈 Média de Gols", "📈", escudo_time(mg["TIME"]))
        card("Mais vitórias", f"{vit['TIME']} - {int(vit['V'])} vitórias", "🏆 Vitórias", "🏆", escudo_time(vit["TIME"]))
        card("Melhor defesa", f"{md['TIME']} - {md['MD']} gols/jogo", "🛡️ Média de Gols Levados", "🛡️", escudo_time(md["TIME"]))
        card("Maior aproveitamento", f"{apr['TIME']} - {apr['AP']}%", "📊 Aproveitamento", "📊", escudo_time(apr["TIME"]))

# ========================
# NOVA PÁGINA
# ========================
elif pagina == "📅 Jogos por equipe":

    df = cla[["TIME","J"]].copy()
    df = ranking(df, ["J"], [False])

    st.dataframe(df[["POS","TIME","J"]], use_container_width=True, hide_index=True)

# ========================
# RESTANTE
# ========================
elif pagina == "🥇 Artilheiros":
    df = ranking(art.copy(), ["GOLS"], [False])
    st.dataframe(df[["POS","JOGADOR","CLUBE","GOLS"]], use_container_width=True, hide_index=True)

elif pagina == "🌍 Artilheiros Estrangeiros":
    df = estrangeiros.copy()
    df = ranking(df, ["GOLS"], [False])
    st.dataframe(df[["POS","JOGADOR","CLUBE","GOLS","PAIS"]], use_container_width=True, hide_index=True)

elif pagina == "🌎 Gols por País":
    df = ranking(ranking_pais.copy(), ["GOLS"], [False])
    st.dataframe(df[["POS","PAIS","GOLS"]], use_container_width=True, hide_index=True)

elif pagina == "📊 Invencibilidade":
    df = cla.sort_values(by="INV", ascending=False)
    st.dataframe(df[["TIME","INV"]], use_container_width=True)

elif pagina == "🔥 Melhores Ataques":
    df = ranking(cla.copy(), ["GOL"], [False])
    st.dataframe(df[["POS","TIME","GOL"]], use_container_width=True)

elif pagina == "📈 Média de Gols":
    df = ranking(cla.copy(), ["MG"], [False])
    st.dataframe(df[["POS","TIME","MG"]], use_container_width=True)

elif pagina == "🏆 Vitórias":
    df = ranking(cla.copy(), ["V"], [False])
    st.dataframe(df[["POS","TIME","V"]], use_container_width=True)

elif pagina == "🛡️ Média de Gols Levados":
    df = ranking(cla.copy(), ["MD"], [True])
    st.dataframe(df[["POS","TIME","MD"]], use_container_width=True)

elif pagina == "📊 Aproveitamento":
    df = ranking(cla.copy(), ["AP"], [False])
    st.dataframe(df[["POS","TIME","AP"]], use_container_width=True)

elif pagina == "🚫 Clean Sheets":
    df = ranking(cla.copy(), ["CL_SH"], [False])
    st.dataframe(df[["POS","TIME","CL_SH"]], use_container_width=True)
