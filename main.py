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
    # =========================
    # PRÉVIA + ORDENAR + GRÁFICOS
    # =========================

    # --- Estado e ordenação padrão (Data desc) ---
    if "sort_col" not in st.session_state:
        st.session_state["sort_col"] = date_col
    if "sort_asc" not in st.session_state:
        st.session_state["sort_asc"] = False  # False = desc (mais recente -> mais antigo)

    # Aplica ordenação corrente ao dff ANTES da prévia
    if not dff.empty and st.session_state["sort_col"] in dff.columns:
        dff = dff.sort_values(
            by=st.session_state["sort_col"],
            ascending=st.session_state["sort_asc"]
        )

    # -------- Controles de ordenação (acima da tabela) --------
    st.markdown(
        "<div style='display:flex; gap:8px; align-items:center; margin-top:8px;'>"
        "<span style='opacity:0.8;'>Ordenar:</span>"
        "</div>", unsafe_allow_html=True
    )
    b1, b2, b3, b4, _sp = st.columns([1,1,1,1,6])
    with b1:
        if st.button("Data ▲"):
            st.session_state["sort_col"] = date_col
            st.session_state["sort_asc"] = True
    with b2:
        if st.button("Data ▼"):
            st.session_state["sort_col"] = date_col
            st.session_state["sort_asc"] = False
    with b3:
        if st.button("Valor ▲"):
            st.session_state["sort_col"] = value_col
            st.session_state["sort_asc"] = True
    with b4:
        if st.button("Valor ▼"):
            st.session_state["sort_col"] = value_col
            st.session_state["sort_asc"] = False

    # Reaplica a ordenação após cliques
    if not dff.empty and st.session_state["sort_col"] in dff.columns:
        dff = dff.sort_values(
            by=st.session_state["sort_col"],
            ascending=st.session_state["sort_asc"]
        )

    # -------- Prévia (tabela HTML formatada) --------
    st.subheader("Prévia dos dados filtrados")

    # Função utilitária para moeda BR
    def _format_brl(x: float) -> str:
        try:
            return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except Exception:
            return "-"

    preview_df = dff.head(200).copy()

    # 1) Data em DD/MM/YYYY
    if date_col in preview_df.columns:
        preview_df[date_col] = pd.to_datetime(preview_df[date_col], errors="coerce").dt.strftime("%d/%m/%Y")

    # 2) Valor com "R$" à esquerda e número centralizado
    if value_col in preview_df.columns:
        preview_df[value_col] = preview_df[value_col].apply(
            lambda v: (
                f"<div style='display:flex;align-items:center;'>"
                f"<span style='margin-right:6px;'>R$</span>"
                f"<span style='flex:1;text-align:center;'>{_format_brl(v)}</span>"
                f"</div>"
            ) if pd.notna(v) else "-"
        )

    # Monta HTML da tabela (full width + estilos)
    n_cols = len(preview_df.columns) if not preview_df.empty else 3

    if preview_df.empty:
        # sem margens e bordas internas; mensagem centralizada
        html_table = (
            f'<table border="0" class="dataframe" '
            f'style="width:100%; border-collapse:collapse; margin-bottom:0;">'
            f'<tr><td colspan="{n_cols}" '
            f'style="text-align:center; padding:12px; color:#888;">'
            f'Não há dados para esta seleção.'
            f'</td></tr></table>'
        )
    else:
        html_table = (
            preview_df.to_html(
                escape=False,
                index=False,
                justify="center"
            )
            .replace(
                '<table border="1" class="dataframe">',
                '<table border="0" class="dataframe" '
                'style="width:100%; border-collapse:collapse; margin-bottom:0;">'
            )
            .replace(
                '<th>', '<th style="text-align:center; padding:6px; border-bottom:1px solid #ddd;">'
            )
            .replace(
                '<td>', '<td style="padding:6px; border-bottom:1px solid #f0f0f0;">'
            )
        )

        # Ícones ▲/▼ no header da coluna ordenada (indicadores visuais)
        current_col = st.session_state["sort_col"]
        current_is_asc = st.session_state["sort_asc"]
        arrow = "▲" if current_is_asc else "▼"
        if date_col in preview_df.columns:
            html_table = html_table.replace(
                f">{date_col}<", f">{date_col} {arrow if current_col == date_col else ''}<"
            )
        if value_col in preview_df.columns:
            html_table = html_table.replace(
                f">{value_col}<", f">{value_col} {arrow if current_col == value_col else ''}<"
            )

    # Contêiner com scroll vertical (400px) e borda externa
    scroll_container = (
        '<div style="max-height:400px; overflow-y:auto; width:100%; '
        'border:1px solid #ddd; border-radius:6px;">'
        f'{html_table}'
        '</div>'
    )
    st.markdown(scroll_container, unsafe_allow_html=True)






    # 🔹 Gráficos
    st.markdown("<h3 style='margin-top: 30px; padding-bottom: 0px;'>Gráficos</h3>", unsafe_allow_html=True)

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
