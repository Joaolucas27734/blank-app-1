import streamlit as st
import pandas as pd
import altair as alt

# -------------------------------------
# CONFIG
# -------------------------------------
st.set_page_config(
    page_title="Dashboard Logístico – FlexLive",
    layout="wide",
)

st.title("📦 Dashboard Completo – Logística FlexLive")

# -------------------------------------
# LISTA MANUAL DAS ABAS DO GOOGLE SHEETS
# -------------------------------------
# ❗ Coloque aqui exatamente os nomes das abas da sua planilha
sheet_names = [
    "Página1", 
    "Página2",
    "Dashboard",
    "Pedidos",
    "Envios"
]

# Escolher aba
selected_sheet = st.sidebar.selectbox("Selecione a aba da planilha:", sheet_names)

# -------------------------------------
# MONTAR LINK CORRETO PARA A ABA
# -------------------------------------
sheet_id = "1WTEiRnm1OFxzn6ag1MfI8VnlQCbL8xwxY3LeanCsdxk"

sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={selected_sheet}"

# -------------------------------------
# CARREGAR DADOS
# -------------------------------------
try:
    df = pd.read_csv(sheet_url)
    st.success(f"Aba carregada: **{selected_sheet}**")
except Exception as e:
    st.error("Erro ao carregar a aba. Verifique se o nome está exatamente igual ao Google Sheets.")
    st.stop()

# -------------------------------------
# TRATAR DATAS
# -------------------------------------
for col in df.columns:
    try:
        df[col] = pd.to_datetime(df[col])
    except:
        pass

# -------------------------------------
# MOSTRAR TABELA
# -------------------------------------
st.header("📄 Dados da Aba Selecionada")
st.dataframe(df, use_container_width=True)

# -------------------------------------
# KPIs AUTOMÁTICOS
# -------------------------------------
if any(col in df.columns for col in ["status", "data_compra", "data_envio"]):

    st.header("📊 KPIs Automáticos")
    col1, col2, col3 = st.columns(3)

    col1.metric("Total de Registros", len(df))

    if "status" in df.columns:
        enviados = df[df["status"].str.contains("enviado", case=False, na=False)]
        col2.metric("Enviados", len(enviados))

    if "data_compra" in df.columns and "data_envio" in df.columns:
        df["lead_time"] = (df["data_envio"] - df["data_compra"]).dt.days
        tempo_medio = round(df["lead_time"].mean(), 2)
        col3.metric("Tempo Médio (dias)", tempo_medio)

# -------------------------------------
# GRÁFICOS AUTOMÁTICOS
# -------------------------------------
st.header("📈 Visualizações Automáticas")

if "data_compra" in df.columns:
    pedidos_por_dia = df.groupby(df["data_compra"].dt.date).size().reset_index(name="Quantidade")
    
    chart = alt.Chart(pedidos_por_dia).mark_line(point=True).encode(
        x="data_compra:T",
        y="Quantidade:Q",
        tooltip=["data_compra", "Quantidade"]
    ).properties(height=350)

    st.subheader("Registros por Dia")
    st.altair_chart(chart, use_container_width=True)

if "status" in df.columns:
    status_count = df["status"].value_counts().reset_index()
    status_count.columns = ["Status", "Quantidade"]

    chart2 = alt.Chart(status_count).mark_bar().encode(
        x="Status:N",
        y="Quantidade:Q",
        color="Status:N",
        tooltip=["Status", "Quantidade"]
    ).properties(height=350)

    st.subheader("Distribuição de Status")
    st.altair_chart(chart2, use_container_width=True)

# -------------------------------------
# DOWNLOAD CSV
# -------------------------------------
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Baixar CSV",
    data=csv,
    file_name=f"{selected_sheet}.csv",
    mime="text/csv",
)
