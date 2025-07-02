import streamlit as st
from PIL import Image
import os

def show_methodology_page():
    st.title("Methodology – How Are the Financial Scores Built?")

    st.markdown("""
    This dashboard provides a financial health overview using composite scores derived from key financial indicators.  
    Each score targets a specific financial dimension -> helping simplify complex financial data into interpretable signals.
    
    ### Step 1: Key Indicators Used

    The dataset includes core financial ratios frequently used in company analysis:

    | Indicator | Meaning |
    |----------|---------|
    | `ROA_pct` | Return on Assets – profitability from assets |
    | `ROE_pct` | Return on Equity – profitability from shareholder capital |
    | `net_margin_pct` | Net profit margin – earnings after all expenses |
    | `current_ratio_pct` | Short-term assets vs. liabilities |
    | `cash_ratio_pct` | Cash reserves vs. liabilities |
    | `debt_to_equity_pct` | Financial leverage – debt vs. shareholder equity |
    | `revenue_growth_pct` | Revenue trend over time |

    These are the building blocks for the scores below.

    ---
    """)
    st.write("---")
    st.subheader(" How Are Scores Normalized?")

    st.markdown("""
    To make indicators comparable, we apply percentile normalization:

    - Each company’s indicator is converted into a value between 0 and 1
    - This value represents the percentile rank of that company

    What it means:
    - A normalized score of 0.90 means the company outperforms 90% of peers
    - In other words, it ranks in the top 10%
    - A score near 0.50 places it around the median

    Comparison Basis:
    - Local Score: compared to all companies in the entire dataset
    - Global Score: compared to companies in the same sector

    This ensures fairness across variables with different scales or units, and highlights relative performance.
    """)

    
    st.subheader(" Step 2: Correlation Matrix – Selecting the Right Combinations")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.normpath(os.path.join(current_dir, '..', 'img', 'correlation_matrix.png'))
    image = Image.open(image_path)
    st.image(image, caption='Correlation Matrix of Key Indicators', use_container_width=True)

    st.markdown("""
    This matrix shows how strongly each indicator correlates with the others:
    - Values close to +1 → strong positive correlation
    - Values close to -1 → strong negative correlation
    - Values near 0 → little to no correlation

    Indicator Selection Strategy

    To build independent scores:
    - We grouped highly correlated variables together to avoid redundancy
    - We kept at least one distinct variable per score

    Example:
    - ROE and debt_to_equity show a strong negative correlation.  
      → We combine them to create a leverage-adjusted profitability score, detecting when ROE is inflated by debt.

    ---
    """)

    with st.expander(" 1. Profitability Score"):
        st.markdown("""
        What it measures:  
        How well the company generates profit from its operations.

        Indicators used:
        - ROA (Return on Assets)
        - ROE (Return on Equity)
        - net_margin (Net Margin)

        Formula:
        ```python
        score_profitability_local = mean([ROA_pct, ROE_pct, net_margin_pct])
        ```

        These indicators reflect internal earnings efficiency from different perspectives.

        Correlation Insight:  
        These indicators are positively correlated — confirming they collectively measure profitability strength.
        """)

    with st.expander(" 2. Liquidity Score"):
        st.markdown("""
        What it measures:  
        The ability to cover short-term obligations with liquid assets.

        Indicators used:
        - current_ratio
        - cash_ratio

        Formula:
        ```python
        score_liquidity_local = mean([current_ratio_pct, cash_ratio_pct])
        ```

        Correlation Insight:  
        High correlation between both ratios shows a reliable short-term liquidity profile.
        """)

    with st.expander(" 3. Solvency Score"):
        st.markdown("""
        What it measures:  
        Long-term financial safety by evaluating debt levels.

        Indicator used:
        - debt_to_equity

        Formula:
        ```python
        score_solvency_local = 1 - debt_to_equity_pct
        ```

        Lower debt-to-equity ratio = higher solvency.

        Correlation Insight:  
        This metric shows expected negative correlation with performance scores, isolating long-term risk.
        """)

    with st.expander(" 4. Leverage-Adjusted Profitability"):
        st.markdown("""
        What it measures:  
        Profitability adjusted for the risk taken (debt level).

        Indicators used:
        - ROE
        - 1 - debt_to_equity (inverted to reflect "low debt")

        Formula:
        ```python
        score_leverage_adjusted_local = mean([ROE_pct, 1 - debt_to_equity_pct])
        ```

        Correlation Insight:  
        This helps detect companies with high ROE that might be artificially boosted by high leverage.
        """)

    with st.expander(" Revenue Growth (Used for Alerts)"):
        st.markdown("""
        Not part of core scores, but used for alert signals.

        - Above +10% → Growth Boost
        - Below -10% → Drop Warning

        Helps signal positive or negative business momentum.
        """)

    with st.expander(" Why These Combinations?"):
        st.markdown("""
        Using a correlation matrix, we ensured that:
        - Each score combines complementary but distinct indicators
        - Redundant or overly correlated metrics are avoided across scores
        - Each score reflects a specific dimension of financial health:
            - Profitability: performance
            - Liquidity: short-term safety
            - Solvency: long-term sustainability
            - Leverage-adjusted: profitability relative to debt

        Together, these form a balanced and interpretable view of company health.
        """)


show_methodology_page()
