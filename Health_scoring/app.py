import pandas as pd
import streamlit as st

# Charger le fichier
df = pd.read_csv("dataset1_complet.csv")
df = df.sort_values(["company", "quarter"])

# Fonctions
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
        if row["revenue_growth"] > 0.01:
            alerts.append("Rev ↑")
        elif row["revenue_growth"] < -0.01:
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

    # Intersections entre local et global
    common_low = local_low & global_low
    common_high = local_high & global_high

    # Règles conditionnelles améliorées
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




# Ajouter colonnes Alert Summary et Status
df["Local Alert Summary"] = df.apply(get_local_alerts, axis=1)
df["Global Alert Summary"] = df.apply(get_global_alerts, axis=1)

df["Overall Status"] = df.apply(get_status, axis=1)
df["Rev Growth"] = df["revenue_growth"].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "")
df["Recommendation"] = df.apply(get_recommendation, axis=1)
df["Status Display"] = df["Overall Status"].apply(style_status)
# Interface Streamlit
st.title("📊 Company Financial Score Dashboard")

# Menu déroulant
company = st.selectbox("Select a company:", sorted(df["company"].unique()))

# Filtrer
df_company = df[df["company"] == company]

# Colonnes à afficher
cols = {
    "score_profitability_local": "Profitability (Local)",
    "score_profitabilty_global": "Profitability (Global)",
    "score_liquidity_local": "Liquidity (Local)",
    "score_liquidity_global": "Liquidity (Global)",
    "score_solvency_local": "Solvency (Local)",
    "score_solvency_global": "Solvency (Global)",
    "score_leverage_adjusted_local": "Adj. Leverage (Local)",
    "score_leverage_adjusted_global": "Adj. Leverage (Global)",
    "Rev Growth": "Rev Growth",
    "Local Alert Summary": "Local Alerts",
    "Global Alert Summary": "Global Alerts",
    "Status Display": "Status Display"
}

# Affichage
st.subheader(f"📈 Results for {company}")
st.dataframe(df_company[["quarter"] + list(cols.keys())].rename(columns=cols), use_container_width=True)
