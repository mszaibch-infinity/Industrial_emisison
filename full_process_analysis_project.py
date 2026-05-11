"""
=========================================================
PROJECT 1 — INDUSTRIAL EMISSIONS ANALYSIS ENGINE
=========================================================

Purpose:
- Simulate industrial emissions monitoring data
- Perform compliance analysis
- Calculate KPIs automatically
- Generate reusable datasets
- Export files for Streamlit dashboards

Outputs:
- emissions_data.csv
- compliance_summary.csv
- monthly_summary.csv
- correlation_matrix.csv
- kpis.csv

Run:
    python analysis.py
"""

# =========================================================
# 1. IMPORT LIBRARIES
# =========================================================

import pandas as pd
import numpy as np
from pathlib import Path

# Make random data reproducible
np.random.seed(42)

# =========================================================
# 2. CREATE OUTPUT FOLDER
# =========================================================

# Creates folder automatically if missing
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

# =========================================================
# 3. GENERATE SIMULATED DATA
# =========================================================

# Number of daily records
days = 270

# Create date range
dates = pd.date_range(
    start="2024-01-01",
    periods=days,
    freq="D"
)

# ---------------------------------------------------------
# Production rate (%)
# Seasonal trend + random noise
# ---------------------------------------------------------

prod_rate = (
    70
    + 15 * np.sin(np.linspace(0, 2 * np.pi, days))
    + np.random.normal(0, 5, days)
)

# Keep values realistic
prod_rate = np.clip(prod_rate, 55, 100)

# ---------------------------------------------------------
# Process temperature
# Correlated with production rate
# ---------------------------------------------------------

temperature = (
    800
    + 0.8 * (prod_rate - 70)
    + np.random.normal(0, 8, days)
)

# ---------------------------------------------------------
# PM emissions
# Correlated with production
# ---------------------------------------------------------

pm = (
    0.22 * prod_rate
    + np.random.normal(0, 3, days)
)

# Add exceedance spike events
spike_days = [
    42, 43,
    88, 89, 90,
    130, 131,
    180, 181, 182, 183,
    220, 221,
    255
]

pm[spike_days] += np.random.uniform(8, 16, len(spike_days))

pm = np.clip(pm, 2, 40)

# ---------------------------------------------------------
# NOx emissions
# Correlated with temperature
# ---------------------------------------------------------

nox = (
    200
    + 1.5 * (temperature - 800)
    + np.random.normal(0, 25, days)
)

nox = np.clip(nox, 150, 420)

# ---------------------------------------------------------
# SO2 emissions
# Weakly correlated with production
# ---------------------------------------------------------

so2 = (
    100
    + 0.5 * (prod_rate - 70)
    + np.random.normal(0, 18, days)
)

so2 = np.clip(so2, 50, 210)

# ---------------------------------------------------------
# CO emissions
# Mostly stable with anomaly period
# ---------------------------------------------------------

co = 300 + np.random.normal(0, 40, days)

# Add anomaly window
co[120:160] += 120

co = np.clip(co, 100, 750)

# =========================================================
# 4. CREATE MAIN DATAFRAME
# =========================================================

df = pd.DataFrame({

    "date": dates,

    "production_rate_pct": prod_rate.round(1),

    "temperature_C": temperature.round(1),

    "PM_mg_Nm3": pm.round(1),

    "NOx_mg_Nm3": nox.round(1),

    "SO2_mg_Nm3": so2.round(1),

    "CO_mg_Nm3": co.round(1),

})

# =========================================================
# 5. COMPLIANCE LIMITS
# =========================================================

LIMITS = {

    "PM_mg_Nm3": 20,

    "NOx_mg_Nm3": 400,

    "SO2_mg_Nm3": 200,

    "CO_mg_Nm3": 500,

}

# =========================================================
# 6. CREATE EXCEEDANCE FLAGS
# =========================================================

# Creates True/False columns
# Useful later for KPIs and dashboards

for param, limit in LIMITS.items():

    flag_name = param.replace("_mg_Nm3", "") + "_exceed"

    df[flag_name] = df[param] > limit

# =========================================================
# 7. COMPLIANCE ANALYSIS
# =========================================================

summary_rows = []

for param, limit in LIMITS.items():

    col = df[param]

    # Count exceedances
    exceedances = (col > limit).sum()

    # Compliance %
    compliance_rate = round(
        (1 - exceedances / len(col)) * 100,
        1
    )

    # Determine trend
    first_half = col.iloc[:len(col)//2].mean()
    second_half = col.iloc[len(col)//2:].mean()

    if second_half > first_half + 2:
        trend = "Increasing"

    elif second_half < first_half - 2:
        trend = "Decreasing"

    else:
        trend = "Stable"

    # Determine status
    if exceedances == 0:
        status = "Compliant"

    elif exceedances < 10:
        status = "Action required"

    else:
        status = "Critical"

    # Store row
    summary_rows.append({

        "parameter": param.replace("_mg_Nm3", ""),

        "limit": limit,

        "mean_value": round(col.mean(), 1),

        "peak_value": round(col.max(), 1),

        "exceedances": exceedances,

        "compliance_percent": compliance_rate,

        "trend": trend,

        "status": status,

    })

# Create summary dataframe
summary_df = pd.DataFrame(summary_rows)

# =========================================================
# 8. CORRELATION ANALYSIS
# =========================================================

corr_cols = [

    "production_rate_pct",

    "temperature_C",

    "PM_mg_Nm3",

    "NOx_mg_Nm3",

    "SO2_mg_Nm3",

    "CO_mg_Nm3",

]

corr_df = df[corr_cols].corr().round(2)

# =========================================================
# 9. MONTHLY SUMMARY
# =========================================================

# Create month column
df["month"] = df["date"].dt.to_period("M")

# Group monthly statistics
monthly_df = df.groupby("month").agg(

    production_mean=("production_rate_pct", "mean"),

    PM_mean=("PM_mg_Nm3", "mean"),

    NOx_mean=("NOx_mg_Nm3", "mean"),

    SO2_mean=("SO2_mg_Nm3", "mean"),

    CO_mean=("CO_mg_Nm3", "mean"),

    PM_exceedances=("PM_exceed", "sum"),

    CO_exceedances=("CO_exceed", "sum"),

).round(1)

# Convert month back to string
monthly_df = monthly_df.reset_index()

monthly_df["month"] = monthly_df["month"].astype(str)

# =========================================================
# 10. KPI CALCULATIONS
# =========================================================

# Total exceedances
total_exceedances = (
    df["PM_exceed"].sum()
    + df["CO_exceed"].sum()
)

# Compliance rate
total_checks = len(df) * len(LIMITS)

total_failed = 0

for param, limit in LIMITS.items():
    total_failed += (df[param] > limit).sum()

overall_compliance = round(
    (1 - total_failed / total_checks) * 100,
    1
)

# Simulated improvement KPI
pre_action_rate = round(
    overall_compliance - np.random.uniform(10, 18),
    1
)

# KPI dictionary
kpis = {

    "parameters_tracked": len(LIMITS),

    "total_exceedance_events": int(total_exceedances),

    "overall_compliance_percent": overall_compliance,

    "pre_action_compliance_percent": pre_action_rate,

    "production_lines": 2,

    "monitoring_days": days,

}

# Convert KPI dictionary to dataframe
kpi_df = pd.DataFrame(

    list(kpis.items()),

    columns=["kpi", "value"]

)

# =========================================================
# 11. EXPORT FILES
# =========================================================

# Main dataset
df.to_csv(

    output_dir / "emissions_data.csv",

    index=False

)

# Compliance summary
summary_df.to_csv(

    output_dir / "compliance_summary.csv",

    index=False

)

# Monthly summary
monthly_df.to_csv(

    output_dir / "monthly_summary.csv",

    index=False

)

# Correlation matrix
corr_df.to_csv(

    output_dir / "correlation_matrix.csv"

)

# KPI dataset
kpi_df.to_csv(

    output_dir / "kpis.csv",

    index=False

)

# =========================================================
# 12. CONSOLE OUTPUT
# =========================================================

print("\n" + "=" * 60)
print("INDUSTRIAL EMISSIONS ANALYSIS COMPLETE")
print("=" * 60)

print("\nFILES EXPORTED:")

print("- emissions_data.csv")
print("- compliance_summary.csv")
print("- monthly_summary.csv")
print("- correlation_matrix.csv")
print("- kpis.csv")

print("\nOUTPUT FOLDER:")
print(output_dir.resolve())

print("\nOVERALL KPI SUMMARY")

for key, value in kpis.items():

    print(f"{key}: {value}")

print("\n" + "=" * 60)
