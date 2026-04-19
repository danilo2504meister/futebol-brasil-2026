import streamlit as st
import pandas as pd

st.set_page_config(page_title="Futebol Brasil 2026", layout="wide")

# =========================
# FUNÇÃO DE CARREGAMENTO
# =========================
@st.cache_data
def carregar_dados():
    arquivo = "br26.xlsx"
    abas = pd.ExcelFile(arquivo).sheet_names

    dfs = {}

    for aba in abas:
        df = pd.read_excel(arquivo, sheet_name=aba)

        # padronizar colunas
        df.columns = df.columns.str.strip().str.upper()

        # padronizar ID_CLUBE (já deve existir, mas garantimos)
        if "ID_CLUBE" in df.columns:
            df["ID_CLUBE"] = df["ID_CLUBE"].astype(str).str.strip().str.lower()

        dfs[aba.upper()] = df

    return dfs

# =========================
# CARREGAR
# =========================
dfs = carregar_dados()

cla = dfs.get("CLA", pd.DataFrame())
inv = dfs.get("INV", pd.DataFrame())
aproveitamento = dfs.get("APROVEITAMENTO", pd.DataFrame())
art = dfs.get("ARTILHEIROS", pd.DataFrame())

# =========================
# INTEGRAÇÃO AUTOMÁTICA
# =========================
if not cla.empty:

    if not inv.empty and "ID_CLUBE" in inv.columns:
        cla = cla.merge(inv[["ID_CLUBE", "INV"]], on="ID_CLUBE", how="left")

    if not aproveitamento.empty and "ID_CLUBE" in aproveitamento.columns:
        cla = cla.merge(aproveitamento[["ID_CLUBE", "APROVEITAMENTO"]], on="ID_CLUBE", how="left")

# =========================
# TRATAR APROVEITAMENTO (%)
# =========================
if not aproveitamento.empty and "APROVEITAMENTO" in aproveitamento.columns:

    # garantir numérico
    aproveitamento["APROVEITAMENTO"] = pd.to_numeric(
        aproveitamento["APROVEITAMENTO"], errors="coerce"
    )

    # converter para %
    aproveitamento["APROVEITAMENTO"] = (aproveitamento["APROVEITAMENTO"] * 100).round(1)

    # formatar como string %
    aproveitamento["APROVEITAMENTO_STR"] = (
        aproveitamento["APROVEITAMENTO"].astype(str) + "%"
    )

# =========================
# MÉTRICAS (HOME)
# =========================
st.title("⚽ Futebol Brasil 2026")

col1, col2, col3 = st.columns(3)

# Maior invencibilidade
if "INV" in cla.columns:
    max_inv = cla["INV"].max()
    time_inv = cla.loc[cla["INV"].idxmax(), "CLUBE"] if "CLUBE" in cla.columns else ""
else:
    max_inv = "-"
    time_inv = "-"

# Melhor aproveitamento
if not aproveitamento.empty:
    top_ap = aproveitamento.sort_values("APROVEITAMENTO", ascending=False).iloc[0]
    time_ap = top_ap["CLUBE"] if "CLUBE" in top_ap else ""
    valor_ap = f"{top_ap['APROVEITAMENTO']:.1f}%"
else:
    time_ap = "-"
    valor_ap = "-"

# Artilheiro
if not art.empty:
    top_art = art.sort_values("GOLS", ascending=False).iloc[0]
    jogador = top_art["JOGADOR"]
    gols = top_art["GOLS"]
else:
    jogador = "-"
    gols = "-"

col1.metric("🔥 Maior Invencibilidade", f"{time_inv} ({max_inv})")
col2.metric("📊 Melhor Aproveitamento", f"{time_ap} ({valor_ap})")
col3.metric("⚽ Artilheiro", f"{jogador} ({gols})")

# =========================
# TABELA CLASSIFICAÇÃO
# =========================
st.subheader("🏆 Classificação")

if not cla.empty:
    st.dataframe(cla, use_container_width=True)
else:
    st.warning("Tabela de classificação não encontrada.")

# =========================
# APROVEITAMENTO (BONITO)
# =========================
st.subheader("📈 Aproveitamento")

if not aproveitamento.empty:
    tabela_ap = aproveitamento.copy()

    if "APROVEITAMENTO_STR" in tabela_ap.columns:
        tabela_ap["APROVEITAMENTO"] = tabela_ap["APROVEITAMENTO_STR"]

    st.dataframe(tabela_ap, use_container_width=True)
else:
    st.warning("Tabela de aproveitamento não encontrada.")
