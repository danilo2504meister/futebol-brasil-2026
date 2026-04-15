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

.card:hover { border: 1px solid #555; }

div.stButton > button {
    width: 100%;
    border-radius: 8px;
    border: 1px solid #3a3f4b;
    background-color: #1f2430;
    color: white;
    padding: 8px;
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
    flags = {"BRA":"🇧🇷","ARG":"🇦🇷","URU":"🇺🇾","PAR":"🇵🇾","COL":"🇨🇴"}
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
# TRATAMENTO GLOBAL
# ========================
cla["TIME"] = cla["TIME"].apply(formatar)
art["CLUBE"] = art["CLUBE"].apply(formatar)

art["GOLS"] = pd.to_numeric(art["GOLS"], errors="coerce").fillna(0)
art["JOGOS"] = pd.to_numeric(art["JOGOS"], errors="coerce").fillna(0)

estrangeiros = art[
    art["PAIS"].notna() &
    (art["PAIS"].str.strip() != "") &
    (~art["PAIS"].str.upper().isin(["BRA","BRASIL"]))
].copy()

estrangeiros["PAIS"] = estrangeiros["PAIS"].str.strip().str.upper()

cla["MG"] = (cla["GOL"] / cla["J"].replace(0,1)).round(2)
cla["MD"] = (cla["GL"] / cla["J"].replace(0,1)).round(2)
cla["AP"] = ((cla["V"]*3 + cla["E"]) / (cla["J"].replace(0,1)*3) * 100).round(2)

ranking_pais = (
    estrangeiros.groupby("PAIS")["GOLS"]
    .sum()
    .reset_index()
    .sort_values(by="GOLS", ascending=False)
)
DATA_ATUALIZACAO = "14/04/2026"
# ========================
# MENU
# ========================
menu = [
    "🏠 Home","🥇 Artilheiros","🌍 Artilheiros Estrangeiros",
    "🌎 Gols por País","📊 Invencibilidade","🔥 Melhores Ataques",
    "📈 Média de Gols","🏆 Vitórias","🛡️ Média de Gols Levados",
    "📊 Aproveitamento","🚫 Clean Sheets","📅 Jogos por equipe"
]

pagina = st.sidebar.radio("Menu", menu)

st.title(pagina)
st.caption(f"Atualizado até: {DATA_ATUALIZACAO}")


# ========================
# HOME
# ========================
if pagina == "🏠 Home":

    artilheiro = art.sort_values(by=["GOLS","JOGADOR"], ascending=[False, True]).iloc[0]
    artilheiro_ext = estrangeiros.sort_values(by=["GOLS","JOGADOR"], ascending=[False, True]).iloc[0]
    top_pais = ranking_pais.iloc[0] if not ranking_pais.empty else pd.Series({"PAIS": "-", "GOLS": 0})

    # EMPATES
    max_inv = cla["INV"].max()
    inv = cla[cla["INV"] == max_inv]

    max_v = cla["V"].max()
    vit = cla[cla["V"] == max_v]

    max_mg = cla["MG"].max()
    mg = cla[cla["MG"] == max_mg]

    min_md = cla["MD"].min()
    md = cla[cla["MD"] == min_md]

    max_ap = cla["AP"].max()
    apr = cla[cla["AP"] == max_ap]

    max_j = cla["J"].max()
    jogos = cla[cla["J"] == max_j]

    col1, col2 = st.columns(2)

    with col1:
        card("Artilheiro", f"{artilheiro['JOGADOR']} - {int(artilheiro['GOLS'])} gols", "🥇 Artilheiros", escudo=escudo_time(artilheiro["CLUBE"]))
        card("Artilheiro Estrangeiro", f"{artilheiro_ext['JOGADOR']} - {int(artilheiro_ext['GOLS'])} gols", "🌍 Artilheiros Estrangeiros", escudo=escudo_time(artilheiro_ext["CLUBE"]))
        card("País com mais gols", f"{bandeira(top_pais['PAIS'])} {top_pais['PAIS']} - {int(top_pais['GOLS'])} gols", "🌎 Gols por País")

        card("Invencibilidade", f"{' | '.join(inv['TIME'])} - {int(max_inv)} jogos", "📊 Invencibilidade", escudo=escudo_time(inv.iloc[0]["TIME"]))
        card("Mais jogos", f"{' | '.join(jogos['TIME'])} - {int(max_j)} jogos", "📅 Jogos por equipe", escudo=escudo_time(jogos.iloc[0]["TIME"]))

    with col2:
        card("Média de gols", f"{' | '.join(mg['TIME'])} - {mg.iloc[0]['MG']} gols/jogo", "📈 Média de Gols", escudo=escudo_time(mg.iloc[0]["TIME"]))
        card("Vitórias", f"{' | '.join(vit['TIME'])} - {int(max_v)} vitórias", "🏆 Vitórias", escudo=escudo_time(vit.iloc[0]["TIME"]))
        card("Defesa", f"{' | '.join(md['TIME'])} - {md.iloc[0]['MD']} gols/jogo", "🛡️ Média de Gols Levados", escudo=escudo_time(md.iloc[0]["TIME"]))
        card("Aproveitamento", f"{' | '.join(apr['TIME'])} - {apr.iloc[0]['AP']}%", "📊 Aproveitamento", escudo=escudo_time(apr.iloc[0]["TIME"]))

# ========================
# PÁGINAS
# ========================
elif pagina == "🥇 Artilheiros":
    df = ranking(art.copy(), ["GOLS"], [False])
    st.dataframe(df[["POS","JOGADOR","CLUBE","GOLS"]], use_container_width=True, hide_index=True)

elif pagina == "🌍 Artilheiros Estrangeiros":
    df = ranking(estrangeiros.copy(), ["GOLS"], [False])
    st.dataframe(df[["POS","JOGADOR","CLUBE","GOLS","PAIS"]], use_container_width=True, hide_index=True)

elif pagina == "🌎 Gols por País":
    df = ranking(ranking_pais.copy(), ["GOLS"], [False])
    st.dataframe(df[["POS","PAIS","GOLS"]], use_container_width=True, hide_index=True)

elif pagina == "📊 Invencibilidade":
    df = cla.copy()
    df = df[df["INV"].notna()]
    df = df[df["INV"] > 0]
    df = ranking(df, ["INV"], [False])
    st.dataframe(df[["POS","TIME","INV"]], use_container_width=True, hide_index=True)

elif pagina == "🔥 Melhores Ataques":
    df = ranking(cla.copy(), ["GOL"], [False])
    st.dataframe(df[["POS","TIME","GOL","J"]], use_container_width=True, hide_index=True)

elif pagina == "📈 Média de Gols":
    df = ranking(cla.copy(), ["MG"], [False])
    st.dataframe(df[["POS","TIME","MG","GOL","J"]], use_container_width=True, hide_index=True)

elif pagina == "🏆 Vitórias":
    df = ranking(cla.copy(), ["V"], [False])
    st.dataframe(df[["POS","TIME","V","J"]], use_container_width=True, hide_index=True)

elif pagina == "🛡️ Média de Gols Levados":
    df = ranking(cla.copy(), ["MD"], [True])
    st.dataframe(df[["POS","TIME","MD","GL","J"]], use_container_width=True, hide_index=True)

elif pagina == "📊 Aproveitamento":
    df = ranking(cla.copy(), ["AP","J"], [False, False])
    st.dataframe(df[["POS","TIME","AP","J"]], use_container_width=True, hide_index=True)

elif pagina == "🚫 Clean Sheets":
    coluna = "CL_SH" if "CL_SH" in cla.columns else "CL SH"
    df = ranking(cla.copy(), [coluna], [False])
    st.dataframe(df[["POS","TIME",coluna,"J"]], use_container_width=True, hide_index=True)

elif pagina == "📅 Jogos por equipe":
    df = ranking(cla.copy(), ["J"], [False])
    st.dataframe(df[["POS","TIME","J"]], use_container_width=True, hide_index=True)
