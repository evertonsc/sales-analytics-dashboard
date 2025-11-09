import io
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta

def preprocess_data(df):
    """Cleans and preprocesses the dataframe."""
    df.columns = [c.strip() for c in df.columns]
    date_col = next((c for c in df.columns if "data" in c.lower()), df.columns[0])
    value_col = next((c for c in df.columns if "valor" in c.lower() or "amount" in c.lower()), df.columns[1])
    category_col = next((c for c in df.columns if "categ" in c.lower()), None)

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
        except (ValueError, TypeError):
            return None
    df[value_col] = df[value_col].apply(to_float)
    df = df.dropna(subset=[value_col])

    if category_col:
        df[category_col] = df[category_col].astype(str).fillna("Sem categoria")
    else:
        category_col = "__categoria__"
        df[category_col] = "Total"
        
    return df, date_col, value_col, category_col

def apply_filters(df, date_col, value_col, category_col):
    """Displays filters and returns the filtered dataframe."""
    st.subheader("Filtros")
    col_selection = st.selectbox("Coluna", ["Data", "Valor", "Categoria"])

    if col_selection == "Data":
        today = datetime.today().date()
        min_d, max_d = df[date_col].min().date(), df[date_col].max().date()
        custom_period_current = st.session_state.get("custom_period", False)
        period_fixed = st.selectbox(
            "Período Fixo",
            ["Hoje", "Última semana", "Último mês", "Últimos três meses", "Último semestre", "Último ano"],
            disabled=custom_period_current,
            key="period_fixed_box"
        )
        custom_period = st.checkbox("Período Customizado", value=custom_period_current, key="custom_period")

        if custom_period:
            st.session_state["disable_period_fixed"] = True
        else:
            st.session_state["disable_period_fixed"] = False

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Data Início", value=min_d, disabled=not custom_period, min_value=min_d, max_value=max_d)
        with col2:
            end_date = st.date_input("Data Fim", value=max_d, disabled=not custom_period, min_value=min_d, max_value=max_d)

        if not custom_period:
            if period_fixed == "Hoje":
                start_date, end_date = today, today
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
            else:
                mask = df[value_col] < v
        dff = df.loc[mask].copy()

    else: # Categoria
        categorias = sorted(pd.Series(df[category_col].astype(str)).unique().tolist())
        if not categorias:
            st.info("Nenhuma categoria encontrada na planilha.")
            dff = df.iloc[0:0].copy()
        else:
            selected_cat = st.selectbox("Categoria", options=categorias, index=0, key="categoria_select")
            dff = df.loc[df[category_col] == selected_cat].copy()
            
    return dff, col_selection

def _format_brl(x: float) -> str:
    """Formats a float to a BRL currency string."""
    try:
        return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "-"

def display_dashboard(dff, date_col, value_col, category_col, col_selection):
    """Displays the dashboard components."""
    st.subheader("Indicadores")
    total = dff[value_col].sum()
    st.metric("Total", f"R$ {_format_brl(total)}")

    st.subheader("Prévia dos dados filtrados")

    # --- Sorting ---
    if not dff.empty:
        sort_cols = list(dff.columns)
        
        # Garante que a coluna de data padrão esteja na lista de opções
        default_sort_col = date_col if date_col in sort_cols else sort_cols[0]
        
        # Se a coluna de ordenação salva não estiver mais disponível, reseta
        if st.session_state.get("sort_col") not in sort_cols:
            st.session_state["sort_col"] = default_sort_col
        
        # Se a ordem não estiver definida, define como descendente
        if "sort_asc" not in st.session_state:
            st.session_state["sort_asc"] = False

        c1, c2 = st.columns(2)
        with c1:
            # Usa o índice da coluna salva para o selectbox
            saved_col_index = sort_cols.index(st.session_state["sort_col"])
            st.session_state["sort_col"] = st.selectbox(
                "Ordenar por", 
                options=sort_cols,
                index=saved_col_index
            )
        with c2:
            order_options = ["Descendente", "Ascendente"]
            # Usa o estado salvo para definir o índice do selectbox de ordem
            saved_order_index = 1 if st.session_state["sort_asc"] else 0
            order_selection = st.selectbox(
                "Ordem", 
                options=order_options,
                index=saved_order_index
            )
            st.session_state["sort_asc"] = (order_selection == "Ascendente")

        dff = dff.sort_values(
            by=st.session_state["sort_col"],
            ascending=st.session_state["sort_asc"]
        )

    # --- Data Preview ---
    preview_df = dff.head(200).copy()
    if date_col in preview_df.columns:
        preview_df[date_col] = pd.to_datetime(preview_df[date_col], errors="coerce").dt.strftime("%d/%m/%Y")
    if value_col in preview_df.columns:
        preview_df[value_col] = preview_df[value_col].apply(
            lambda v: f"<div style='display:flex;align-items:center;'><span style='margin-right:6px;'>R$</span><span style='flex:1;text-align:center;'>{_format_brl(v)}</span></div>" if pd.notna(v) else "-"
        )
    if col_selection == "Categoria" and category_col in preview_df.columns:
        preview_df = preview_df.drop(columns=[category_col])

    n_cols = len(preview_df.columns) if not preview_df.empty else 3
    if preview_df.empty:
        html_table = f'<table border="0" class="dataframe" style="width:100%; border-collapse:collapse; margin-bottom:0;"><tr><td colspan="{n_cols}" style="text-align:center; padding:12px; color:#888;">Não há dados para esta seleção.</td></tr></table>'
    else:
        html_table = (
            preview_df.to_html(escape=False, index=False, justify="center")
            .replace('<table border="1" class="dataframe">', '<table border="0" class="dataframe" style="width:100%; border-collapse:collapse; margin-bottom:0;">')
            .replace('<th>', '<th style="text-align:center; padding:6px; border-bottom:1px solid #ddd;">')
            .replace('<td>', '<td style="padding:6px; border-bottom:1px solid #f0f0f0;">')
        )
    scroll_container = f'<div style="max-height:400px; overflow-y:auto; width:100%; border:1px solid #ddd; border-radius:6px;">{html_table}</div>'
    st.markdown(scroll_container, unsafe_allow_html=True)

    # --- Charts ---
    st.markdown("<h3 style='margin-top: 30px; padding-bottom: 0px;'>Gráficos</h3>", unsafe_allow_html=True)
    
    # Garante que a coluna 'Mês' exista antes de agrupar
    if not dff.empty:
        dff["Mês"] = dff[date_col].dt.to_period("M").dt.to_timestamp()
    else:
        dff["Mês"] = pd.Series(dtype='datetime64[ns]')


    palette = px.colors.qualitative.Set2
    base_layout = dict(template="simple_white", margin=dict(t=60, r=20, b=20, l=20), title_x=0.02, legend_title_text="")

    # Monthly evolution
    serie = dff.groupby("Mês", as_index=False)[value_col].sum().sort_values("Mês")
    fig_area = px.area(serie, x="Mês", y=value_col, title="Evolução mensal do valor")
    fig_area.update_traces(mode="lines+markers", marker=dict(size=6, line=dict(width=0)), hovertemplate="Mês: %{x|%b/%Y}<br>Total: R$ %{y:,.2f}<extra></extra>")
    fig_area.update_yaxes(title=None, showgrid=True, gridcolor="rgba(0,0,0,0.07)", tickprefix="R$ ", tickformat=",.2f", zeroline=False)
    fig_area.update_xaxes(title=None, dtick="M1", tickformat="%b/%y", showgrid=False)
    fig_area.update_layout(**base_layout)

    # Category participation
    by_cat = dff.groupby(category_col, as_index=False)[value_col].sum().sort_values(value_col, ascending=False)
    if not by_cat.empty:
        fig_bar = px.bar(by_cat, y=category_col, x=value_col, orientation="h", title="Participação por categoria", color=category_col, color_discrete_sequence=palette, text=by_cat[value_col].map(lambda v: f"R$ {_format_brl(v)}"))
        fig_bar.update_traces(textposition="outside", hovertemplate=f"{category_col}: "+"%{y}<br>Total: R$ %{x:,.2f}<extra></extra>", showlegend=False)
        fig_bar.update_yaxes(title=None, categoryorder="total ascending")
        fig_bar.update_xaxes(title=None, showgrid=True, gridcolor="rgba(0,0,0,0.07)", tickprefix="R$ ", tickformat=",.2f", zeroline=False)
        fig_bar.update_layout(**base_layout)

    gcol1, gcol2 = st.columns(2)
    with gcol1:
        st.plotly_chart(fig_area, use_container_width=True, config={"displaylogo": False, "locale": "pt-BR"})
    with gcol2:
        if not by_cat.empty:
            st.plotly_chart(fig_bar, use_container_width=True, config={"displaylogo": False, "locale": "pt-BR"})
        else:
            st.info("Sem categorias para exibir o gráfico.")

st.set_page_config(page_title="Dashboard", layout="wide")
st.title("📊 Dashboard a partir de Planilha (Excel/CSV)")
st.caption("Carregue sua planilha e visualize gráficos e indicadores dinâmicos.")

uploaded = st.file_uploader("Envie um arquivo .xlsx ou .csv", type=["xlsx", "csv"])

@st.cache_data
def load_data(file):
    """Loads data from an uploaded .xlsx or .csv file."""
    if file.name.lower().endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file, engine="openpyxl")
    return df

if uploaded:
    df_raw = load_data(uploaded).copy()
    df_processed, date_col, value_col, category_col = preprocess_data(df_raw)
    df_filtered, col_selection = apply_filters(df_processed, date_col, value_col, category_col)
    display_dashboard(df_filtered, date_col, value_col, category_col, col_selection)
else:
    st.info("⬆️ Envie um .xlsx ou .csv para começar. Dica: use colunas como **Data**, **Valor** e **Categoria**.")