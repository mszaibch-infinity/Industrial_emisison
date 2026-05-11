"""
PROJECT 1 — Industrial Emissions Compliance Analysis
Run:
    python p1_analysis.py

Outputs:
- Console summary tables
- Saved chart PNG
"""

# =========================================================
# 1. IMPORT LIBRARIES
# =========================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# Make random data reproducible
np.random.seed(42)

# =========================================================
# 2. DATA CREATION
# =========================================================

# Create date range
days = 270
dates = pd.date_range(start="2024-01-01", periods=days, freq="D")

# Production rate (%)
# Seasonal wave + random noise
prod_rate = (
    70
    + 15 * np.sin(np.linspace(0, 2 * np.pi, days))
    + np.random.normal(0, 5, days)
)

# Keep values within realistic range
prod_rate = np.clip(prod_rate, 55, 100)

# Temperature correlated with production
temperature = (
    800
    + 0.8 * (prod_rate - 70)
    + np.random.normal(0, 8, days)
)

# PM emissions correlated with production
pm = (
    0.22 * prod_rate
    + np.random.normal(0, 3, days)
)

# Add artificial spike events
spike_days = [42, 43, 88, 89, 90, 130, 131, 180, 181, 182, 183, 220, 221, 255]
pm[spike_days] += np.random.uniform(8, 16, len(spike_days))

# Limit PM values
pm = np.clip(pm, 2, 40)

# NOx correlated with temperature
nox = (
    200
    + 1.5 * (temperature - 800)
    + np.random.normal(0, 25, days)
)

nox = np.clip(nox, 150, 420)

# SO2 weakly correlated with production
so2 = (
    100
    + 0.5 * (prod_rate - 70)
    + np.random.normal(0, 18, days)
)

so2 = np.clip(so2, 50, 210)

# CO mostly random with anomaly period
co = 300 + np.random.normal(0, 40, days)

# Add anomaly window
co[120:160] += 120

co = np.clip(co, 100, 750)

# =========================================================
# 3. CREATE DATAFRAME
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
# 4. COMPLIANCE LIMITS
# =========================================================

LIMITS = {
    "PM_mg_Nm3": 20,
    "NOx_mg_Nm3": 400,
    "SO2_mg_Nm3": 200,
    "CO_mg_Nm3": 500,
}

# =========================================================
# 5. DATA ANALYSIS
# =========================================================

print("\n" + "=" * 60)
print("INDUSTRIAL EMISSIONS COMPLIANCE ANALYSIS")
print("=" * 60)

summary_rows = []

# Loop through each parameter and limit
for param, limit in LIMITS.items():

    col = df[param]

    # Count exceedances
    exceedances = (col > limit).sum()

    # Compliance percentage
    compliance_rate = round(
        (1 - exceedances / len(col)) * 100,
        1
    )

    # Status label
    if exceedances == 0:
        status = "OK"

    elif exceedances < 10:
        status = "ACTION"

    else:
        status = "CRITICAL"

    # Store summary row
    summary_rows.append({
        "Parameter": param.replace("_mg_Nm3", ""),
        "Limit": limit,
        "Mean": round(col.mean(), 1),
        "Peak": round(col.max(), 1),
        "Exceedances": exceedances,
        "Compliance %": compliance_rate,
        "Status": status,
    })

# Create summary table
summary = pd.DataFrame(summary_rows)

print("\nCOMPLIANCE SUMMARY")
print(summary.to_string(index=False))

# =========================================================
# 6. CORRELATION ANALYSIS
# =========================================================

corr_cols = [
    "production_rate_pct",
    "temperature_C",
    "PM_mg_Nm3",
    "NOx_mg_Nm3",
    "SO2_mg_Nm3",
    "CO_mg_Nm3",
]

corr_matrix = df[corr_cols].corr().round(2)

print("\nCORRELATION MATRIX")
print(corr_matrix.to_string())

# =========================================================
# 7. EXCEEDANCE FLAGS
# =========================================================

# Create True/False exceedance columns
df["PM_exceed"] = df["PM_mg_Nm3"] > LIMITS["PM_mg_Nm3"]
df["CO_exceed"] = df["CO_mg_Nm3"] > LIMITS["CO_mg_Nm3"]

# Create month column
df["month"] = df["date"].dt.to_period("M")

# =========================================================
# 8. MONTHLY SUMMARY
# =========================================================

monthly = df.groupby("month").agg(

    PM_mean=("PM_mg_Nm3", "mean"),
    CO_mean=("CO_mg_Nm3", "mean"),

    PM_exceedances=("PM_exceed", "sum"),
    CO_exceedances=("CO_exceed", "sum"),

    prod_mean=("production_rate_pct", "mean"),

).round(1)

print("\nMONTHLY SUMMARY")
print(monthly.to_string())

# =========================================================
# 9. DATA PLOTTING
# =========================================================

# Chart style
plt.style.use("seaborn-v0_8-whitegrid")

# Color palette
colors = {
    "pm": "#16a34a",
    "co": "#d97706",
    "limit": "#dc2626",
}

# Create figure
fig = plt.figure(figsize=(14, 10))

# Main title
fig.suptitle(
    "Industrial Emissions Compliance Analysis",
    fontsize=14,
    fontweight="bold"
)

# Create subplot grid
gs = GridSpec(2, 2, figure=fig)

# =========================================================
# 10. CHART A — PM TIME SERIES
# =========================================================

ax1 = fig.add_subplot(gs[0, :])

# PM line
ax1.plot(
    df["date"],
    df["PM_mg_Nm3"],
    color=colors["pm"],
    linewidth=1,
    label="PM"
)

# Compliance limit line
ax1.axhline(
    LIMITS["PM_mg_Nm3"],
    color=colors["limit"],
    linestyle="--",
    label="Limit"
)

# Highlight exceedance area
ax1.fill_between(
    df["date"],
    df["PM_mg_Nm3"],
    LIMITS["PM_mg_Nm3"],
    where=(df["PM_mg_Nm3"] > LIMITS["PM_mg_Nm3"]),
    color=colors["limit"],
    alpha=0.2
)

ax1.set_title("PM Daily Values vs Compliance Limit")
ax1.set_ylabel("PM (mg/Nm3)")
ax1.legend()

# =========================================================
# 11. CHART B — CO ANOMALY
# =========================================================

ax2 = fig.add_subplot(gs[1, 0])

ax2.plot(
    df["date"],
    df["CO_mg_Nm3"],
    color=colors["co"],
    linewidth=1,
    label="CO"
)

ax2.axhline(
    LIMITS["CO_mg_Nm3"],
    color=colors["limit"],
    linestyle="--",
    label="Limit"
)

ax2.fill_between(
    df["date"],
    df["CO_mg_Nm3"],
    LIMITS["CO_mg_Nm3"],
    where=(df["CO_mg_Nm3"] > LIMITS["CO_mg_Nm3"]),
    color=colors["limit"],
    alpha=0.2
)

ax2.set_title("CO Anomaly Window")
ax2.set_ylabel("CO (mg/Nm3)")
ax2.legend()

# =========================================================
# 12. CHART C — PM VS PRODUCTION
# =========================================================

ax3 = fig.add_subplot(gs[1, 1])

# Exceedance mask
exceed_mask = df["PM_mg_Nm3"] > LIMITS["PM_mg_Nm3"]

# Normal values
ax3.scatter(
    df.loc[~exceed_mask, "production_rate_pct"],
    df.loc[~exceed_mask, "PM_mg_Nm3"],
    color=colors["pm"],
    alpha=0.5,
    s=20,
    label="Within limit"
)

# Exceedance values
ax3.scatter(
    df.loc[exceed_mask, "production_rate_pct"],
    df.loc[exceed_mask, "PM_mg_Nm3"],
    color=colors["limit"],
    alpha=0.7,
    s=25,
    label="Exceedance"
)

# Limit line
ax3.axhline(
    LIMITS["PM_mg_Nm3"],
    color=colors["limit"],
    linestyle="--"
)

ax3.set_title("Production Rate vs PM")
ax3.set_xlabel("Production Rate (%)")
ax3.set_ylabel("PM (mg/Nm3)")
ax3.legend()

# =========================================================
# 13. SAVE OUTPUT
# =========================================================

plt.tight_layout()

plt.savefig(
    "p1_analysis_charts.png",
    dpi=150,
    bbox_inches="tight"
)

print("\nCharts saved -> p1_analysis_charts.png")

print("=" * 60)
