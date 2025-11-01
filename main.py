
import io
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Dashboard Excel → Python", layout="wide")

st.title("📊 Dashboard a partir de Planilha (Excel/CSV)")
st.caption("Carregue sua planilha, selecione as colunas e gere gráficos e indicadores interativos.")

uploaded = st.file_uploader("Envie um arquivo .xlsx ou .csv", type=["xlsx", "csv"])

@st.cache_data
def load_data(file):
    if file.name.lower().endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file, engine="openpyxl")
    # Tenta normalizar nomes de colunas comuns
    df.columns = [c.strip() for c in df.columns]
    return df

if uploaded:
    df = load_data(uploaded)

    st.subheader("Configurações")
    cols = df.columns.tolist()
    col1, col2, col3 = st.columns(3)

    with col1:
        date_col = st.selectbox("Coluna de Data", options=cols, index=next((i for i,c in enumerate(cols) if "data" in c.lower()), 0))
    with col2:
        value_col = st.selectbox("Coluna de Valor", options=cols, index=next((i for i,c in enumerate(cols) if "valor" in c.lower() or "amount" in c.lower()), 0))
    with col3:
        category_col = st.selectbox("Coluna de Categoria (opcional)", options=["<nenhuma>"] + cols, index=0)

    # Conversões
    df = df.copy()
    # Data
    try:
        df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")
    except Exception:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col])

    # Valor (tenta converter formato PT-BR)
    def to_float(x):
        if isinstance(x, str):
            x = x.replace(".", "").replace(",", ".")
        try:
            return float(x)
        except Exception:
            return None
    df[value_col] = df[value_col].apply(to_float)
    df = df.dropna(subset=[value_col])

    # Categoria
    if category_col != "<nenhuma>":
        df[category_col] = df[category_col].astype(str).fillna("Sem categoria")
    else:
        df["__categoria__"] = "Total"
        category_col = "__categoria__"

    # Filtros
    st.subheader("Filtros")
    min_d, max_d = df[date_col].min().date(), df[date_col].max().date()
    f1, f2 = st.columns(2)
    with f1:
        date_range = st.date_input("Período", value=(min_d, max_d), min_value=min_d, max_value=max_d)
    with f2:
        cats = sorted(df[category_col].unique().tolist())
        sel_cats = st.multiselect("Categorias", options=cats, default=cats)

    d1, d2 = date_range
    mask = (
        (df[date_col].dt.date >= d1) &
        (df[date_col].dt.date <= d2) &
        (df[category_col].isin(sel_cats))
    )
    dff = df.loc[mask].copy()

    # KPIs
    st.subheader("Indicadores")
    k1, k2, k3 = st.columns(3)
    total = dff[value_col].sum()
    pos = dff.loc[dff[value_col] >= 0, value_col].sum()
    neg = dff.loc[dff[value_col] < 0, value_col].sum()
    with k1:
        st.metric("Total", f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    with k2:
        st.metric("Entradas (≥ 0)", f"R$ {pos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    with k3:
        st.metric("Saídas (< 0)", f"R$ {neg:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # Agregações por mês
    dff["Mês"] = dff[date_col].dt.to_period("M").dt.to_timestamp()
    by_month = dff.groupby("Mês")[value_col].sum().reset_index()

    st.subheader("Gráficos")
    gcol1, gcol2 = st.columns(2)
    with gcol1:
        fig_line = px.line(by_month, x="Mês", y=value_col, markers=True, title="Soma por mês")
        st.plotly_chart(fig_line, use_container_width=True)
    with gcol2:
        by_cat = dff.groupby(category_col)[value_col].sum().reset_index().sort_values(value_col, ascending=False)
        fig_bar = px.bar(by_cat, x=category_col, y=value_col, title="Soma por categoria")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("Prévia dos dados filtrados")
    st.dataframe(dff.head(200))
else:
    st.info("⬆️ Envie um .xlsx ou .csv para começar. Dica: use colunas como **Data**, **Valor** e **Categoria**.")
