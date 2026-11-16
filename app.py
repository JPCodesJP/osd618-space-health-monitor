"""
Main Landing Page: OSD-618 Autonomous Deep-Space Health Monitoring System
Acts as the executive command center, interactive module launcher, and architectural overview.
"""

import streamlit as st
from utils import render_study_subtitle

# Page Configuration
st.set_page_config(
    page_title="MVCT",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
  # Header Section
  st.title(
      "Autonomous Deep-Space Behavioral & Mental Health Monitoring System"
  )
  render_study_subtitle()

  st.markdown("---")

  # 1. Slim Explore Operational Modules (Centered & Narrowed width using columns)
  st.subheader("Explore Operational Modules")
  st.markdown(
      "Hover over any module symbol below to view its title, or click to launch"
      " its interactive view:"
  )

  # Use columns to restrict the width of the module container to the center portion of the screen
  _, center_col, _ = st.columns([1, 3, 1])

  with center_col:
    st.markdown(
        """
        <style>
        .module-flex-container {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 40px;
            margin: 15px 0 25px 0;
        }
        .module-item {
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .module-circle {
            width: 75px;
            height: 75px;
            border-radius: 50%;
            background: linear-gradient(135deg, #1e1e24 0%, #2d2d3a 100%);
            border: 2px solid rgba(255, 255, 255, 0.15);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            color: #ffffff;
            box-shadow: 0 6px 18px rgba(0,0,0,0.25);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            text-decoration: none !important;
            cursor: pointer;
        }
        .module-circle:hover {
            transform: translateY(-5px) scale(1.10);
            border-color: #1f77b4;
            box-shadow: 0 12px 28px rgba(31, 119, 180, 0.4);
            background: linear-gradient(135deg, #1f77b4 0%, #2ca02c 100%);
        }
        .module-tooltip {
            visibility: hidden;
            background-color: #141419;
            color: #ffffff;
            text-align: center;
            border-radius: 6px;
            padding: 5px 10px;
            position: absolute;
            z-index: 100;
            bottom: -40px;
            left: 50%;
            transform: translateX(-50%);
            opacity: 0;
            transition: opacity 0.2s ease-in-out;
            font-size: 12px;
            font-weight: 600;
            white-space: nowrap;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            border: 1px solid rgba(255,255,255,0.1);
            pointer-events: none;
        }
        .module-item:hover .module-tooltip {
            visibility: visible;
            opacity: 1;
        }
        </style>

        <div class="module-flex-container">
            <div class="module-item">
                <a href="Isolation_and_Confinement_Impact" target="_self" class="module-circle">🤝</a>
                <div class="module-tooltip">Social Isolation</div>
            </div>
            <div class="module-item">
                <a href="Error_Proneness" target="_self" class="module-circle">🧭</a>
                <div class="module-tooltip">Error-Proneness</div>
            </div>
            <div class="module-item">
                <a href="Cognitive_Impact" target="_self" class="module-circle">🔍</a>
                <div class="module-tooltip">Cognitive Impact</div>
            </div>
            <div class="module-item">
                <a href="Crew_Risk_Mitigation" target="_self" class="module-circle">🛡️</a>
                <div class="module-tooltip">Risk Forecaster & Countermeasures</div>
            </div>
            <div class="module-item">
                <a href="About" target="_self" class="module-circle">ℹ️</a>
                <div class="module-tooltip">About & System Philosophy</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

  st.markdown("---")

  # 2. End-to-End System Architecture Flow Diagram
  st.subheader("🏛️ System Architecture Design & Operational Pipeline")
  st.markdown(
      "Our autonomous health monitoring framework follows a rigorous 6-stage"
      " progression—transitioning from ground-based control data collection"
      " through orbital validation to fully autonomous deep-space mission"
      " deployment."
  )

  # Tabs to organize the two phases from your project slides
  arch_tab1, arch_tab2 = st.tabs(
      ["Phase 1: Training & Near-Earth Validation (Stages 1–3)", "Phase 2: Deep-Space Deployment & Feedback (Stages 4–6)"]
  )

  with arch_tab1:
    st.markdown("### 🔬 Phase 1: Training Software Phase")

    col_s1, col_s2, col_s3 = st.columns(3)

    with col_s1:
      st.markdown("#### Stage 1: Control Variable Data Collection")
      st.markdown("""
            * **Ground Simulation:** Uses NASA HERA (Isolation & Confinement facility) to collect dedicated baseline data.
            * **Biomarker Capture:** Gathers vitals (Bio-Monitor smart shirts), facial/vocal stress recognition, social interactions, and sleep patterns.
            """)

    with col_s2:
      st.markdown("#### Stage 2: Training Math Models")
      st.markdown("""
            * **Model Selection:** Tests multiple mathematical models to identify best-performing subsets.
            * **Model #1 (Individual):** Establishes correlations between individual biomarkers and behavioral patterns.
            * **Model #2 (Group Prediction):** Aggregates mass data across astronauts to predict risk and mitigation protocols.
            """)

    with col_s3:
      st.markdown("#### Stage 3: Near-Earth Orbital Testing")
      st.markdown("""
            * **ISS Deployment:** High-accuracy models from Stage 2 are tested on the International Space Station.
            * **Robustness Enhancement:** Compares continuous ISS telemetry against baseline data to cross-check predictive accuracy.
            """)

  with arch_tab2:
    st.markdown("### 🚀 Phase 2: Mission Deployment Phase")

    col_s4, col_s5, col_s6 = st.columns(3)

    with col_s4:
      st.markdown("#### Stage 4: Deep Space / Lunar Test")
      st.markdown("""
            * **Lunar Transit Testing:** Utilizes Moon missions as an intermediate proving ground before deep-space transit.
            * **Redundancy:** Deploys 2+ models in parallel as backup and cross-validation against system failure.
            """)

    with col_s5:
      st.markdown("#### Stage 5: Evaluation & Prediction")
      st.markdown("""
            * **Individual Alerts:** Signals when individual stress peaks; triggers countermeasure and scheduling models.
            * **Group Forecasting:** Predicts error probability curves and deploys automated risk mitigation protocols.
            """)

    with col_s6:
      st.markdown("#### Stage 6: Autonomous Feedback Loop")
      st.markdown("""
            * **Continuous Monitoring:** Continues gathering stress telemetry during and after countermeasure deployment.
            * **Efficacy & Updates:** Compares post-intervention data to evaluate effectiveness; receives periodic version updates from Earth[cite: 5, 6].
            """)

  st.markdown("---")
  st.caption(
      "🚀 Built for the NASA Space Apps Challenge | Powered by NASA OSDR OSD-618"
      " open science datasets & Streamlit edge analytics."
  )


if __name__ == "__main__":
  main()