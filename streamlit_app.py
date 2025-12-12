# app.py
import streamlit as st
import pandas as pd
from kpi import load_data, kpi_report, kpis_to_dataframe
import plotly.express as px
import io

st.set_page_config(layout="wide", page_title="Dropshipping Logistics KPIs")

st.title("Dropshipping Logistics — KPI Analyzer")

st.markdown("""
Faça upload do CSV com os dados de pedidos (veja `sample_data.csv` no repo para o esquema). 
Se seus nomes de colunas forem diferentes, use o mapeamento abaixo.
""")

uploaded = st.file_uploader("Upload CSV", type=["csv"])
use_sample = st.checkbox("Usar sample_data.csv de exemplo (se estiver no mesmo diretório)", value=False)

# column remapping UI
st.subheader("Mapeamento de colunas (opcional)")
default_map = {
    "order_id":"order_id",
    "order_date":"order_date",
    "supplier_post_date":"supplier_post_date",
    "tracking_first_update":"tracking_first_update",
    "delivery_date":"delivery_date",
    "carrier":"carrier",
    "carrier_attempts":"carrier_attempts",
    "status":"status",
    "product_cost":"product_cost",
    "shipping_cost":"shipping_cost",
    "refund_amount":"refund_amount",
    "is_returned":"is_returned",
    "is_lost":"is_lost",
    "customs_retained":"customs_retained",
    "packaging_quality_score":"packaging_quality_score",
    "contacts_count":"contacts_count"
}
col_map = {}
cols_ui = st.columns(2)
i = 0
for k,v in default_map.items():
    with cols_ui[i%2]:
        col_map[k] = st.text_input(f"{k}", value=v)
    i += 1

df = None
if uploaded is not None:
    df = pd.read_csv(uploaded)
elif use_sample:
    try:
        df = pd.read_csv("sample_data.csv")
    except Exception as e:
        st.error(f"Não foi possível carregar sample_data.csv: {e}")

if df is not None:
    st.success(f"Dados carregados: {df.shape[0]} linhas × {df.shape[1]} colunas")
    # rename according to mapping
    rename_map = {v:k for k,v in col_map.items() if v in df.columns}
    if rename_map:
        df = df.rename(columns=rename_map)
    # apply loader for types
    df = load_data(df)
    st.dataframe(df.head(200))

    # KPI calc
    promised_days = st.number_input("Promised delivery days (SLA)", value=30, min_value=1)
    report = kpi_report(df, promised_days=int(promised_days))
    kpi_df = kpis_to_dataframe(report)
    st.header("KPIs calculadas")
    st.table(kpi_df.T.rename(columns={0:"value"}).reset_index().rename(columns={"index":"kpi"}))

    # Charts
    st.subheader("Visualizações rápidas")
    # Delivery time distribution
    if 'delivery_date' in df.columns and 'order_date' in df.columns:
        mask = df['delivery_date'].notna() & df['order_date'].notna()
        if mask.sum()>0:
            df['days_to_delivery'] = (df['delivery_date'] - df['order_date']).dt.days
            fig = px.histogram(df.loc[mask], x='days_to_delivery', nbins=30, title='Distribuição do tempo até entrega (dias)')
            st.plotly_chart(fig, use_container_width=True)

    # Transit time
    if 'supplier_post_date' in df.columns and 'tracking_first_update' in df.columns:
        mask2 = df['supplier_post_date'].notna() & df['tracking_first_update'].notna()
        if mask2.sum()>0:
            df['international_transit'] = (df['tracking_first_update'] - df['supplier_post_date']).dt.days
            fig2 = px.box(df.loc[mask2], y='international_transit', title='Transit time internacional (dias) — boxplot')
            st.plotly_chart(fig2, use_container_width=True)

    # Packaging quality
    if 'packaging_quality_score' in df.columns:
        fig3 = px.histogram(df, x='packaging_quality_score', nbins=5, title='Quality score da embalagem')
        st.plotly_chart(fig3, use_container_width=True)

    # Export KPIs
    st.subheader("Exportar KPIs")
    buf = io.BytesIO()
    kpi_df.to_csv(buf, index=False)
    b = buf.getvalue()
    st.download_button("Baixar KPIs CSV", data=b, file_name="kpis_summary.csv", mime="text/csv")

    # Save cleaned dataset
    st.subheader("Exportar dados limpos")
    buf2 = io.BytesIO()
    df.to_csv(buf2, index=False)
    st.download_button("Baixar dados limpos", data=buf2.getvalue(), file_name="cleaned_data.csv", mime="text/csv")

else:
    st.info("Faça upload do CSV ou marque 'Usar sample_data.csv' para testar.")
