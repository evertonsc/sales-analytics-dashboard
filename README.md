# 📊 Excel → Python Dashboard

An **interactive web application** built with [Streamlit](https://streamlit.io/) and [Plotly](https://plotly.com/python/) that allows you to automatically generate **charts and key indicators** from an Excel or CSV spreadsheet.  
Ideal for quick financial data analysis, tracking expenses, revenues, or any time-series dataset with **Date**, **Value**, and **Category** columns.

🗣 Application is in PT-BR because it was part of a college subject and it was one of the rules needed to accomplish.

---

## 🚀 Features

- 📂 Upload `.xlsx` or `.csv` files  
- 🧠 Automatic column detection (*Date*, *Value*, *Category*)  
- 📆 Date range filtering  
- 🏷️ Dynamic category filtering  
- 💡 Automatic KPI calculation (Total, Income, Expenses)  
- 📈 Monthly trend line chart  
- 📊 Category-wise bar chart  
- 🧾 Filtered data preview  

---

## ⚙️ Requirements

- [Python 3.9+](https://www.python.org/downloads/) installed.

Before running, install the dependencies:
```bash
pip install streamlit pandas plotly openpyxl
```

---

## ▶️ How to Run

In the terminal, execute:

```bash
streamlit run main.py
```

Streamlit will automatically open your default browser at:
```
http://localhost:8501
```

---

## 🧠 How to Use

1. **Upload** an `.xlsx` or `.csv` file by clicking *"Upload a .xlsx or .csv file"*  or drag and drop it.
2. **Select the columns** corresponding to:
   - Date  
   - Value  
   - Category (optional)  
3. **Adjust filters** such as date range and categories  
4. Explore:
   - Main KPIs (Total, Income, Expenses)
   - Interactive charts by month and category
   - Preview of the filtered data

---

## 📄 Example Spreadsheet (`test_data.xlsx`)

Example data columns:

| Date       | Value    | Category       |
|-------------|-----------|----------------|
| 01/01/2024  | 1500.00   | Sales          |
| 03/01/2024  | -350.00   | Fixed Costs    |
| 07/01/2024  | 1200.00   | Services       |
| 10/01/2024  | -100.00   | Materials      |

P.s: It will also be in PT-BR because of college rules.

---

## 🧱 Technologies Used

- [Python 3.9+](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [Plotly Express](https://plotly.com/python/plotly-express/)
- [OpenPyXL](https://openpyxl.readthedocs.io/)
