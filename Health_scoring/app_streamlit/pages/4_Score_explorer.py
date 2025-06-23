import streamlit as st
import pandas as pd
import os
import altair as alt

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
st.markdown("""
<div style="background-color: #f0f2f6; padding: 15px; border-radius: 8px;">
<b>📘 How to use this explorer:</b><br><br>
- Select one or more <b>companies</b> from the list to compare their performance.<br>
- Choose the <b>financial indicators</b> (scores) you want to explore.<br>
- The line chart will display the evolution of those scores over time.<br>
- Use the <b>threshold sliders</b> to highlight performance boundaries (e.g. weak/strong zones).<br>
- Hover on lines to see the exact values for each quarter.<br><br>
<b>Tip:</b> You can compare different companies on the same chart and use dashed lines to distinguish score types.
</div>
""", unsafe_allow_html=True)

# --- Score options ---
score_options = {
    "Profitability (Local)": "score_profitability_local",
    "Profitability (Global)": "score_profitabilty_global",  # Typo preserved
    "Liquidity (Local)": "score_liquidity_local",
    "Liquidity (Global)": "score_liquidity_global",
    "Solvency (Local)": "score_solvency_local",
    "Solvency (Global)": "score_solvency_global",
    "Leverage (Local)": "score_leverage_adjusted_local",
    "Leverage (Global)": "score_leverage_adjusted_global",
}

# --- Multi-select company and scores ---
selected_companies = st.multiselect(
    "🏢 Select companies to compare:",
    options=sorted(df["company"].unique())
)

selected_labels = st.multiselect(
    "📊 Select score indicators to show:",
    options=list(score_options.keys())
)

# --- Threshold sliders ---
if selected_companies and selected_labels:
    st.markdown("### 🎯 Threshold Settings")
    low_threshold = st.slider("Low threshold", 0.0, 1.0, 0.2)
    high_threshold = st.slider("High threshold", 0.0, 1.0, 0.8)

    selected_columns = [score_options[label] for label in selected_labels]

    # --- Prepare data
    def prepare_plot_data(df_src, label):
        all_quarters = df["quarter"].sort_values().unique()
        df_plot = df_src[["quarter"] + selected_columns].copy()
        df_plot = df_plot.set_index("quarter").reindex(all_quarters)
        df_plot.fillna(method="ffill", inplace=True)
        df_plot.reset_index(inplace=True)
        df_plot["Company"] = label
        df_plot = df_plot.rename(columns={v: k for k, v in score_options.items()})
        df_melt = df_plot.melt(id_vars=["quarter", "Company"], var_name="Score", value_name="Value")
        return df_melt

    df_all = pd.concat([
        prepare_plot_data(df[df["company"] == comp], comp)
        for comp in selected_companies
    ])

    # --- Chart
    base_chart = alt.Chart(df_all).mark_line(point=True).encode(
        x=alt.X("quarter:O", title="Quarter"),
        y=alt.Y("Value:Q", scale=alt.Scale(domain=[0, 1]), title="Score"),
        color=alt.Color("Company:N", title="Company"),
        strokeDash=alt.StrokeDash("Score:N", title="Indicator"),
        tooltip=["quarter", "Company", "Score", alt.Tooltip("Value", format=".2f")]
    )

    threshold_df = pd.DataFrame({
        "y": [low_threshold, high_threshold],
        "Label": ["Low Threshold", "High Threshold"]
    })
    threshold_lines = alt.Chart(threshold_df).mark_rule(strokeDash=[4, 4], color="gray").encode(
        y="y:Q",
        tooltip="Label"
    )

    st.subheader("📊 Score Trends")
    st.altair_chart((base_chart + threshold_lines).properties(width=1000, height=500), use_container_width=True)

   