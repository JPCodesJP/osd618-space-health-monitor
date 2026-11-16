import os
import pandas as pd
import streamlit as st

# File paths for OSD-618 Datasets
RAWM_MASTER_PATH = "osd_618_rawm_cleaned_master.csv"


@st.cache_data
def load_data(filename="osd_618_social_cleaned_master.csv"):
  if not os.path.exists(filename):
    return None
  return pd.read_csv(filename)


@st.cache_data
def load_rawm_master_data():
  """Loads the cleaned OSD-618 RAWM master dataset."""
  if not os.path.exists(RAWM_MASTER_PATH):
    return None
  return pd.read_csv(RAWM_MASTER_PATH)

def render_study_subtitle():
  """Renders a consistent subtitle with a direct link to the NASA OSD-618 repository page."""
  st.caption(
      "📡 Results shown are derived from real experimental data from **NASA"
      " GeneLab / OSDR Study OSD-618** — "
      "[View Official OSD-618 Dataset"
      " ↗](https://osdr.nasa.gov/bio/repo/data/studies/OSD-618)"
  )


def categorize_treatment(row):
  hu = str(row.get("Hindlimb_Unloading", "")).lower()
  rad = str(row.get("Ionizing_Radiation", "")).lower()
  housing = str(row.get("Housing_Condition", "")).lower()

  has_hu = "hindlimb unloaded" in hu or (
      "unloaded" in hu and "normal" not in hu and "control" not in hu
  )
  has_rad = "mixed" in rad or (
      "irradiated" in rad and "sham" not in rad and "control" not in rad
  )
  has_iso = "isolation" in housing or "isolated" in housing

  if has_hu or has_rad or has_iso:
    return "Treated / Stressed"
  else:
    return "Control / Untreated"


def get_metric_explanation(metric_name):
  name_lower = metric_name.lower()

  # Composite Stress Scores
  if "stress_score" in name_lower or "stress_indicator_score" in name_lower:
    return {
        "desc": (
            "Composite PCA (Principal Component Analysis, a mathematical"
            " statistical model) score capturing overall neurobehavioral"
            " disruption across assay parameters."
        ),
        "meaning": (
            "A **higher score** indicates greater behavioral/cognitive"
            " disruption and stress relative to controls."
        ),
    }

  # RAWM (Radial Arm Water Maze) Specific Metrics
  elif "error" in name_lower:
    return {
        "desc": (
            "Measures incorrect arm entries (spatial working and reference"
            " memory errors) during maze navigation trials."
        ),
        "meaning": (
            "A **higher score** indicates cognitive confusion, impaired spatial"
            " memory, and increased error-proneness under stress."
        ),
    }
  elif "duration" in name_lower or "time" in name_lower:
    return {
        "desc": (
            "Measures total trial duration in seconds taken to locate the"
            " escape platform."
        ),
        "meaning": (
            "A **higher duration** reflects slower navigation, hesitation, or"
            " spatial disorientation."
        ),
    }

  # NOR Specific Metrics
  elif "discrimination" in name_lower or "di_" in name_lower:
    return {
        "desc": (
            "Discrimination Index: Measures the relative preference for"
            " exploring the novel object over the familiar object."
        ),
        "meaning": (
            "A **higher score** (closer to +1) indicates strong recognition"
            " memory; scores near 0 or negative indicate cognitive impairment."
        ),
    }
  elif "novel" in name_lower and (
      "time" in name_lower
      or "duration" in name_lower
      or "percent" in name_lower
      or "ratio" in name_lower
  ):
    return {
        "desc": (
            "Measures time or proportion of exploration spent investigating the"
            " brand-new (novel) object."
        ),
        "meaning": (
            "A **higher score** indicates healthy curiosity and intact object"
            " recognition memory."
        ),
    }
  elif "familiar" in name_lower:
    return {
        "desc": (
            "Measures time or frequency spent investigating the old, previously"
            " seen object."
        ),
        "meaning": (
            "A **higher score** relative to the novel object suggests the mouse"
            " did not remember seeing it before."
        ),
    }

  # Social Approach Specific Metrics
  elif "sociability_ratio" in name_lower or "sociability_percent" in name_lower:
    return {
        "desc": (
            "Measures preference for interacting with a social target (mouse)"
            " versus an empty container."
        ),
        "meaning": (
            "A **higher score** indicates stronger sociability and social"
            " preference."
        ),
    }
  elif (
      "socialmemory_ratio" in name_lower or "socialmemory_percent" in name_lower
  ):
    return {
        "desc": (
            "Measures preference for exploring a novel (unfamiliar) mouse"
            " versus a familiar mouse."
        ),
        "meaning": (
            "A **higher score** indicates better social recognition and"
            " novelty memory."
        ),
    }

  # General Locomotor / Habituation / Velocity
  elif "distance" in name_lower or "velocity" in name_lower:
    return {
        "desc": (
            "Measures general locomotor activity (total distance traveled in cm"
            " or movement speed)."
        ),
        "meaning": (
            "A **higher score** indicates greater physical movement or arena"
            " exploration."
        ),
    }
  elif "habituation" in name_lower:
    return {
        "desc": (
            "Measures baseline exploratory activity in the arena before test"
            " targets are introduced."
        ),
        "meaning": (
            "A **higher score** indicates higher baseline exploratory"
            " movement."
        ),
    }
  else:
    return {
        "desc": "Specific behavioral parameter recorded during the assay.",
        "meaning": (
            "A **higher score** represents a higher numerical value for this"
            " specific measurement."
        ),
    }


def render_sidebar_filters(dataframe, prefix="default"):
  st.sidebar.header("Spaceflight Factor Controls")
  st.sidebar.caption(
      "Check or uncheck factors below to isolate specific spaceflight impacts."
  )

  def render_checkbox_group(title, column_name, df):
    if column_name not in df.columns:
      return []
    st.sidebar.subheader(title)
    options = sorted(df[column_name].dropna().unique().tolist())
    selected = []
    for opt in options:
      count = len(df[df[column_name] == opt])
      if st.sidebar.checkbox(
          f"{opt} ({count})", value=True, key=f"{prefix}_{column_name}_{opt}"
      ):
        selected.append(opt)
    if not selected:
      selected = options
    return selected

  selected_categories = render_checkbox_group(
      "Compare Groups", "Treatment_Category", dataframe
  )
  st.sidebar.divider()
  selected_hu = render_checkbox_group(
      "Altered Gravity", "Hindlimb_Unloading", dataframe
  )
  st.sidebar.divider()
  selected_rad = render_checkbox_group(
      "Ionizing Radiation", "Ionizing_Radiation", dataframe
  )
  st.sidebar.divider()
  selected_housing = render_checkbox_group(
      "Housing Condition", "Housing_Condition", dataframe
  )

  filtered_df = dataframe.copy()
  if "Treatment_Category" in filtered_df.columns and selected_categories:
    filtered_df = filtered_df[
        filtered_df["Treatment_Category"].isin(selected_categories)
    ]
  if "Hindlimb_Unloading" in filtered_df.columns and selected_hu:
    filtered_df = filtered_df[
        filtered_df["Hindlimb_Unloading"].isin(selected_hu)
    ]
  if "Ionizing_Radiation" in filtered_df.columns and selected_rad:
    filtered_df = filtered_df[
        filtered_df["Ionizing_Radiation"].isin(selected_rad)
    ]
  if "Housing_Condition" in filtered_df.columns and selected_housing:
    filtered_df = filtered_df[
        filtered_df["Housing_Condition"].isin(selected_housing)
    ]

  return filtered_df