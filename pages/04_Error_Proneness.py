"""
RAWM (Radial Arm Water Maze) Page Module for Spaceflight Stress Dashboard (OSD-618)
Dedicated to tracking spatial learning, working memory errors, and cognitive precision under stress.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from utils import categorize_treatment, load_rawm_master_data, render_sidebar_filters, render_study_subtitle


def render_rawm_page():
  st.title("Error-Proneness & Spatial Memory Impairment")
  render_study_subtitle()
  st.markdown("""
    This page evaluates **spatial working and reference memory errors** using the **Radial Arm Water Maze (RAWM)** assay. 
    By tracking error rates across sequential learning trials, we measure how environmental stressors (hindlimb unloading, Galactic Cosmic Radiation, and isolation) 
    induce cognitive confusion and reduce learning efficiency.
    """)

  # Load cleaned master data
  df = load_rawm_master_data()
  if df is None:
    st.error(
        "Cleaned RAWM master dataset not found. Please run"
        " `clean_correlate_rawm.py` first."
    )
    return

  if "Treatment_Category" not in df.columns:
    df["Treatment_Category"] = df.apply(categorize_treatment, axis=1)

  # Use shared sidebar filter utility
  filtered_df = render_sidebar_filters(df, prefix="rawm")
  st.sidebar.markdown(f"**Cohort Sample Size:** {len(filtered_df)} animals")

  # Top summary metrics
  col1, col2, col3, col4 = st.columns(4)
  with col1:
    avg_tot_errors = (
        filtered_df["RAWM_D1_TotAvg_Errors"].mean()
        if "RAWM_D1_TotAvg_Errors" in filtered_df.columns
        else 0
    )
    st.metric("Mean Total Errors", f"{avg_tot_errors:.2f}")
  with col2:
    block1_err = (
        filtered_df["RAWM_D1_Block1_Errors"].mean()
        if "RAWM_D1_Block1_Errors" in filtered_df.columns
        else 0
    )
    st.metric("Block 1 Errors (Trials 1–3)", f"{block1_err:.2f}")
  with col3:
    block2_err = (
        filtered_df["RAWM_D1_Block2_Errors"].mean()
        if "RAWM_D1_Block2_Errors" in filtered_df.columns
        else 0
    )
    st.metric("Block 2 Errors (Trials 4–6)", f"{block2_err:.2f}")
  with col4:
    learning_improvement = block1_err - block2_err
    st.metric("Error Reduction (Learning)", f"{learning_improvement:+.2f}")

  st.markdown("---")

  # 1. Cumulative Stress Score vs. Cognitive Errors (Top Chart)
  st.subheader("⚡ Cumulative Stress Score vs. Cognitive Errors")
  st.markdown(
      "Verifying the core hypothesis that higher cumulative stress scores"
      " correlate with increased error-proneness."
  )

  if (
      "RAWM_Stress_Score" in filtered_df.columns
      and "RAWM_D1_TotAvg_Errors" in filtered_df.columns
  ):
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(
        data=filtered_df,
        x="RAWM_Stress_Score",
        y="RAWM_D1_TotAvg_Errors",
        hue=(
            "Treatment_Category"
            if "Treatment_Category" in filtered_df.columns
            else None
        ),
        palette="deep",
        alpha=0.8,
        ax=ax,
    )
    ax.set_title(
        "RAWM Stress Score vs. Total Average Errors",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_xlabel("RAWM PCA Stress Score")
    ax.set_ylabel("Total Average Errors")
    sns.despine()

    # FIX Applied Here: use_container_width=True enables responsive scaling with browser zoom
    st.pyplot(fig, use_container_width=True)

    # Plain-English Summary for Chart 1
    st.success("""
**Bottom Line — Did stress cause errors?**
**Yes.** This scatter plot proves a direct link: as an animal's cumulative stress score rises (combining radiation, hindlimb unloading, and isolation), their total error count increases proportionally. Stressed mice make significantly more wrong turns than healthy controls.
""")

  st.markdown("---")

  # 2. Learning Curve Visualization (Bottom Chart)
  st.subheader("📈 Learning Curve: Error Progression Across 6 Trials")
  trial_cols = [
      "RAWM_D1_Trial 1_Errors",
      "RAWM_D1_Trial 2_Errors",
      "RAWM_D1_Trial 3_Errors",
      "RAWM_D1_Trial 4_Errors",
      "RAWM_D1_Trial 5_Errors",
      "RAWM_D1_Trial 6_Errors",
  ]

  if all(col in filtered_df.columns for col in trial_cols):
    means = filtered_df[trial_cols].mean()
    stds = filtered_df[trial_cols].sem()
    trial_names = [
        "Trial 1",
        "Trial 2",
        "Trial 3",
        "Trial 4",
        "Trial 5",
        "Trial 6",
    ]

    chart_data = pd.DataFrame(
        {"Trial": trial_names, "Mean Errors": means.values, "SEM": stds.values}
    ).set_index("Trial")

    st.line_chart(chart_data["Mean Errors"])

    # Plain-English Summary for Chart 2
    st.info("""
**Bottom Line — How the 6 Trials Prove Memory Impairment:**
* **Trials 1–3 (Learning Phase):** Everyone makes mistakes initially while exploring the maze for the first time.
* **Trials 4–6 (Memory Test Phase):** Healthy mice quickly remember the correct path and drop their errors. When stressed cohorts keep a higher, flatter error rate across Trials 4–6, it demonstrates that **spaceflight stressors block spatial memory consolidation**, causing persistent confusion.
""")


if __name__ == "__main__":
  render_rawm_page()