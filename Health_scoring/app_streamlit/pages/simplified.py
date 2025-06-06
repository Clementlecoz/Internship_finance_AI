import pandas as pd
import streamlit as st

import os
import pandas as pd

# Get the absolute path of the current script (your .py file)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct absolute path to dataset relative to the script location
csv_path = os.path.normpath(os.path.join(current_dir, '..', 'dataset1_complet.csv'))

# Load the dataset
df = pd.read_csv(csv_path)

# Optional: print the path to confirm
print(f"Loading dataset from: {csv_path}")

#df = pd.read_csv("../dataset1_complet.csv")
df = df.sort_values(["company", "quarter"])


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
        global_ = row.get(f"score_{score}_global") if score != "profitability" else row.get("score_profitabilty_global")
        if pd.notna(global_):
            if global_ > 0.8:
                alerts.append(f"High {score.title()}")
            elif global_ < 0.2:
                alerts.append(f"Low {score.title()}")
    return ", ".join(alerts)



thresholds = {
    "score_profitability": {"low": 0.2, "high": 0.8},
    "score_liquidity": {"low": 0.2, "high": 0.8},
    "score_solvency": {"low": 0.2, "high": 0.8},
    "score_leverage_adjusted": {"low": 0.2, "high": 0.8},
    "revenue_growth": {"drop": -0.1, "boost": 0.1}
}

def get_local_status(row):
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



def get_status(row):
    local_low = set()
    global_low = set()
    local_high = set()
    global_high = set()

    for score in ["profitability", "liquidity", "solvency", "leverage_adjusted"]:
        local = row.get(f"score_{score}_local")
        global_ = row.get(f"score_{score}_global") if score != "profitability" else row.get("score_profitabilty_global")

        if pd.notna(local):
            if local < 0.2:
                local_low.add(score)
            elif local > 0.8:
                local_high.add(score)

        if pd.notna(global_):
            if global_ < 0.2:
                global_low.add(score)
            elif global_ > 0.8:
                global_high.add(score)

    
    common_low = local_low & global_low
    common_high = local_high & global_high

    if len(common_low) >= 2:
        return "Structural Risk"
    elif "solvency" in common_low:
        if "leverage_adjusted" in global_high or "leverage_adjusted" in local_high:
            return "Mixed Risk"
    elif len(local_low) >= 2 and len(global_low) == 0:
        return "Local Weakness"
    elif len(common_high) >= 2:
        return "Strong Performer"
    elif len(global_high) >= 2:
        return "Global Improvement"
    elif len(global_low) >= 2:
        return "Global Risk"
    return "Neutral"
def get_recommendation(row):
    local_low = set()
    global_low = set()
    local_high = set()
    global_high = set()

    for score in ["profitability", "liquidity", "solvency", "leverage_adjusted"]:
        local = row.get(f"score_{score}_local")
        global_ = row.get(f"score_{score}_global") if score != "profitability" else row.get("score_profitabilty_global")

        if pd.notna(local) and local < 0.2:
            local_low.add(score)
        if pd.notna(global_) and global_ < 0.2:
            global_low.add(score)
        if pd.notna(local) and local > 0.8:
            local_high.add(score)
        if pd.notna(global_) and global_ > 0.8:
            global_high.add(score)

    common_low = local_low & global_low
    common_high = local_high & global_high

    phrases = []

    if common_low:
        phrases.append(f"Weak both locally and globally: {', '.join(common_low).title()}")
    if local_low - global_low:
        phrases.append(f"Internal weakness (local only): {', '.join(local_low - global_low).title()}")
    if global_low - local_low:
        phrases.append(f"Global peer underperformance: {', '.join(global_low - local_low).title()}")

    if common_high:
        phrases.append(f"Strong performance in: {', '.join(common_high).title()}")

    if not phrases:
        return "No specific concern or strength detected."
    
    return ". ".join(phrases) + "."


def style_status(status):
    if status == "Strong Performer":
        return "🟢 Strong Performer"
    elif status == "Global Improvement":
        return "🟢 Global Improvement"
    elif status == "Mixed Risk":
        return "🟡 Mixed Risk"
    elif status == "Local Weakness":
        return "🟠 Local Weakness"
    elif status == "Global Risk":
        return "🔴 Global Risk"
    elif status == "Structural Risk":
        return "🔴 Structural Risk"
    else:
        return "⚪ Neutral"


def to_percentage(score):
    return f"{score * 100:.0f}%" if pd.notna(score) else ""



df["Local Alert Summary"] = df.apply(get_local_alerts, axis=1)
df["Global Alert Summary"] = df.apply(get_global_alerts, axis=1)
df["Local Status"] = df.apply(get_local_status, axis=1)

df["Overall Status"] = df.apply(get_status, axis=1)
df["Rev Growth"] = df["revenue_growth"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "")
df["Profitability (Local %)"] = df["score_profitability_local"].apply(to_percentage)
df["Profitability (Global %)"] = df["score_profitabilty_global"].apply(to_percentage)
df["Liquidity (Local %)"] = df["score_liquidity_local"].apply(to_percentage)
df["Liquidity (Global %)"] = df["score_liquidity_global"].apply(to_percentage)
df["Solvency (Local %)"] = df["score_solvency_local"].apply(to_percentage)
df["Solvency (Global %)"] = df["score_solvency_global"].apply(to_percentage)
df["Adj. Leverage (Local %)"] = df["score_leverage_adjusted_local"].apply(to_percentage)
df["Adj. Leverage (Global %)"] = df["score_leverage_adjusted_global"].apply(to_percentage)

df["Recommendation"] = df.apply(get_recommendation, axis=1)
df["Status Display"] = df["Overall Status"].apply(style_status)

def color_local_status(val):
    color = ""
    if val == "Strong":
        color = "background-color: #b6fcb6"  
    elif val == "Danger":
        color = "background-color: #ffd3d3"  
    elif val == "Critical Risk":
        color = "background-color: #ff9999"  
    elif val == "Stable":
        color = "background-color: #f7f7f7"  
    elif val == "Good signal":
        color = "background-color: #d1e7dd"  
    elif val == "Caution":
        color = "background-color: #fff3cd"  
    elif val == "Mixed Risk":
        color = "background-color: #ffe6cc"  
    elif val == "Leveraged Risk":
        color = "background-color: #f0c2c2" 
    return color


# streamlit
st.title("📊 Company Financial Score Dashboard")

# Menu déroulant
company = st.selectbox("Select a company:", sorted(df["company"].unique()))

# filter by comapny
df_company = df[df["company"] == company]





# Plain language mapping
def get_friendly_status(val):
    if val in ["Excellent Health", "Strong", "Good signal"]:
        return "🟢 Healthy"
    elif val in ["Caution", "Mixed Risk", "Stable", "Watch"]:
        return " stable"
    elif val in ["Danger", "Critical Risk", "Leveraged Risk"]:
        return "🔴 At Risk"
    else:
        return "Unknown"

df_company["Overall Health"] = df_company["Local Status"].apply(get_friendly_status)

# Emoji revenue trend
def revenue_trend(row):
    if pd.isna(row["revenue_growth"]):
        return "N/A"
    elif row["revenue_growth"] > 0.1:
        return "📈 +{:.1f}%".format(row["revenue_growth"] * 100)
    elif row["revenue_growth"] < -0.1:
        return "📉 {:.1f}%".format(row["revenue_growth"] * 100)
    else:
        return "{:.1f}%".format(row["revenue_growth"] * 100)

df_company["Revenue Trend"] = df_company.apply(revenue_trend, axis=1)

# Simple table
simple_cols = ["quarter", "Overall Health", "Revenue Trend", "Local Alert Summary", "Global Alert Summary","Recommendation"]
simple_df = df_company[simple_cols].rename(columns={
    "quarter": "Quarter",
    "Overall Health": "Health",
    "Revenue Trend": " Revenue",
    "Local Alert Summary": " Local Key Alerts",
    "Global Alert Summary": " Global Key Alerts",
    "Recommendation": "Summary"
})

# Summary cards
st.subheader(" Quick Summary")
healthy_count = df_company["Overall Health"].eq("🟢 Healthy").sum()
at_risk_count = df_company["Overall Health"].eq("🔴 At Risk").sum()
avg_growth = df_company["revenue_growth"].mean()

col1, col2 = st.columns(2)
col1.metric("🟢 Healthy Quarters", healthy_count)
col2.metric("🔴 At Risk Quarters", at_risk_count)


# Render table
st.subheader(" Simple Overview Table")
st.dataframe(simple_df, hide_index=True)
