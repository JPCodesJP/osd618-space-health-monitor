"""
About Page: OSD-618 Autonomous Deep-Space Health Monitoring System
Provides executive summaries, OSDR attribution, and the core deep-space philosophy.
"""

import streamlit as st
from utils import render_study_subtitle

# Page Title & Subtitle
st.title("ℹ️ About OSD-618: System Philosophy & Attribution")
render_study_subtitle()

st.markdown("---")

# 1. Executive Summary & Core Philosophy
st.subheader("🧠 The Operational Imperative: Autonomous Deep Space")
st.markdown("""
During long-duration crewed transit missions (such as a journey to Mars), **real-time communication with Earth is physically impossible** due to light-speed radio delays ranging from 4 to 24 minutes each way. 

This dashboard functions as a conceptual prototype for an **autonomous, onboard decision support system**. By ingesting and modeling experimental spaceflight stressor data from **NASA OSDR OSD-618**, this system continuously analyzes behavioral and neurological telemetry locally, predicts performance degradation, and automatically triggers countermeasures—**without waiting for instructions from Earth mission control.**
""")

st.markdown("---")

# 2. Underlying Dataset & Architecture Details
col_left, col_right = st.columns(2)

with col_left:
  st.markdown("""
    ### 🧪 Underlying NASA Dataset (OSD-618)
    Our predictive models and behavioral modules are grounded in empirical multi-stressor rodent study data, capturing the synergistic impacts of:
    * **Altered Gravity:** Hindlimb unloading (HU) simulating fluid shifts.
    * **Radiation:** Ionizing radiation fields mimicking Galactic Cosmic Rays (GCR).
    * **Confinement:** Social isolation and housing density stress.
    """)

with col_right:
  st.markdown("""
    ### 🛡️ Core Dashboard Modules
    Use the sidebar to navigate across the system architecture:
    * **01 - Isolation & Confinement Impact:** Evaluates social approach and sociability deficits (Week 34).
    * **02 - Cognitive Impact (NOR):** Tracks novelty recognition memory decay (Week 39).
    * **03 - Error Proneness (RAWM):** Analyzes spatial working memory and trial error rates (Week 42).
    * **04 - Crew Risk Mitigation:** Projects long-duration risk trajectories and automated countermeasures.
    """)

st.markdown("---")

# 3. Hackathon Context & Attributions
st.subheader("🏆 Hackathon Project Context")
st.markdown("""
* **Event:** NASA Space Apps Challenge
* **Primary Objective:** Transform raw Open Science Data Repository (OSDR) data into actionable edge-computing tools for deep-space missions.
* **Disclaimer:** Predictive regression models implemented in this prototype serve as a conceptual framework to demonstrate autonomous decision support. Real-world mission architects can adapt or substitute advanced biophysical models tailored to specific operational validation thresholds.
""")

st.markdown("---")
st.caption(
    "🚀 Built for the NASA Space Apps Challenge | Powered by NASA OSDR OSD-618"
    " open science datasets & Streamlit edge analytics."
)