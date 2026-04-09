import streamlit as st
import pandas as pd

st.set_page_config(page_title="Futebol Brasil 2026", layout="wide")

# ========================
# ESTILO CLARO (PROFISSIONAL)
# ========================
st.markdown("""
<style>
body {
    background-color: #f5f6fa;
}
.card {
    background-color: white;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 10px;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.08);
}
.ad {
    background-color: #eaeaea;
    padding: 20px;
    text-align: center;
    border-radius: 10px;
    margin: 20px 0;
}
</style>
""", unsafe_allow_html=True)

# ========================
# FUNÇÕES
# ========================
def limpar(df):
    df.columns = df.columns.str.strip().str.upper()
    return df

def formatar_time(nome):
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

# FORMATAR TIMES
cal["MANDANTE"] = cal["MANDANTE"].apply(formatar_time)
cal["VISITANTE"] = cal["VISITANTE"].apply(formatar_time)
cla["EQUIPE"] = cla["EQUIPE"].apply(formatar_time)
art["CLUBE"] = art["CLUBE"].apply(formatar_time)

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

    col1, col2, col3 = st.columns(3)
    col1.metric("⚽ Gols", total_gols)
    col2.metric("📊 Jogos", total_jogos)
    col3.metric("📈 Média", media)

    st.markdown('<div class="ad">ESPAÇO PARA PUBLICIDADE</div>', unsafe_allow_html=True)

# ========================
# 📊 RESULTADOS (CARDS)
# ========================
elif pagina == "📊 Resultados":

    st.subheader("Resultados")

    df = cal.copy()

    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce").dt.date
    df["GM"] = pd.to_numeric(df["GM"], errors="coerce").fillna(0).astype(int)
    df["GV"] = pd.to_numeric(df["GV"], errors="coerce").fillna(0).astype(int)

    # filtros
    col1, col2 = st.columns(2)

    with col1:
        data = st.date_input("Filtrar por data")

    with col2:
        time = st.selectbox(
            "Buscar time",
            ["Todos"] + sorted(df["MANDANTE"].unique())
        )

    if data:
        df = df[df["DATA"] == data]

    if time != "Todos":
        df = df[(df["MANDANTE"] == time) | (df["VISITANTE"] == time)]

    # cards
    for _, row in df.iterrows():
        st.markdown(f"""
        <div class="card">
            <b>{row['MANDANTE']}</b> {row['GM']} x {row['GV']} <b>{row['VISITANTE']}</b><br>
            📅 {row['DATA']} | 🏆 {row.get('CAMPEONATO','')}
        </div>
        """, unsafe_allow_html=True)

# ========================
# 🥇 ARTILHEIROS
# ========================
elif pagina == "🥇 Artilheiros":

    st.subheader("Artilheiros")

    df = art.copy()

    df["GOLS"] = df["GOLS"].fillna(0).astype(int)
    df["JOGOS"] = df["JOGOS"].fillna(0).astype(int)

    df = df.rename(columns={"Z": "Jogador"})

    df = df.sort_values(by="GOLS", ascending=False)

    df.insert(0, "Pos", [f"{i}º" for i in range(1, len(df)+1)])

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

    df["APROV"] = ((df["PTS"] / (df["J"] * 3)) * 100).round(2)
    df["MG"] = df["MG"].round(2)

    df = df.sort_values(by="PTS", ascending=False)

    df.insert(0, "Classificação", [f"{i}º" for i in range(1, len(df)+1)])

    colunas = [
        "Classificação", "EQUIPE", "PTS", "J", "V", "E", "D",
        "APROV", "GL", "MG", "MD", "CL SH"
    ]

    if "GOLS" in df.columns:
        colunas.insert(4, "GOLS")
    if "CIDADE" in df.columns:
        colunas.insert(2, "CIDADE")
    if "UF" in df.columns:
        colunas.insert(3, "UF")

    df = df[colunas]

    # zebra
    def zebra(row):
        return ['background-color: #f2f2f2' if row.name % 2 == 0 else '' for _ in row]

    st.dataframe(df.style.apply(zebra, axis=1), use_container_width=True)

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
