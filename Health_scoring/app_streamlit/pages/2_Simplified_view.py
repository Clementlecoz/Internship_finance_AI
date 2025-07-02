import pandas as pd
import streamlit as st
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.normpath(os.path.join(current_dir, '..', 'dataset1_complet.csv'))
df = pd.read_csv(csv_path)
df = df.sort_values(["company", "quarter"])

# thresholds
thresholds_dynamic = {}
thresholds_dynamic_global = {}
score_cols_local = ["score_profitability_local", "score_liquidity_local", "score_solvency_local", "score_leverage_adjusted_local"]
score_cols_global = ["score_profitability_global", "score_liquidity_global", "score_solvency_global", "score_leverage_adjusted_global"]

for col in score_cols_local:
    low = df[col].quantile(0.1)
    high = df[col].quantile(0.9)
    thresholds_dynamic[col.replace("_local", "")] = {"low": low, "high": high}

for col in score_cols_global:
    low = df[col].quantile(0.1)
    high = df[col].quantile(0.9)
    thresholds_dynamic_global[col.replace("_global", "")] = {"low": low, "high": high}

thresholds_dynamic["revenue_growth"] = {"drop": -0.1, "boost": 0.1}

# same functions as before
def get_local_alerts(row):
    alerts = []
    for score in ["profitability", "liquidity", "solvency", "leverage_adjusted"]:
        val = row.get(f"score_{score}_local")
        if pd.notna(val):
            key = f"score_{score}"
            if val > thresholds_dynamic[key]["high"]:
                alerts.append(f"↑ {score.title()}")
            elif val < thresholds_dynamic[key]["low"]:
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
            key = f"score_{score}"
            if val > thresholds_dynamic_global[key]["high"]:
                alerts.append(f"High {score.title()}")
            elif val < thresholds_dynamic_global[key]["low"]:
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

def get_recommendation(row):
    local_alerts = get_local_alerts(row)
    global_alerts = get_global_alerts(row)
    if not local_alerts and not global_alerts:
        return "No specific concern or strength detected."
    return f"Local: {local_alerts}. Global: {global_alerts}."

def color_status(val):
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


df["Local Alert Summary"] = df.apply(get_local_alerts, axis=1)
df["Global Alert Summary"] = df.apply(get_global_alerts, axis=1)
df["Local Status"] = df.apply(get_local_status, axis=1)
df["Global Status"] = df.apply(get_global_status, axis=1)
#df["Recommendation"] = df.apply(get_recommendation, axis=1)

# streamlit app
st.title("Simplified Financial Health View")

st.markdown("""
This view provides an **accessible summary** of each company's financial health over time.
It focuses on:

- Key **alerts** and **signals** per quarter (ex : profitability drop, revenue drop),
- Whether a quarter was strong, weak, or required attention,
- Simple **recommendations** for interpretation.
""")


company = st.selectbox("Select a company to analyze:", [""] + sorted(df["company"].unique()))


if company:
    df_company = df[df["company"] == company]

    risk_count = df_company["Local Status"].isin([
        "Critical Risk", "Leveraged Risk"
    ]).sum()

    danger_count = df_company["Local Status"].isin([
        "Danger", "Caution"
    ]).sum()

    strong_count = df_company["Local Status"].isin([
        "Strong", "Excellent Health"
    ]).sum()

    st.subheader(f" Local Summary for {company}")
    st.markdown(f"""
    - **🛑 Quarters at Risk:** {risk_count}
    - **⚠️ Danger/Watch Quarters:** {danger_count}
    - **✅ Strong Quarters:** {strong_count}
    """)

   
    st.markdown(" Quarter-by-Quarter Summary")
    cols_display = {
        "quarter": "Quarter",
        "Local Status": "Local Status",
        "Global Status": "Global Status",
        "Local Alert Summary": "Local Alerts",
        "Global Alert Summary": "Global Alerts",
        #"Recommendation": "Recommendation"
    }
    df_display = df_company[list(cols_display.keys())].rename(columns=cols_display)
    styled_table = df_display.style.applymap(color_status, subset=["Local Status", "Global Status"])
    st.markdown(styled_table.to_html(escape=False), unsafe_allow_html=True)
