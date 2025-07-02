import streamlit as st
import pandas as pd
import os
import altair as alt

current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.normpath(os.path.join(current_dir, '..', 'dataset1_complet.csv'))

@st.cache_data
def load_data():
    df = pd.read_csv(csv_path)
    df = df.sort_values(["company", "quarter"])
    return df

df = load_data()

st.title("Score Evolution Explorer")
st.markdown("""
<div style="background-color: #f0f2f6; padding: 15px; border-radius: 8px;">
<b>How to use this explorer:</b><br><br>
- Select one or more <b>companies</b> from the list to compare their performance.<br>
- Choose the <b>financial indicators</b> (scores) you want to explore.<br>
- Optionally, add <b>macroeconomic variables</b> (ex : GDP growth, inflation, interest rate) to provide external context.<br>
- These macro values are visually centered to align with financial indicators on the chart.<br>
- The line chart will display the evolution over time for all selected indicators.<br>
- Use the <b>threshold sliders</b> to highlight performance boundaries (ex : weak/strong zones).<br>
- Hover on the lines to see exact values for each quarter.<br><br>
<b>Tip:</b> You can compare different companies and visualize their sensitivity to economic environments.
</div>
""", unsafe_allow_html=True)

score_options = {
    "Profitability (Local)": "score_profitability_local",
    "Profitability (Global)": "score_profitability_global",  
    "Liquidity (Local)": "score_liquidity_local",
    "Liquidity (Global)": "score_liquidity_global",
    "Solvency (Local)": "score_solvency_local",
    "Solvency (Global)": "score_solvency_global",
    "Leverage (Local)": "score_leverage_adjusted_local",
    "Leverage (Global)": "score_leverage_adjusted_global",
    "Revenue Growth": "revenue_growth"
}

macro_options = {
    "Inflation (YoY)": "inflation_YoY",
    "GDP Growth Rate": "gdp_growth_rate",
    "Interest Rate": "interest_rate"
}

selected_companies = st.multiselect(
    "Select companies to compare:",
    options=sorted(df["company"].unique())
)

selected_labels = st.multiselect(
    "Select score indicators to show:",
    options=list(score_options.keys())
)

selected_macro = st.multiselect(
    "Optional: Add macroeconomic variables:",
    options=list(macro_options.keys())
)

if selected_companies and selected_labels:
    st.markdown("### Threshold Settings")
    low_threshold = st.slider("Low threshold", 0.0, 1.0, 0.2)
    high_threshold = st.slider("High threshold", 0.0, 1.0, 0.8)

    selected_columns = [score_options[label] for label in selected_labels]
    macro_columns = [macro_options[m] for m in selected_macro]

    def prepare_plot_data(df_src, label):
        all_quarters = df["quarter"].sort_values().unique()
        df_plot = df_src[["quarter"] + selected_columns].copy()
        df_plot = df_plot.set_index("quarter").reindex(all_quarters)
        df_plot.fillna(method="ffill", inplace=True)
        df_plot.fillna(method="bfill", inplace=True)
        df_plot.reset_index(inplace=True)
        df_plot["Company"] = label

        if "revenue_growth" in df_plot.columns and df_plot["revenue_growth"].notna().any():
            mean_rev = df_plot["revenue_growth"].mean()
            df_plot["revenue_growth"] = df_plot["revenue_growth"] - mean_rev + 0.5
            

        df_plot = df_plot.rename(columns={v: k for k, v in score_options.items()})
        df_melt = df_plot.melt(id_vars=["quarter", "Company"], var_name="Score", value_name="Value")
        df_melt["Value"] = df_melt["Value"].fillna(0.5)
        
        return df_melt

    def prepare_macro_data(df_src, label):
        df_macro = df_src[["quarter"] + macro_columns].copy()
        df_macro["Company"] = label
        df_macro = df_macro.sort_values("quarter")

        for col in macro_columns:
            df_macro[col] = df_macro[col].clip(-1, 1) + 0.5

        df_macro = df_macro.rename(columns={v: k for k, v in macro_options.items()})

        df_melt = df_macro.melt(id_vars=["quarter", "Company"], var_name="Score", value_name="Value")
        df_melt["Value"] = df_melt["Value"].fillna(0.5)

        # NEW → Add LineType column
        df_melt["LineType"] = "dotted"

        return df_melt

    df_all = pd.concat([
        prepare_plot_data(df[df["company"] == comp], comp)
        for comp in selected_companies
    ])

    if selected_macro:
        df_macro_all = pd.concat([
            prepare_macro_data(df[df["company"] == comp], comp)
            for comp in selected_companies
        ])
        df_all = pd.concat([df_all, df_macro_all])

    base_chart = alt.Chart(df_all).mark_line(point=True).encode(
    x=alt.X("quarter:O", title="Quarter"),
    y=alt.Y("Value:Q", scale=alt.Scale(domain=[0, 1]), title="Value"),
    color=alt.Color("Company:N", title="Company"),
    
    strokeDash=alt.StrokeDash(
    "LineType:N",
    scale=alt.Scale(
        domain=["solid", "dotted"],
        range=[[1, 0], [4, 4]]
    ),
    legend=None
),

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

    st.subheader("Score Trends")
    st.altair_chart((base_chart + threshold_lines).properties(width=1000, height=500), use_container_width=True)
