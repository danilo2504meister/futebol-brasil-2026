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
    df = df.loc[:, ~df.columns.str.contains("^UNNAMED")]
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
    inv = pd.read_excel("br26.xlsx", sheet_name="INV")
    return limpar(art), limpar(cla), limpar(est), limpar(cal), limpar(inv)

art, cla, est, cal, inv = carregar()

# ========================
# TRATAMENTO GLOBAL
# ========================
cla["CLUBE"] = cla["CLUBE"].apply(formatar)
art["CLUBE"] = art["CLUBE"].apply(formatar)

cla["APROVEITAMENTO"] = (
    pd.to_numeric(cla["APROVEITAMENTO"], errors="coerce") * 100
).round(1)

art["GOLS"] = pd.to_numeric(art["GOLS"], errors="coerce").fillna(0)
art["JOGOS"] = pd.to_numeric(art["JOGOS"], errors="coerce").fillna(0)

estrangeiros = art[
    art["PAIS"].notna() &
    (art["PAIS"].str.strip() != "") &
    (~art["PAIS"].str.upper().isin(["BRA","BRASIL"]))
].copy()

estrangeiros["PAIS"] = estrangeiros["PAIS"].str.strip().str.upper()

ranking_pais = (
    estrangeiros.groupby("PAIS")["GOLS"]
    .sum()
    .reset_index()
    .sort_values(by="GOLS", ascending=False)
)

DATA_ATUALIZACAO = "19/04/2026"

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

    artilheiro_ext = estrangeiros.sort_values(
        by=["GOLS","JOGADOR"], ascending=[False, True]
    ).iloc[0] if not estrangeiros.empty else None

    top_pais = ranking_pais.iloc[0] if not ranking_pais.empty else pd.Series({"PAIS": "-", "GOLS": 0})

    max_inv = inv["INV"].max()
    inv_home = inv[inv["INV"] == max_inv]

    max_v = cla["V"].max()
    vit = cla[cla["V"] == max_v]

    max_mg = cla["MG"].max()
    mg = cla[cla["MG"] == max_mg]

    # 🔥 Melhor Ataque
    max_gols = cla["GOLS"].max()
    ataque = cla[cla["GOLS"] == max_gols]

    # 🛡️ MD com desempate
    md = cla.sort_values(by=["MD","J"], ascending=[True, False]).head(1)

    # 📊 Aproveitamento com desempate
    apr = cla.sort_values(by=["APROVEITAMENTO","J"], ascending=[False, False]).head(1)

    max_j = cla["J"].max()
    jogos = cla[cla["J"] == max_j]

    col1, col2 = st.columns(2)

    with col1:
        card("Artilheiro", f"{artilheiro['JOGADOR']} - {int(artilheiro['GOLS'])} gols", "🥇 Artilheiros", escudo=escudo_time(artilheiro["CLUBE"]))

        if artilheiro_ext is not None:
            card("Artilheiro Estrangeiro", f"{artilheiro_ext['JOGADOR']} - {int(artilheiro_ext['GOLS'])} gols", "🌍 Artilheiros Estrangeiros", escudo=escudo_time(artilheiro_ext["CLUBE"]))

        card("Melhor Ataque", f"{' | '.join(ataque['CLUBE'])} - {int(max_gols)} gols", "🔥 Melhores Ataques", escudo=escudo_time(ataque.iloc[0]["CLUBE"]))

        card("País estrangeiro com mais gols", f"{bandeira(top_pais['PAIS'])} {top_pais['PAIS']} - {int(top_pais['GOLS'])} gols", "🌎 Gols por País")

        card("Maior Invencibilidade Atual", f"{' | '.join(inv_home['CLUBE'])} - {int(max_inv)} jogos", "📊 Invencibilidade", escudo=escudo_time(inv_home.iloc[0]["CLUBE"]))
        card("Clube com Mais jogos", f"{' | '.join(jogos['CLUBE'])} - {int(max_j)} jogos", "📅 Jogos por equipe", escudo=escudo_time(jogos.iloc[0]["CLUBE"]))

    with col2:
        card("Maior Média de gols por jogo", f"{' | '.join(mg['CLUBE'])} - {mg.iloc[0]['MG']:.2f} gols/jogo", "📈 Média de Gols", escudo=escudo_time(mg.iloc[0]["CLUBE"]))
        card("Mais Vitórias", f"{' | '.join(vit['CLUBE'])} - {int(max_v)} vitórias", "🏆 Vitórias", escudo=escudo_time(vit.iloc[0]["CLUBE"]))
        card("Menor Média de Gols Levados", f"{md.iloc[0]['CLUBE']} - {md.iloc[0]['MD']:.2f} gols/jogo", "🛡️ Média de Gols Levados", escudo=escudo_time(md.iloc[0]["CLUBE"]))
        card("Melhor Aproveitamento de Pontos", f"{apr.iloc[0]['CLUBE']} - {apr.iloc[0]['APROVEITAMENTO']}%", "📊 Aproveitamento", escudo=escudo_time(apr.iloc[0]["CLUBE"]))

# ========================
# PÁGINAS AJUSTADAS
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
    df = ranking(df, ["INV"], [False])
    st.dataframe(df[["POS","CLUBE","INV","VIT","EMP"]], use_container_width=True, hide_index=True)

elif pagina == "🔥 Melhores Ataques":
    df = ranking(cla.copy(), ["GOLS"], [False])
    st.dataframe(df[["POS","CLUBE","GOLS","J"]], use_container_width=True, hide_index=True)

elif pagina == "📈 Média de Gols":
    df = ranking(cla.copy(), ["MG"], [False])
    df["MG"] = df["MG"].map("{:.2f}".format)
    st.dataframe(df[["POS","CLUBE","MG","GOLS","J"]], use_container_width=True, hide_index=True)

elif pagina == "🏆 Vitórias":
    df = ranking(cla.copy(), ["V"], [False])
    st.dataframe(df[["POS","CLUBE","V","J"]], use_container_width=True, hide_index=True)

elif pagina == "🛡️ Média de Gols Levados":
    df = ranking(cla.copy(), ["MD"], [True])
    df["MD"] = df["MD"].map("{:.2f}".format)
    st.dataframe(df[["POS","CLUBE","MD","GL","J"]], use_container_width=True, hide_index=True)

elif pagina == "📊 Aproveitamento":
    df = ranking(cla.copy(), ["AP","J"], [False, False])
    st.dataframe(df[["POS","CLUBE","AP","J"]], use_container_width=True, hide_index=True)

elif pagina == "🚫 Clean Sheets":
    coluna = "CL_SH" if "CL_SH" in cla.columns else "CL SH"
    df = ranking(cla.copy(), [coluna], [False])
    st.dataframe(df[["POS","CLUBE",coluna,"J"]], use_container_width=True, hide_index=True)

elif pagina == "📅 Jogos por equipe":
    df = ranking(cla.copy(), ["J"], [False])
    st.dataframe(df[["POS","CLUBE","J"]], use_container_width=True, hide_index=True)
