import streamlit as st
from PIL import Image


st.set_page_config(page_title="Company Financial Health Dashboard", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(145deg, #0f1c2e, #1a2a45, #10253f);
        background-attachment: fixed;
        color: white;
    }
    .main-container {
        background-color: rgba(255, 255, 255, 0.07);
        padding: 2rem;
        border-radius: 12px;
        max-width: 1000px;
        margin: auto;
    }
    h1 {
        color: #00c3ff;
        text-align: center;
        font-size: 2.8rem;
    }
    h3 {
        color: #a0d1ff;
        font-size: 1.4rem;
        margin-top: 2rem;
    }
    ul {
        font-size: 1.05rem;
        line-height: 1.6rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


logo = Image.open("Copilot_20250623_064402.png")
st.image(logo, width=120)



with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("# Company Financial Health Dashboard")

    st.markdown("### Project Overview")
    st.write(
        "This dashboard provides a comprehensive view of company financial health, "
        "including scoring, trend analysis, and anomaly detection."
    )

    st.markdown("### Scope of Analysis")
    st.write(
        "This analysis focuses on five major international banks from both American and European markets:\n"
        "- **JPMorgan Chase** (🇺🇸 United States)\n"
        "- **BNP Paribas** (🇫🇷 France)\n"
        "- **Crédit Agricole** (🇫🇷 France)\n"
        "- **HSBC** (🇬🇧 United Kingdom)\n"
        "- **Banco Santander** (🇪🇸 Spain)\n\n"
        "These institutions were selected to ensure a diversified view across regions and financial models, "
        "providing meaningful comparisons in terms of profitability, risk exposure, liquidity, and solvency. "
        "The data includes quarterly financial indicators from recent years, offering both local (company-specific) "
        "and global (market-relative) perspectives on their financial health."
    )



    st.markdown("### Navigation")
    st.markdown("""
    - **Expert View** - Access detailed financial indicators and quarterly analysis  
    - **Simplified View** - Designed for non-financial users with a focus on clarity  
    - **Score Explorer** - Visualize score evolution and compare between companies  
    - **Methodology** - Learn how scores are calculated from key financial indicators  
    """)

    st.markdown("### What You Can Do")
    st.markdown("""
    - Identify strong or weak financial signals  
    - Spot companies at risk using key ratios and composite scores  
    - Understand the scoring logic behind each health dimension  
    """)

    st.info("Use the sidebar on the left to navigate between pages.")

    st.markdown("</div>", unsafe_allow_html=True)
