import pandas as pd
import streamlit as st

# Load your actual normalized dataset (replace this with your real DataFrame)
df = dataset_normalized.copy()

# Define helper functions
def classify_score(score):
    if pd.isna(score):
        return "Missing"
    elif score < 0.2:
        return "Red"
    elif score < 0.7:
        return "Yellow"
    else:
        return "Green"

def classify_revenue_alert(value):
    if pd.isna(value):
        return "Unknown"
    elif value < -10:
        return "Rev ↓"
    elif value > 10:
        return "Rev ↑"
    else:
        return "Stable"

def alert_summary(row):
    alerts = []
    if classify_score(row['score_profitability']) == 'Red':
        alerts.append("Profit")
    if classify_score(row['score_liquidity']) == 'Red':
        alerts.append("Liquidity")
    if classify_score(row['score_solvency']) == 'Red':
        alerts.append("Solvency")
    if classify_score(row['score_leverage_ajusted_localc']) == 'Red':
        alerts.append("Adj. Leverage")

    alert_text = f"Red ({', '.join(alerts)})" if alerts else ""
    rev = classify_revenue_alert(row['revenue_growth'])
    if rev == "Rev ↓":
        alert_text += ", Rev ↓" if alert_text else "Rev ↓"
    elif rev == "Rev ↑":
        alert_text += ", Rev ↑" if alert_text else "Rev ↑"

    return alert_text if alert_text else "Stable"

# Streamlit layout
st.set_page_config(page_title="Company Score Dashboard", layout="wide")
st.title("📊 Financial Score Dashboard")

# Company selection
companies = df['company'].dropna().unique()
selected_company = st.selectbox("Select a company:", sorted(companies))

# Filter data
df_filtered = df[df['company'] == selected_company].copy()
df_filtered["Rev Growth"] = df_filtered["revenue_growth"].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "")
df_filtered["Alert Summary"] = df_filtered.apply(alert_summary, axis=1)

# Table output
summary = df_filtered[[
    "quarter", "score_profitability", "score_liquidity", "score_solvency",
    "score_leverage_ajusted_localc", "Rev Growth", "Alert Summary"
]].rename(columns={
    "quarter": "Quarter",
    "score_profitability": "Profitability",
    "score_liquidity": "Liquidity",
    "score_solvency": "Solvency",
    "score_leverage_ajusted_localc": "Adj. Leverage"
}).reset_index(drop=True)

st.dataframe(summary, use_container_width=True)
