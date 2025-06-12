# 📈_Score_Explorer.py

import streamlit as st
import pandas as pd
import os

# --- Load Dataset ---
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.normpath(os.path.join(current_dir, '..', 'dataset1_complet.csv'))

@st.cache_data
def load_data():
    df = pd.read_csv(csv_path)
    df = df.sort_values(["company", "quarter"])
    return df

df = load_data()

# --- UI: Title ---
st.title("📈 Score Evolution Explorer")

# --- Company Selector ---
company = st.selectbox("Select a company:", sorted(df["company"].unique()))
df_company = df[df["company"] == company]

# ✅ Corrected score column mapping
score_options = {
    "Profitability (Local)": "score_profitability_local",
    "Profitability (Global)": "score_profitabilty_global",  # Typo preserved from your dataset
    "Liquidity (Local)": "score_liquidity_local",
    "Liquidity (Global)": "score_liquidity_global",
    "Solvency (Local)": "score_solvency_local",
    "Solvency (Global)": "score_solvency_global",
    "Leverage (Local)": "score_leverage_adjusted_local",
    "Leverage (Global)": "score_leverage_adjusted_global",
}

# --- Multi-Select: What to plot
selected_labels = st.multiselect(
    "Select score indicators to show:",
    options=list(score_options.keys()),
    default=["Profitability (Local)", "Liquidity (Local)"]
)

# --- Extract column names
selected_columns = [score_options[label] for label in selected_labels]

# --- Plot if there’s data
if selected_columns:
    df_plot = df_company[["quarter"] + selected_columns].copy()
    df_plot = df_plot.set_index("quarter")
    df_plot.rename(columns={v: k for k, v in score_options.items()}, inplace=True)

    st.subheader(f"Score Trends for {company}")
    st.line_chart(df_plot)

    # Optional raw data display
    with st.expander("🔍 See raw score data"):
        st.dataframe(df_plot, use_container_width=True)
else:
    st.warning("Please select at least one indicator to display.")
