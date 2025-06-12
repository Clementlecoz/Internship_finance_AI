import pandas as pd
import streamlit as st
import os

# Reuse your dataset loading logic
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.normpath(os.path.join(current_dir, '..', 'dataset1_complet.csv'))
df = pd.read_csv(csv_path)
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





df["Local Alert Summary"] = df.apply(get_local_alerts, axis=1)
df["Global Alert Summary"] = df.apply(get_global_alerts, axis=1)
df["Local Status"] = df.apply(get_local_status, axis=1)

df["Overall Status"] = df.apply(get_status, axis=1)
df["Rev Growth"] = df["revenue_growth"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "")
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

# Add your existing transformations again (or modularize them)
# Copy-paste the relevant functions from your main script:
# - get_local_alerts, get_global_alerts, get_local_status, get_status, get_recommendation, style_status, color_local_status
# Then apply those transformations again:
df["Local Alert Summary"] = df.apply(get_local_alerts, axis=1)
df["Global Alert Summary"] = df.apply(get_global_alerts, axis=1)
df["Local Status"] = df.apply(get_local_status, axis=1)
df["Overall Status"] = df.apply(get_status, axis=1)
df["Rev Growth"] = df["revenue_growth"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "")
df["Recommendation"] = df.apply(get_recommendation, axis=1)
df["Status Display"] = df["Overall Status"].apply(style_status)

# UI
st.title("🗓️ Company Overview by Quarter")

# Dropdown for quarter selection
unique_quarters = sorted(df["quarter"].unique())
selected_quarter = st.selectbox("Select a quarter:", unique_quarters)

# Filter and show data
df_quarter = df[df["quarter"] == selected_quarter]

cols_quarter = {
    "company": "Company",
    "score_profitability_local": "Profitability (Local)",
    "score_profitabilty_global": "Profitability (Global)",
    "score_liquidity_local": "Liquidity (Local)",
    "score_liquidity_global": "Liquidity (Global)",
    "score_solvency_local": "Solvency (Local)",
    "score_solvency_global": "Solvency (Global)",
    "score_leverage_adjusted_local": "Adj. Leverage (Local)",
    "score_leverage_adjusted_global": "Adj. Leverage (Global)",
    "Rev Growth": "Rev Growth",
    "Status Display": "Status Display",
    "Local Status": "Local Status",
    "Recommendation": "Recommendation"
}

styled_quarter = df_quarter[list(cols_quarter.keys())].rename(columns=cols_quarter).style.applymap(
    color_local_status, subset=["Local Status"]
)

st.markdown(styled_quarter.to_html(escape=False), unsafe_allow_html=True)
