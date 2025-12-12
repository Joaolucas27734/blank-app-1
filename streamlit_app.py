import streamlit as st
import pandas as pd
import altair as alt

# -------------------------------------
# CONFIG GERAL
# -------------------------------------
st.set_page_config(
    page_title="Dashboard Logístico – FlexLive",
    layout="wide",
)

st.title("📦 Dashboard Completo de Logística – FlexLive")

# -------------------------------------
# CARREGAR TODAS AS ABA (SHEETS)
# -------------------------------------
st.sidebar.header("📑 Abas da Planilha")

base_url = "https://docs.google.com/spreadsheets/d/1WTEiRnm1OFxzn6ag1MfI8VnlQCbL8xwxY3LeanCsdxk"

# Lê metadados (nomes das abas)
sheets_meta_url = f"{base_url}/gviz/tq?&tqx=out:json"
meta = pd.read_json(sheets_meta_url.replace("json", "csv"), lines=True, orient="records")

# Em caso de erro do Sheets retornar JSON estranho, usamos fallback
try:
    sheet_names = meta['table']['cols'][0]['label']
except:
    # MÉTODO ALTERNATIVO: carrega diretamente nomes padrão (Sheet1, Sheet2,...)
    import requests, re
    r = requests.get(base_url)
    sheet_names = list(set(re.findall(r'name":"([^"]+)"', r.text))) or ["Página 1"]

# Sidebar para escolher aba
selected_sheet = st.sidebar.selectbox("Selecione a Página", sheet_names)

# Monta URL da aba específica
sheet_csv_url = f"{base_url}/gviz/tq?tqx=out:csv&sheet={selected_sheet}"

# Carrega dados
df = pd.read_csv(sheet_csv_url)

st.success(f"Página carregada: **{selected_sheet}**")

# -------------------------------------
# TRATA DATAS AUTOMATICAMENTE
# -------------------------------------
for col in df.columns:
    try:
        df[col] = pd.to_datetime(df[col])
    except:
        pass

# -------------------------------------
# EXIBE TABELA COMPLETA
# -------------------------------------
st.header("📄 Dados da Página Selecionada")
st.dataframe(df, use_container_width=True)

# -------------------------------------
# KPIs AUTOMÁTICOS (SE COLUNAS EXISTIREM)
# -------------------------------------
if any(col in df.columns for col in ["status", "data_compra", "data_envio"]):
    
    st.header("📊 KPIs Automáticos")

    col1, col2, col3 = st.columns(3)

    # Total
    col1.metric("Total de Registros", len(df))

    # Status
    if "status" in df.columns:
        enviados = df[df["status"].str.contains("enviado", case=False, na=False)]
        col2.metric("Enviados", len(enviados))

    # Lead time
    if "data_compra" in df.columns and "data_envio" in df.columns:
        df["lead_time"] = (df["data_envio"] - df["data_compra"]).dt.days
        tempo_medio = round(df["lead_time"].mean(), 2)
        col3.metric("Tempo Médio (dias)", tempo_medio)

# -------------------------------------
# GRÁFICOS AUTOMÁTICOS
# -------------------------------------
st.header("📈 Visualizações Automáticas")

# Gráfico de pedidos por dia
if "data_compra" in df.columns:
    pedidos_por_dia = df.groupby(df["data_compra"].dt.date).size().reset_index(name="Quantidade")

    chart = alt.Chart(pedidos_por_dia).mark_line(point=True).encode(
        x="data_compra:T",
        y="Quantidade:Q",
        tooltip=["data_compra", "Quantidade"]
    ).properties(height=350)

    st.subheader("📅 Registros por Dia")
    st.altair_chart(chart, use_container_width=True)

# Gráfico de status
if "status" in df.columns:
    status_count = df["status"].value_counts().reset_index()
    status_count.columns = ["Status", "Quantidade"]

    chart2 = alt.Chart(status_count).mark_bar().encode(
        x="Status:N",
        y="Quantidade:Q",
        color="Status:N",
        tooltip=["Status", "Quantidade"]
    ).properties(height=350)

    st.subheader("🔖 Status dos Pedidos")
    st.altair_chart(chart2, use_container_width=True)

# -------------------------------------
# DOWNLOAD CSV
# -------------------------------------
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Baixar CSV desta página",
    data=csv,
    file_name=f"{selected_sheet}.csv",
    mime="text/csv",
)
