"""Employee Attrition Analysis - Streamlit dashboard.

Run with:  streamlit run app.py
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit.runtime import exists

# Makes the VS Code "Run" button work: if the file was started as plain
# Python, relaunch it through Streamlit, which opens the browser.
if not exists():
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(Path(__file__).resolve())])
    sys.exit()

# ----------------------------------------------------------------------------
# Page setup
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Employee Attrition Analysis",
    page_icon="📊",
    layout="wide",
)

DATA_PATH = Path(__file__).parent  / "Employee_Attrition_Analysis_6000_Records.csv"
COLORS = {"Yes": "#E4572E", "No": "#2E86AB"}


# ----------------------------------------------------------------------------
# Data loading & preparation (cached so it only runs once)
# ----------------------------------------------------------------------------
@st.cache_data(show_spinner="Loading data...")
def load_data(source) -> pd.DataFrame:
    df = pd.read_csv(source)
    df = df.drop_duplicates().copy()

    if "Age" in df.columns:
        df["AgeGroup"] = pd.cut(
            df["Age"],
            bins=[17, 25, 35, 45, 55, 65],
            labels=["18-25", "26-35", "36-45", "46-55", "56-65"],
        )
    df["AttritionEncoded"] = df["Attrition"].map({"Yes": 1, "No": 0})
    return df


def get_dataframe() -> pd.DataFrame | None:
    """Use the bundled CSV if present, otherwise ask the user to upload one."""
    if DATA_PATH.exists():
        return load_data(DATA_PATH)
    uploaded = st.sidebar.file_uploader("Upload the attrition CSV", type="csv")
    if uploaded is None:
        st.info("Place the CSV in `data/` or upload it from the sidebar to begin.")
        return None
    return load_data(uploaded)


def attrition_rate_table(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Attrition % and headcount for every category of `col`."""
    out = (
        df.groupby(col, observed=True)["AttritionEncoded"]
        .agg(AttritionRate="mean", Employees="count")
        .reset_index()
    )
    out["AttritionRate"] = (out["AttritionRate"] * 100).round(1)
    return out


def rate_bar(df: pd.DataFrame, col: str, title: str, horizontal: bool = False):
    t = attrition_rate_table(df, col)
    if horizontal:
        t = t.sort_values("AttritionRate")
        fig = px.bar(t, x="AttritionRate", y=col, orientation="h",
                     text="AttritionRate", hover_data=["Employees"])
    else:
        fig = px.bar(t, x=col, y="AttritionRate", text="AttritionRate",
                     hover_data=["Employees"])
    fig.update_traces(marker_color=COLORS["Yes"], texttemplate="%{text}%")
    fig.update_layout(title=title, yaxis_title=None if horizontal else "Attrition rate (%)",
                      xaxis_title="Attrition rate (%)" if horizontal else None,
                      margin=dict(t=50, b=10))
    return fig


def count_bar(df: pd.DataFrame, col: str, title: str):
    fig = px.histogram(df, x=col, color="Attrition", barmode="group",
                       color_discrete_map=COLORS)
    fig.update_layout(title=title, yaxis_title="Employees", margin=dict(t=50, b=10))
    return fig


def has(df: pd.DataFrame, *cols: str) -> bool:
    return all(c in df.columns for c in cols)


# ----------------------------------------------------------------------------
# Load
# ----------------------------------------------------------------------------
st.title("📊 Employee Attrition Analysis")
st.caption("Interactive EDA dashboard - use the sidebar filters to slice the data.")

df = get_dataframe()
if df is None:
    st.stop()

# ----------------------------------------------------------------------------
# Sidebar filters
# ----------------------------------------------------------------------------
st.sidebar.header("Filters")
filtered = df.copy()

for col, label in [
    ("Department", "Department"),
    ("JobRole", "Job role"),
    ("Gender", "Gender"),
    ("OverTime", "Overtime"),
    ("BusinessTravel", "Business travel"),
]:
    if col in filtered.columns:
        options = sorted(filtered[col].dropna().unique())
        chosen = st.sidebar.multiselect(label, options, default=options)
        filtered = filtered[filtered[col].isin(chosen)]

if "Age" in filtered.columns:
    lo, hi = int(df["Age"].min()), int(df["Age"].max())
    age_range = st.sidebar.slider("Age range", lo, hi, (lo, hi))
    filtered = filtered[filtered["Age"].between(*age_range)]

if filtered.empty:
    st.warning("No employees match the current filters.")
    st.stop()

st.sidebar.markdown(f"**{len(filtered):,}** of {len(df):,} employees selected")
st.sidebar.download_button(
    "Download filtered data (CSV)",
    filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_attrition_data.csv",
    mime="text/csv",
)

# ----------------------------------------------------------------------------
# KPI cards
# ----------------------------------------------------------------------------
total = len(filtered)
left = int((filtered["Attrition"] == "Yes").sum())
stayed = total - left
overall_rate = df["AttritionEncoded"].mean() * 100
rate = left / total * 100

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total employees", f"{total:,}")
k2.metric("Employees left", f"{left:,}")
k3.metric("Employees stayed", f"{stayed:,}")
k4.metric("Attrition rate", f"{rate:.1f}%", delta=f"{rate - overall_rate:+.1f} pts vs overall",
          delta_color="inverse")

st.divider()

# ----------------------------------------------------------------------------
# Tabs
# ----------------------------------------------------------------------------
tabs = st.tabs([
    "Overview", "People", "Work factors", "Pay & tenure",
    "Correlation", "High-risk groups", "Data",
])

# ---- Overview --------------------------------------------------------------
with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        fig = px.pie(filtered, names="Attrition", hole=0.5,
                     color="Attrition", color_discrete_map=COLORS,
                     title="Attrition distribution")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        if has(filtered, "Department"):
            st.plotly_chart(rate_bar(filtered, "Department", "Attrition rate by department"),
                            use_container_width=True)

    if has(filtered, "JobRole"):
        st.plotly_chart(rate_bar(filtered, "JobRole", "Attrition rate by job role", horizontal=True),
                        use_container_width=True)

# ---- People ----------------------------------------------------------------
with tabs[1]:
    c1, c2 = st.columns(2)
    if has(filtered, "Gender"):
        c1.plotly_chart(count_bar(filtered, "Gender", "Attrition by gender"),
                        use_container_width=True)
    if has(filtered, "AgeGroup"):
        c2.plotly_chart(rate_bar(filtered, "AgeGroup", "Attrition rate by age group"),
                        use_container_width=True)
    if has(filtered, "Age"):
        fig = px.box(filtered, x="Attrition", y="Age", color="Attrition",
                     color_discrete_map=COLORS, title="Age distribution by attrition")
        st.plotly_chart(fig, use_container_width=True)

# ---- Work factors ----------------------------------------------------------
with tabs[2]:
    pairs = [
        ("OverTime", "Attrition rate by overtime"),
        ("BusinessTravel", "Attrition rate by business travel"),
        ("JobSatisfaction", "Attrition rate by job satisfaction"),
        ("WorkLifeBalance", "Attrition rate by work-life balance"),
        ("JobLevel", "Attrition rate by job level"),
        ("TrainingTimesLastYear", "Attrition rate by training frequency"),
    ]
    available = [(c, t) for c, t in pairs if has(filtered, c)]
    for i in range(0, len(available), 2):
        cols = st.columns(2)
        for slot, (c, t) in zip(cols, available[i:i + 2]):
            slot.plotly_chart(rate_bar(filtered, c, t), use_container_width=True)

# ---- Pay & tenure ----------------------------------------------------------
with tabs[3]:
    numeric_views = [
        ("MonthlyIncome", "Monthly income vs attrition"),
        ("YearsAtCompany", "Years at company vs attrition"),
        ("DistanceFromHome", "Distance from home vs attrition"),
    ]
    available = [(c, t) for c, t in numeric_views if has(filtered, c)]
    for i in range(0, len(available), 2):
        cols = st.columns(2)
        for slot, (c, t) in zip(cols, available[i:i + 2]):
            fig = px.box(filtered, x="Attrition", y=c, color="Attrition",
                         color_discrete_map=COLORS, title=t)
            fig.update_layout(showlegend=False)
            slot.plotly_chart(fig, use_container_width=True)

# ---- Correlation -----------------------------------------------------------
with tabs[4]:
    numeric_df = filtered.select_dtypes(include=np.number)
    if numeric_df.shape[1] > 1:
        corr = numeric_df.corr()
        fig = px.imshow(corr, color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                        aspect="auto", title="Correlation heatmap")
        fig.update_layout(height=650)
        st.plotly_chart(fig, use_container_width=True)

        if "AttritionEncoded" in corr.columns:
            top = (corr["AttritionEncoded"].drop("AttritionEncoded")
                   .sort_values(key=abs, ascending=False).head(10).reset_index())
            top.columns = ["Feature", "Correlation with attrition"]
            st.subheader("Top 10 features associated with attrition")
            st.dataframe(top, use_container_width=True, hide_index=True)
            st.caption("Correlation shows association, not causation.")

# ---- High-risk groups ------------------------------------------------------
with tabs[5]:
    st.subheader("Find high-risk employee groups")
    candidates = [c for c in ["Department", "JobRole", "OverTime", "JobSatisfaction",
                              "WorkLifeBalance", "BusinessTravel", "JobLevel", "AgeGroup"]
                  if c in filtered.columns]
    chosen = st.multiselect("Group by (pick 1-3 columns)", candidates,
                            default=[c for c in ["OverTime", "JobSatisfaction"] if c in candidates],
                            max_selections=3)
    min_size = st.slider("Minimum group size", 5, 100, 20)
    if chosen:
        grp = (filtered.groupby(chosen, observed=True)["AttritionEncoded"]
               .agg(AttritionRate="mean", Employees="count").reset_index())
        grp["AttritionRate"] = (grp["AttritionRate"] * 100).round(1)
        grp = grp[grp["Employees"] >= min_size].sort_values("AttritionRate", ascending=False)
        st.dataframe(grp, use_container_width=True, hide_index=True)
        if len(chosen) == 2 and not grp.empty:
            pivot = grp.pivot(index=chosen[0], columns=chosen[1], values="AttritionRate")
            fig = px.imshow(pivot, text_auto=True, color_continuous_scale="Reds",
                            aspect="auto", title="Attrition rate (%) heatmap")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select at least one column.")

# ---- Data ------------------------------------------------------------------
with tabs[6]:
    st.subheader("Dataset preview")
    st.dataframe(filtered.head(200), use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Summary statistics**")
        st.dataframe(filtered.describe().T, use_container_width=True)
    with c2:
        st.markdown("**Missing values**")
        miss = filtered.isnull().sum().rename("Missing").to_frame()
        st.dataframe(miss[miss["Missing"] > 0] if miss["Missing"].any() else miss,
                     use_container_width=True)
        st.write(f"Rows: **{filtered.shape[0]:,}** | Columns: **{filtered.shape[1]}**")
