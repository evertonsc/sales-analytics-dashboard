import io
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Dashboard", layout="wide")

st.title("📊 Dashboard a partir de Planilha (Excel/CSV)")
st.caption("Carregue sua planilha e visualize gráficos e indicadores dinâmicos.")

uploaded = st.file_uploader("Envie um arquivo .xlsx ou .csv", type=["xlsx", "csv"])

@st.cache_data
def load_data(file):
    if file.name.lower().endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file, engine="openpyxl")
    df.columns = [c.strip() for c in df.columns]
    return df

if uploaded:
    df = load_data(uploaded).copy()

    # Identifica colunas automaticamente
    date_col = next((c for c in df.columns if "data" in c.lower()), df.columns[0])
    value_col = next((c for c in df.columns if "valor" in c.lower() or "amount" in c.lower()), df.columns[1])
    category_col = next((c for c in df.columns if "categ" in c.lower()), None)

    # Conversões
    try:
        df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")
    except Exception:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col])

    def to_float(x):
        if isinstance(x, str):
            x = x.replace(".", "").replace(",", ".")
        try:
            return float(x)
        except:
            return None
    df[value_col] = df[value_col].apply(to_float)
    df = df.dropna(subset=[value_col])

    if category_col:
        df[category_col] = df[category_col].astype(str).fillna("Sem categoria")
    else:
        df["__categoria__"] = "Total"
        category_col = "__categoria__"

    # 🔹 Filtros
    st.subheader("Filtros")

    col_selection = st.selectbox("Coluna", ["Data", "Valor", "Categoria"])

    # ================== COLUNA: DATA ==================
    if col_selection == "Data":
        today = datetime.today().date()
        min_d, max_d = df[date_col].min().date(), df[date_col].max().date()

        # Lemos o estado atual do checkbox ANTES de renderizar o selectbox,
        # para manter a ordem visual (selectbox -> checkbox -> datas) sem duplicar o selectbox.
        custom_period_current = st.session_state.get("custom_period", False)

        # 1) Selectbox "Período Fixo" (vem ANTES visualmente)
        period_fixed = st.selectbox(
            "Período Fixo",
            ["Hoje", "Última semana", "Último mês", "Últimos três meses", "Último semestre", "Último ano"],
            disabled=custom_period_current,
            key="period_fixed_box"
        )

        # 2) Checkbox "Período Customizado" (vem logo depois e controla o estado acima)
        custom_period = st.checkbox("Período Customizado", value=custom_period_current, key="custom_period")


        # Atualiza dinamicamente o estado do Período Fixo (desabilita se custom for marcado)
        if custom_period:
            st.session_state["disable_period_fixed"] = True
        else:
            st.session_state["disable_period_fixed"] = False

        # Campos de data
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Data Início", value=min_d, disabled=not custom_period, min_value=min_d, max_value=max_d)
        with col2:
            end_date = st.date_input("Data Fim", value=max_d, disabled=not custom_period, min_value=min_d, max_value=max_d)

        # Define o período automático se não for customizado
        if not custom_period:
            if period_fixed == "Hoje":
                start_date = today
                end_date = today
            elif period_fixed == "Última semana":
                start_date = today - timedelta(days=6)
                end_date = today
            elif period_fixed == "Último mês":
                start_date = today - timedelta(days=30)
                end_date = today
            elif period_fixed == "Últimos três meses":
                start_date = today - timedelta(days=90)
                end_date = today
            elif period_fixed == "Último semestre":
                start_date = today - timedelta(days=182)
                end_date = today
            elif period_fixed == "Último ano":
                start_date = today - timedelta(days=365)
                end_date = today

        mask = (df[date_col].dt.date >= start_date) & (df[date_col].dt.date <= end_date)
        dff = df.loc[mask].copy()
    
    # ================== COLUNA: VALOR ==================
    elif col_selection == "Valor":
        st.markdown("Filtre pelos valores da coluna selecionada.")
        comparator = st.selectbox("Condição", ["Maior que", "Menor que", "Entre", "Igual a"])


        if comparator == "Entre":
            c1, c2 = st.columns(2)
            with c1:
                v1 = st.number_input("Valor inicial", value=0.0, key="valor_inicial")
            with c2:
                v2 = st.number_input("Valor final", value=0.0, key="valor_final")
            low, high = (v1, v2) if v1 <= v2 else (v2, v1)
            mask = (df[value_col] >= low) & (df[value_col] <= high)
        else:
            v = st.number_input("Valor", value=0.0, key="valor_unico")
            if comparator == "Igual a":
                mask = df[value_col] == v
            elif comparator == "Maior que":
                mask = df[value_col] > v
            else:  # Menor que
                mask = df[value_col] < v

        dff = df.loc[mask].copy()

    # ================== COLUNA: CATEGORIA ==================
    else:
        # Mapear categorias a partir da planilha
        categorias = sorted(pd.Series(df[category_col].astype(str)).unique().tolist())
        if not categorias:
            st.info("Nenhuma categoria encontrada na planilha.")
            dff = df.iloc[0:0].copy()
        else:
            selected_cat = st.selectbox("Categoria", options=categorias, index=0, key="categoria_select")
            dff = df.loc[df[category_col] == selected_cat].copy()

    # 🔹 Indicadores
    st.subheader("Indicadores")
    total = dff[value_col].sum()
    st.metric("Total", f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # 🔹 Prévia dos dados filtrados
    st.subheader("Prévia dos dados filtrados")
    st.dataframe(dff.head(200))


    # 🔹 Gráficos
    st.subheader("Gráficos")
    dff["Mês"] = dff[date_col].dt.to_period("M").dt.to_timestamp()

    gcol1, gcol2 = st.columns(2)
    with gcol1:
        fig_line = px.line(dff.groupby("Mês")[value_col].sum().reset_index(),
                           x="Mês", y=value_col, markers=True, title="Soma por mês")
        st.plotly_chart(fig_line, use_container_width=True)
    with gcol2:
        by_cat = dff.groupby(category_col)[value_col].sum().reset_index().sort_values(value_col, ascending=False)
        fig_bar = px.bar(by_cat, x=category_col, y=value_col, title="Soma por categoria")
        st.plotly_chart(fig_bar, use_container_width=True)

    
else:
    st.info("⬆️ Envie um .xlsx ou .csv para começar. Dica: use colunas como **Data**, **Valor** e **Categoria**.")
