import streamlit as st
import pandas as pd
import altair as alt

# ------------------------------
# CONFIG
# ------------------------------
st.set_page_config(
    page_title="Dashboard Logístico",
    layout="wide",
)

st.title("📦 Dashboard de Logística – FlexLive Dropshipping")

# ------------------------------
# IMPORTAÇÃO DO GOOGLE SHEETS
# ------------------------------
sheet_url = "https://docs.google.com/spreadsheets/d/1WTEiRnm1OFxzn6ag1MfI8VnlQCbL8xwxY3LeanCsdxk/gviz/tq?tqx=out:csv"
df = pd.read_csv(sheet_url)

st.success("Dados carregados direto do Google Sheets!")

# ------------------------------
# TRATAMENTO DE DADOS
# ------------------------------
# Converte datas automaticamente
for col in df.columns:
    try:
        df[col] = pd.to_datetime(df[col])
    except:
        pass

# ------------------------------
# SIDEBAR – FILTRO
# ------------------------------
st.sidebar.header("Filtros")

if "status" in df.columns:
    filtro_status = st.sidebar.multiselect(
        "Status do pedido",
        df["status"].dropna().unique(),
        default=df["status"].dropna().unique()
    )
    df = df[df["status"].isin(filtro_status)]

# ------------------------------
# KPIs
# ------------------------------
col1, col2, col3 = st.columns(3)

# KPI 1 – Total de Pedidos
total_pedidos = len(df)
col1.metric("📦 Total de Pedidos", total_pedidos)

# KPI 2 – Pedidos Enviados
if "status" in df.columns:
    enviados = df[df["status"].str.contains("enviado", case=False, na=False)]
    col2.metric("🚚 Pedidos Enviados", len(enviados))

# KPI 3 – Tempo Médio (Dias)
if "data_envio" in df.columns and "data_compra" in df.columns:
    df["lead_time"] = (df["data_envio"] - df["data_compra"]).dt.days
    tempo_medio = round(df["lead_time"].mean(), 2)
    col3.metric("⏱ Tempo Médio de Processamento", tempo_medio)

# ------------------------------
# GRÁFICOS
# ------------------------------
st.header("📊 Visualizações")

# Gráfico de Pedidos por Dia
if "data_compra" in df.columns:
    pedidos_por_dia = df.groupby(df["data_compra"].dt.date).size().reset_index(name="Quantidade")

    chart = alt.Chart(pedidos_por_dia).mark_line(point=True).encode(
        x="data_compra:T",
        y="Quantidade:Q",
        tooltip=["data_compra", "Quantidade"]
    ).properties(width="100%", height=350)

    st.subheader("📈 Pedidos por Dia")
    st.altair_chart(chart, use_container_width=True)

# Gráfico de Status
if "status" in df.columns:
    status_count = df["status"].value_counts().reset_index()
    status_count.columns = ["Status", "Quantidade"]

    chart2 = alt.Chart(status_count).mark_bar().encode(
        x="Status:N",
        y="Quantidade:Q",
        tooltip=["Status", "Quantidade"],
        color="Status:N"
    ).properties(width="100%", height=350)

    st.subheader("📊 Distribuição de Status")
    st.altair_chart(chart2, use_container_width=True)

# ------------------------------
# TABELA COMPLETA
# ------------------------------
st.header("📄 Dados Completos")
st.dataframe(df, use_container_width=True)

# ------------------------------
# DOWNLOAD DO CSV
# ------------------------------
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Baixar CSV Filtrado",
    data=csv,
    file_name="dados_logistica.csv",
    mime="text/csv",
)
