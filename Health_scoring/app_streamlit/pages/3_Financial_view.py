import pandas as pd
import streamlit as st
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.normpath(os.path.join(current_dir, '..', 'dataset1_complet.csv'))
df = pd.read_csv(csv_path)
df = df.sort_values(["company", "quarter"])

# dynamic thresholds (percentiles)
thresholds_dynamic = {}
score_cols = ["score_profitability_local", "score_liquidity_local", "score_solvency_local", "score_leverage_adjusted_local"]

for col in score_cols:
    low = df[col].quantile(0.1)
    high = df[col].quantile(0.9)
    thresholds_dynamic[col.replace("_local", "")] = {"low": low, "high": high}

# fixed treshold for revenue growth
thresholds_dynamic["revenue_growth"] = {"drop": -0.1, "boost": 0.1}


thresholds_dynamic_global = {}
score_cols_global = ["score_profitability_global", "score_liquidity_global", "score_solvency_global", "score_leverage_adjusted_global"]

for col in score_cols_global:
    low = df[col].quantile(0.1)
    high = df[col].quantile(0.9)
    thresholds_dynamic_global[col.replace("_global", "")] = {"low": low, "high": high}


def get_local_alerts(row):
    alerts = []
    for score in ["profitability", "liquidity", "solvency", "leverage_adjusted"]:
        val = row.get(f"score_{score}_local")
        if pd.notna(val):
            threshold_key = f"score_{score}"  
            if val > thresholds_dynamic[threshold_key]["high"]:
                alerts.append(f"↑ {score.title()}")
            elif val < thresholds_dynamic[threshold_key]["low"]:
                alerts.append(f"↓ {score.title()}")
    rev = row.get("revenue_growth")
    if pd.notna(rev):
        if rev > thresholds_dynamic["revenue_growth"]["boost"]:
            alerts.append("Rev ↑")
        elif rev < thresholds_dynamic["revenue_growth"]["drop"]:
            alerts.append("Rev ↓")
    return ", ".join(alerts)


def get_global_alerts(row):
    alerts = []
    for score in ["profitability", "liquidity", "solvency", "leverage_adjusted"]:
        val = row.get(f"score_{score}_global")
        if pd.notna(val):
            threshold_key = f"score_{score}"  
            if val > thresholds_dynamic_global[threshold_key]["high"]:
                alerts.append(f"High {score.title()}")
            elif val < thresholds_dynamic_global[threshold_key]["low"]:
                alerts.append(f"Low {score.title()}")
    return ", ".join(alerts)


def get_local_status(row):
    red, green = 0, 0
    indicators = {
        "score_profitability": row.get("score_profitability_local"),
        "score_liquidity": row.get("score_liquidity_local"),
        "score_solvency": row.get("score_solvency_local"),
        "score_leverage_adjusted": row.get("score_leverage_adjusted_local")
    }

    available = [val for val in indicators.values() if pd.notna(val)]
    if len(available) < 3:
        return "Insufficient Data"

    for key, value in indicators.items():
        if pd.notna(value):
            if value < thresholds_dynamic[key]["low"]:
                red += 1
            elif value > thresholds_dynamic[key]["high"]:
                green += 1

    adj_leverage = indicators["score_leverage_adjusted"]
    rev = row.get("revenue_growth")

    if adj_leverage is not None and adj_leverage < thresholds_dynamic["score_leverage_adjusted"]["low"]:
        return "Leveraged Risk"
    elif adj_leverage is not None and adj_leverage > thresholds_dynamic["score_leverage_adjusted"]["high"] and red == 0 and rev is not None and rev > thresholds_dynamic["revenue_growth"]["boost"]:
        return "Excellent Health"
    elif red >= 3:
        return "Critical Risk"
    elif red == 2:
        return "Danger"
    elif green >= 2 and red == 0:
        return "Strong"
    elif green > 0 and red == 0:
        return "Good signal"
    elif red == green and red > 0:
        return "Mixed Risk"
    elif red == 1 and green == 0:
        return "Caution"
    elif all(thresholds_dynamic[k]["low"] <= val <= thresholds_dynamic[k]["high"] for k, val in indicators.items() if pd.notna(val)):
        return "Stable"
    else:
        return "Watch"


def get_global_status(row):
    red, green = 0, 0
    indicators = {
        "score_profitability": row.get("score_profitability_global"),
        "score_liquidity": row.get("score_liquidity_global"),
        "score_solvency": row.get("score_solvency_global"),
        "score_leverage_adjusted": row.get("score_leverage_adjusted_global")
    }

    available = [val for val in indicators.values() if pd.notna(val)]
    if len(available) < 3:
        return "Insufficient Data"

    for key, value in indicators.items():
        if pd.notna(value):
            if value < thresholds_dynamic_global[key]["low"]:
                red += 1
            elif value > thresholds_dynamic_global[key]["high"]:
                green += 1

    if red >= 3:
        return "Critical Risk"
    elif red == 2:
        return "Danger"
    elif green >= 2 and red == 0:
        return "Strong"
    elif green > 0 and red == 0:
        return "Good signal"
    elif red == green and red > 0:
        return "Mixed Risk"
    elif red == 1 and green == 0:
        return "Caution"
    elif all(thresholds_dynamic_global[k]["low"] <= val <= thresholds_dynamic_global[k]["high"] for k, val in indicators.items() if pd.notna(val)):
        return "Stable"
    else:
        return "Watch"



def format_percentage(x):
    try:
        return f"{x*100:.1f}%" if pd.notna(x) else ""
    except:
        return x

def color_local_status(val):
    colors = {
        "Strong": "#b6fcb6",
        "Danger": "#ffd3d3",
        "Critical Risk": "#ff9999",
        "Stable": "#f7f7f7",
        "Good signal": "#d1e7dd",
        "Caution": "#fff3cd",
        "Mixed Risk": "#ffe6cc",
        "Leveraged Risk": "#f0c2c2",
        "Excellent Health": "#c2f7e1",
        "Insufficient Data": "#e0e0e0"
    }
    return f"background-color: {colors.get(val, '')}"

# compute scores and format ===
df["Local Alert Summary"] = df.apply(get_local_alerts, axis=1)
df["Global Alert Summary"] = df.apply(get_global_alerts, axis=1)
df["Local Status"] = df.apply(get_local_status, axis=1)
df["Global Status"] = df.apply(get_global_status, axis=1)

df["Rev Growth"] = df["revenue_growth"].apply(format_percentage)


st.title("Company Financial Score Dashboard")


cols = {
    "score_profitability_local": "Profitability (Local)",
    "score_profitability_global": "Profitability (Global)",
    "score_liquidity_local": "Liquidity (Local)",
    "score_liquidity_global": "Liquidity (Global)",
    "score_solvency_local": "Solvency (Local)",
    "score_solvency_global": "Solvency (Global)",
    "score_leverage_adjusted_local": "Adj. Leverage (Local)",
    "score_leverage_adjusted_global": "Adj. Leverage (Global)",
    "Rev Growth": "Revenue Growth",
    "Local Alert Summary": "Local Alerts",
    "Global Alert Summary": "Global Alerts",
    "Local Status": "Local Status",
    "Global Status": "Global Status"
}


view_mode = st.radio(
    " Select a view mode:",
    [
        " ",  
        "📈 Company Over Time   -> Track one company across quarters",
        "📅 Quarter Comparison  -> Compare all banks in a specific quarter"
    ],
    key="view_mode_radio"
)


if "Company Over Time" in view_mode:
    selected_mode = "Company Over Time"
elif "Quarter Comparison" in view_mode:
    selected_mode = "Quarter Comparison"
else:
    selected_mode = None

if selected_mode:

    view_option = st.radio(
        "Select score view:",
        [
            "   ",
            "All Scores                    -> Show both internal (local) and external (global) performance. ",
            "Local Scores Only  -> See how the company is doing compared to its own past results.",
            "Global Scores Only -> See how the company compares to other banks in the market. "
        ],
        key="score_view_radio"
    )
    st.markdown("""
    What do the scores mean:
    - A score of 90% means the company outperforms 90% of peers
    - In other words, it ranks in the top 10%
    """)

    
    if not view_option.startswith("  "):

        if selected_mode == "Company Over Time":
            company = st.selectbox("Select a company:", sorted(df["company"].unique()))
            df_company = df[df["company"] == company].sort_values("quarter", ascending=False)

            if "Local Scores Only" in view_option:
                selected_cols = [col for col in cols if "Local" in cols[col] or col in ["Rev Growth", "Local Alert Summary", "Local Status"]]
            elif "Global Scores Only" in view_option:
                selected_cols = [col for col in cols if "Global" in cols[col] or col == "Global Alert Summary"]
            else:
                selected_cols = list(cols.keys())

            st.subheader(f"📈 Results for {company}")


            for col in selected_cols:
                if "score" in col or "Rev Growth" in col:
                    df_company[col] = df_company[col].apply(format_percentage)

            df_display = df_company[["quarter"] + selected_cols].copy()
            df_display = df_display.rename(columns=cols)

            if df_display.columns.duplicated().any():
                st.error("Duplicate column names detected after renaming.")
                st.stop()

            if "Local Status" in df_display.columns or "Global Status" in df_display.columns:
                style_dict = {}
                if "Local Status" in df_display.columns:
                    style_dict["Local Status"] = color_local_status
                if "Global Status" in df_display.columns:
                    style_dict["Global Status"] = color_local_status

                styled_df = df_display.style
                for colname, color_func in style_dict.items():
                    styled_df = styled_df.applymap(color_func, subset=[colname])
            else:
                styled_df = df_display.style


            st.markdown(styled_df.to_html(escape=False), unsafe_allow_html=True)

        elif selected_mode == "Quarter Comparison":
            st.subheader(" Compare All Companies at a Given Quarter")
            selected_quarter = st.selectbox("Select a quarter:", sorted(df["quarter"].unique(), reverse=True))
            df_quarter = df[df["quarter"] == selected_quarter].copy()

            if "Local Scores Only" in view_option:
                selected_cols = [col for col in cols if "Local" in cols[col] or col in ["Rev Growth", "Local Alert Summary", "Local Status"]]
            elif "Global Scores Only" in view_option:
                selected_cols = [col for col in cols if "Global" in cols[col] or col == "Global Alert Summary"]
            else:
                selected_cols = list(cols.keys())

            for col in selected_cols:
                if "score" in col or "Rev Growth" in col:
                    df_quarter[col] = df_quarter[col].apply(format_percentage)

            df_display = df_quarter[["company"] + selected_cols].copy()
            df_display = df_display.rename(columns=cols)

            if df_display.columns.duplicated().any():
                st.error(" Duplicate column names detected after renaming.")
                st.stop()

            if "Local Status" in df_display.columns or "Global Status" in df_display.columns:
                style_dict = {}
                if "Local Status" in df_display.columns:
                    style_dict["Local Status"] = color_local_status
                if "Global Status" in df_display.columns:
                    style_dict["Global Status"] = color_local_status  

                styled_df = df_display.style
                for colname, color_func in style_dict.items():
                    styled_df = styled_df.applymap(color_func, subset=[colname])
            else:
                styled_df = df_display.style


            st.markdown(styled_df.to_html(escape=False), unsafe_allow_html=True)