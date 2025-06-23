import pandas as pd
import streamlit as st
import os

# === Load Dataset ===
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.normpath(os.path.join(current_dir, '..', 'dataset1_complet.csv'))
df = pd.read_csv(csv_path)
df = df.sort_values(["company", "quarter"])

# === Utility Functions ===
def get_local_alerts(row):
    alerts = []
    for score in ["profitability", "liquidity", "solvency", "leverage_adjusted"]:
        local = row.get(f"score_{score}_local")
        if pd.notna(local):
            if local > 0.8:
                alerts.append(f"↑ {score.title()}")
            elif local < 0.2:
                alerts.append(f"↓ {score.title()}")
    if pd.notna(row.get("revenue_growth")):
        if row["revenue_growth"] > 0.1:
            alerts.append("Rev ↑")
        elif row["revenue_growth"] < -0.1:
            alerts.append("Rev ↓")
    return ", ".join(alerts)

def get_global_alerts(row):
    alerts = []
    for score in ["profitability", "liquidity", "solvency", "leverage_adjusted"]:
        global_ = row.get(f"score_{score}_global")
        if pd.notna(global_):
            if global_ > 0.8:
                alerts.append(f"High {score.title()}")
            elif global_ < 0.2:
                alerts.append(f"Low {score.title()}")
    return ", ".join(alerts)

def get_local_status(row):
    thresholds = {
        "score_profitability": {"low": 0.2, "high": 0.8},
        "score_liquidity": {"low": 0.2, "high": 0.8},
        "score_solvency": {"low": 0.2, "high": 0.8},
        "score_leverage_adjusted": {"low": 0.2, "high": 0.8},
        "revenue_growth": {"drop": -0.1, "boost": 0.1}
    }
    red, green = 0, 0
    indicators = {
        "score_profitability": row.get("score_profitability_local"),
        "score_liquidity": row.get("score_liquidity_local"),
        "score_solvency": row.get("score_solvency_local"),
        "score_leverage_adjusted": row.get("score_leverage_adjusted_local")
    }
    for key, value in indicators.items():
        if pd.notna(value):
            if value < thresholds[key]["low"]:
                red += 1
            elif value > thresholds[key]["high"]:
                green += 1

    adj_leverage = indicators["score_leverage_adjusted"]
    rev = row.get("revenue_growth")
    if adj_leverage is not None and adj_leverage < thresholds["score_leverage_adjusted"]["low"]:
        return "Leveraged Risk"
    elif adj_leverage is not None and adj_leverage > thresholds["score_leverage_adjusted"]["high"] and red == 0 and rev is not None and rev > thresholds["revenue_growth"]["boost"]:
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
    elif all(0.2 <= val <= 0.8 for val in indicators.values() if pd.notna(val)):
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
        "Excellent Health": "#c2f7e1"
    }
    return f"background-color: {colors.get(val, '')}"

# === Compute Scores & Format ===
df["Local Alert Summary"] = df.apply(get_local_alerts, axis=1)
df["Global Alert Summary"] = df.apply(get_global_alerts, axis=1)
df["Local Status"] = df.apply(get_local_status, axis=1)
df["Rev Growth"] = df["revenue_growth"].apply(format_percentage)

# === Streamlit Interface ===
st.title("📊 Company Financial Score Dashboard")

# Column dictionary
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
    "Local Status": "Local Status"
}

# --- Select View Mode ---
view_mode = st.radio(
    " Select a view mode:",
    [
        " ",  # placeholder
        "📈 Company Over Time   -> Track one company across quarters",
        "📊 Quarter Comparison  -> Compare all banks in a specific quarter"
    ],
    key="view_mode_radio"
)

# Define internal view mode logic
if "Company Over Time" in view_mode:
    selected_mode = "Company Over Time"
elif "Quarter Comparison" in view_mode:
    selected_mode = "Quarter Comparison"
else:
    selected_mode = None

# === Show score selection if mode selected ===
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

    # === Show table only if score view is selected ===
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
                st.error("❌ Duplicate column names detected after renaming.")
                st.stop()

            if "Local Status" in df_display.columns:
                styled_df = df_display.style.applymap(color_local_status, subset=["Local Status"])
            else:
                styled_df = df_display.style

            st.markdown(styled_df.to_html(escape=False), unsafe_allow_html=True)

        elif selected_mode == "Quarter Comparison":
            st.subheader("📅 Compare All Companies at a Given Quarter")
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
                st.error("❌ Duplicate column names detected after renaming.")
                st.stop()

            if "Local Status" in df_display.columns:
                styled_df = df_display.style.applymap(color_local_status, subset=["Local Status"])
            else:
                styled_df = df_display.style

            st.markdown(styled_df.to_html(escape=False), unsafe_allow_html=True)