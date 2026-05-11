"""
=========================================================
STREAMLIT DASHBOARD
Industrial Emissions Compliance Analysis
=========================================================

Run:
    streamlit run dashboard.py

Reads exported files from:
    /output

Purpose:
- Display KPI cards
- Show compliance charts
- Show correlation matrix
- Show summary tables

Simple beginner-friendly dashboard
"""

# =========================================================
# 1. IMPORT LIBRARIES
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# =========================================================
# 2. PAGE CONFIG
# =========================================================

st.set_page_config(

    page_title="Industrial Emissions Dashboard",

    layout="wide"

)

# =========================================================
# 3. LOAD DATA
# =========================================================

df = pd.read_csv("output/emissions_data.csv")

summary_df = pd.read_csv("output/compliance_summary.csv")

monthly_df = pd.read_csv("output/monthly_summary.csv")

corr_df = pd.read_csv("output/correlation_matrix.csv", index_col=0)

kpi_df = pd.read_csv("output/kpis.csv")

# =========================================================
# 4. CONVERT KPI TABLE TO DICTIONARY
# =========================================================

kpis = dict(zip(kpi_df["kpi"], kpi_df["value"]))

# =========================================================
# 5. DASHBOARD HEADER
# =========================================================

st.title("Industrial Emissions Compliance Analysis")

st.markdown("""
Continuous emissions monitoring analysis across
multiple industrial process parameters.

Dataset is simulated for portfolio demonstration.
""")

# =========================================================
# 6. KPI CARDS
# =========================================================

st.subheader("Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

# ✅ CREATE STYLED KPI CARDS WITH FIXED HEIGHT & FLEXIBLE LAYOUT
# Key improvements:
# - height: 120px keeps all cards uniform (prevents size differences)
# - white-space: nowrap prevents metric name from wrapping
# - Flexbox (flex-direction, justify-content) centers content vertically
# - Color-coded cards for visual distinction
# - font-size increased: heading 12px -> value 32px for better visibility

kpi_data = [
    ("Parameters", int(kpis["parameters_tracked"]), "#3498db"),
    ("Exceedance Events", int(kpis["total_exceedance_events"]), "#e74c3c"),
    ("Compliance Rate", f'{kpis["overall_compliance_percent"]}%', "#27ae60"),
    ("Pre-action Rate", f'{kpis["pre_action_compliance_percent"]}%', "#f39c12"),
    ("Production Lines", int(kpis["production_lines"]), "#9b59b6"),
]

cols = [col1, col2, col3, col4, col5]

for i, (metric, value, color) in enumerate(kpi_data):
    # Convert hex color to rgba for semi-transparent background
    bg = f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1)"

    card_html = f"""
    <div style="
        background-color: {bg};
        border-left: 5px solid {color};
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    ">
        <p style="
            margin: 0;
            font-size: 12px;
            color: {color};
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
            white-space: nowrap;
        ">
            {metric}
        </p>
        <p style="margin: 8px 0 0 0; font-size: 32px; font-weight: bold; color: {color};">
            {value}
        </p>
    </div>
    """

    with cols[i]:
        st.markdown(card_html, unsafe_allow_html=True)

# =========================================================
# 7. PROJECT SUMMARY
# =========================================================

st.info("""

This project simulates industrial emissions monitoring
across a nine-month operating period.

Analysis includes:
- Compliance monitoring
- Exceedance detection
- Correlation analysis
- Monthly trend analysis
- Process anomaly identification

""")

# =========================================================
# 8. PM TIME SERIES CHART
# =========================================================

st.subheader("PM Emissions vs Compliance Limit")

fig, ax = plt.subplots(figsize=(12, 4))

# PM line
ax.plot(

    df["date"],

    df["PM_mg_Nm3"],

    label="PM",

    linewidth=1.5

)

# Compliance limit
ax.axhline(

    y=20,

    linestyle="--",

    linewidth=1,

    label="Compliance Limit"

)

# Chart labels
ax.set_ylabel("PM (mg/Nm3)")

ax.legend()

st.pyplot(fig)

# =========================================================
# 9. NOx + CO CHARTS
# =========================================================

col1, col2 = st.columns(2)

# ---------------------------------------------------------
# NOx Monthly Trend
# ---------------------------------------------------------

with col1:

    st.subheader("NOx Monthly Trend")

    fig, ax = plt.subplots(figsize=(6, 4))

    ax.plot(

        monthly_df["month"],

        monthly_df["NOx_mean"],

        marker="o"

    )

    ax.axhline(

        y=400,

        linestyle="--",

        linewidth=1

    )

    ax.set_ylabel("NOx")

    plt.xticks(rotation=45)

    st.pyplot(fig)

# ---------------------------------------------------------
# CO Monthly Trend
# ---------------------------------------------------------

with col2:

    st.subheader("CO Monthly Trend")

    fig, ax = plt.subplots(figsize=(6, 4))

    ax.plot(

        monthly_df["month"],

        monthly_df["CO_mean"],

        marker="o"

    )

    ax.axhline(

        y=500,

        linestyle="--",

        linewidth=1

    )

    ax.set_ylabel("CO")

    plt.xticks(rotation=45)

    st.pyplot(fig)

# =========================================================
# 10. SCATTER PLOT
# =========================================================

st.subheader("Production Rate vs PM Emissions")

fig, ax = plt.subplots(figsize=(7, 5))

# Normal points
normal = df["PM_mg_Nm3"] <= 20

ax.scatter(

    df.loc[normal, "production_rate_pct"],

    df.loc[normal, "PM_mg_Nm3"],

    alpha=0.6,

    label="Within Limit"

)

# Exceedance points
exceed = df["PM_mg_Nm3"] > 20

ax.scatter(

    df.loc[exceed, "production_rate_pct"],

    df.loc[exceed, "PM_mg_Nm3"],

    alpha=0.8,

    label="Exceedance"

)

# Compliance line
ax.axhline(

    y=20,

    linestyle="--",

    linewidth=1

)

ax.set_xlabel("Production Rate (%)")

ax.set_ylabel("PM (mg/Nm3)")

ax.legend()

st.pyplot(fig)

# =========================================================
# 11. CORRELATION MATRIX
# =========================================================

st.subheader("Correlation Matrix")

st.dataframe(

    corr_df,

    use_container_width=True

)

# =========================================================
# 12. COMPLIANCE SUMMARY TABLE
# =========================================================

st.subheader("Compliance Summary")

st.dataframe(

    summary_df,

    use_container_width=True

)

# =========================================================
# 13. MONTHLY SUMMARY TABLE
# =========================================================

st.subheader("Monthly Summary")

st.dataframe(

    monthly_df,

    use_container_width=True

)

# =========================================================
# 14. ANALYTICAL INSIGHT
# =========================================================

st.warning("""

Key finding:

CO exceedances did not strongly correlate with
production rate increases.

This suggests the anomaly may be linked to
combustion efficiency or monitoring system issues
rather than production load alone.

""")

# =========================================================
# 15. FOOTER
# =========================================================

st.caption("""

Simulated industrial dataset for analytics portfolio
demonstration.

Python + pandas + Streamlit

""")
