import pandas as pd
import streamlit as st
import os

# --- Load dataset ---
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.normpath(os.path.join(current_dir, '..', 'dataset1_complet.csv'))
df = pd.read_csv(csv_path)
df = df.sort_values(["company", "quarter"])

# --- Functions needed to calculate Overall Status ---
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
    elif "solvency" in common_low and ("leverage_adjusted" in global_high or "leverage_adjusted" in local_high):
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

def color_overall_status(val):
    if "Strong" in val:
        return "background-color: #b6fcb6"
    elif "Improvement" in val:
        return "background-color: #d0f0c0"
    elif "Risk" in val:
        return "background-color: #ff9999"
    elif "Weakness" in val:
        return "background-color: #ffe6cc"
    elif "Mixed" in val:
        return "background-color: #fff3cd"
    elif "Neutral" in val:
        return "background-color: #f7f7f7"
    return ""

# --- Also get alerts and recommendation ---
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

# --- Add required columns ---
df["Overall Status"] = df.apply(get_status, axis=1)
df["Status Display"] = df["Overall Status"].apply(style_status)
df["Local Alert Summary"] = df.apply(get_local_alerts, axis=1)
df["Global Alert Summary"] = df.apply(get_global_alerts, axis=1)
df["Recommendation"] = df.apply(get_recommendation, axis=1)

# --- Streamlit UI ---
st.title("🧭 Simplified Financial Health View")

company = st.selectbox("Select a company:", sorted(df["company"].unique()))
df_company = df[df["company"] == company]

# --- Summary counts ---
risk_count = df_company["Overall Status"].isin([
    "Global Risk", "Structural Risk", "Mixed Risk", "Local Weakness"
]).sum()

strong_count = df_company["Overall Status"].isin([
    "Strong Performer", "Global Improvement"
]).sum()

st.subheader(f"🔍 Summary for {company}")
st.markdown(f"""
- **🛑 Quarters at Risk:** {risk_count}
- **✅ Strong Quarters:** {strong_count}
""")

# --- Display simplified table ---
cols_display = {
    "quarter": "Quarter",
    "Status Display": "Overall Status",
    "Local Alert Summary": "Local Alerts",
    "Global Alert Summary": "Global Alerts",
    "Recommendation": "Recommendation"
}
df_display = df_company[list(cols_display.keys())].rename(columns=cols_display)
styled_table = df_display.style.applymap(color_overall_status, subset=["Overall Status"])

st.markdown("### 🗂️ Quarter-by-Quarter Summary")
st.markdown(styled_table.to_html(escape=False), unsafe_allow_html=True)

with st.expander("ℹ️ About this view"):
    st.markdown("""
    This simplified view avoids technical scores and highlights:
    - Key alerts per quarter,
    - High-level health status,
    - Practical recommendations.
    """)
