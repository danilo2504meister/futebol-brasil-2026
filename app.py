import streamlit as st
import pandas as pd

st.set_page_config(page_title="Futebol Brasil 2026", layout="wide")

# ========================
# FUNÇÕES
# ========================
def limpar(df):
    df.columns = df.columns.str.strip().str.upper()
    return df

def formatar_time(nome):
    if isinstance(nome, str) and "-" in nome:
        nome, uf = nome.split("-")
        return nome.title(), uf
    return nome, ""

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

# ========================
# AJUSTAR TIMES (nome + UF)
# ========================
cal[["TIME", "UF"]] = cal["MANDANTE"].apply(lambda x: pd.Series(formatar_time(x)))
cla[["TIME", "UF"]] = cla["EQUIPE"].apply(lambda x: pd.Series(formatar_time(x)))
art["CLUBE"] = art["CLUBE"].apply(lambda x: formatar_time(x)[0])

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
    total_jogos = len(cal)
    media = round(total_gols / total_jogos, 2)

    # métricas principais
    col1, col2, col3 = st.columns(3)
    col1.metric("⚽ Total de Gols", total_gols)
    col2.metric("📊 Total de Jogos", total_jogos)
    col3.metric("📈 Média de Gols", media)

    st.divider()

    # estatísticas
    time_mais_jogos = cla.sort_values(by="J", ascending=False).iloc[0]["TIME"]
    time_mais_vitorias = cla.sort_values(by="V", ascending=False).iloc[0]["TIME"]
    time_mais_gols = cal.groupby("TIME")["GM"].sum().idxmax()

    art["GOLS"] = art["GOLS"].fillna(0).astype(int)
    artilheiro = art.sort_values(by="GOLS", ascending=False).iloc[0]

    col4, col5 = st.columns(2)
    col6, col7 = st.columns(2)

    col4.metric("🏃 Mais Jogos", time_mais_jogos)
    col5.metric("🏆 Mais Vitórias", time_mais_vitorias)
    col6.metric("🔥 Mais Gols", time_mais_gols)
    col7.metric("🥇 Artilheiro", f"{artilheiro['Z']} ({artilheiro['GOLS']})")

# ========================
# 📊 RESULTADOS
# ========================
elif pagina == "📊 Resultados":

    st.subheader("Resultados")

    df = cal.copy()
    df["DATA"] = pd.to_datetime(df["DATA"]).dt.date

    time = st.selectbox(
        "Filtrar por time",
        ["Todos"] + sorted(df["TIME"].unique())
    )

    if time != "Todos":
        df = df[df["TIME"] == time]

    df["PLACAR"] = (
        df["TIME"] + " " +
        df["GM"].astype(int).astype(str) +
        " x " +
        df["GV"].astype(int).astype(str)
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
        "Z": "Jogador"
    })

    df = df.sort_values(by="GOLS", ascending=False).head(50)

    # ranking
    df.insert(0, "Pos", [f"{i}º" for i in range(1, len(df)+1)])

    # remover colunas indesejadas
    colunas_remover = ["COD", "COLUNA1", "HORA DE NASCIMENTO"]
    df = df.drop(columns=[c for c in colunas_remover if c in df.columns], errors="ignore")

    df = df[["Pos", "Jogador", "CLUBE", "GOLS", "JOGOS"]]

    st.dataframe(df, use_container_width=True)

# ========================
# 📈 CLASSIFICAÇÃO
# ========================
elif pagina == "📈 Classificação":

    st.subheader("Classificação")

    df = cla.copy()

    # cálculos
    df["APROV"] = ((df["PTS"] / (df["J"] * 3)) * 100).round(2)
    df["MG"] = df["MG"].round(2)

    # ranking fixo
    df = df.sort_values(by="PTS", ascending=False)
    df.insert(0, "Classificação", [f"{i}º" for i in range(1, len(df)+1)])

    # selecionar colunas
    colunas = [
        "Classificação", "TIME", "UF", "PTS", "J", "V", "E", "D",
        "APROV", "GL", "MG", "MD", "CL SH"
    ]

    # adicionar gols e cidade se existirem
    if "GOLS" in df.columns:
        colunas.insert(4, "GOLS")
    if "CIDADE" in df.columns:
        colunas.insert(3, "CIDADE")

    df = df[colunas]

    # estilo zebra
    def zebra(df):
        return ['background-color: #111' if i % 2 == 0 else '' for i in range(len(df))]

    st.dataframe(df.style.apply(zebra, axis=0), use_container_width=True)

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
