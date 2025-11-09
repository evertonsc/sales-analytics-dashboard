# 📊 Dashboard de Excel → Python

Uma **aplicação web interativa** construída com [Streamlit](https://streamlit.io/) e [Plotly](https://plotly.com/python/) que permite gerar automaticamente **gráficos e indicadores chave** a partir de uma planilha Excel ou CSV.
Ideal para análise rápida de dados financeiros, acompanhamento de despesas, receitas ou qualquer conjunto de dados de série temporal com colunas de **Data**, **Valor** e **Categoria**.

🗣 A aplicação está em PT-BR porque o projeto fez parte de uma disciplina universitária e era uma das regras a serem cumpridas.

---

## 🚀 Funcionalidades

- 📂 Upload de arquivos `.xlsx` ou `.csv`
- 🧠 Detecção automática de colunas (Data, Valor, Categoria)
- 📆 Filtragem por intervalo de datas
- 🏷️ Filtragem dinâmica por categoria
- 📈 Gráfico de linha de tendência mensal
- 📊 Gráfico de barras por categoria
- 🧾 Prévia dos dados filtrados

---

## ⚙️ Requisitos

- [Python 3.9+](https://www.python.org/downloads/) instalado.

Antes de executar, instale as dependências:

```bash
pip install streamlit pandas plotly openpyxl
```

---

## ▶️ Como Executar

No terminal, execute:

```bash
streamlit run main.py
```

Se você receber um erro de "command not found", você pode tentar executar como um módulo Python:

```bash
python -m streamlit run main.py
```

O Streamlit abrirá automaticamente seu navegador padrão em:

```
http://localhost:8501
```

---

## 🧠 Como Usar

1. **Faça upload** de um arquivo `.xlsx` ou `.csv` clicando em "Upload a .xlsx or .csv file" ou arrastando e soltando-o.
2. **Selecione as colunas** correspondentes a:
   - Data
   - Valor
   - Categoria (opcional)
3. **Ajuste os filtros** como intervalo de datas e categorias
4. Explore:
   - KPIs principais (Total, Receita, Despesas)
   - Gráficos interativos por mês e categoria
   - Prévia dos dados filtrados

---

## 📄 Planilha de Exemplo (`test_data.xlsx`)

Colunas de dados de exemplo:

| Data       | Valor   | Categoria    |
| ---------- | ------- | ----------- |
| 01/01/2024 | 1500.00 | Vendas       |
| 03/01/2024 | -350.00 | Custos Fixos |
| 07/01/2024 | 1200.00 | Serviços     |
| 10/01/2024 | -100.00 | Materiais    |

P.s: Também estará em PT-BR devido às regras da faculdade.

---

## 🧱 Tecnologias Utilizadas

- [Python 3.9+](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [Plotly Express](https://plotly.com/python/plotly-express/)
- [OpenPyXL](https://openpyxl.readthedocs.io/)
