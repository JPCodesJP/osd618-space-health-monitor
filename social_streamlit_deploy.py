import os
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title='OSD-618: Spaceflight Stress & Behavior Dashboard',
    page_icon='🐁',
    layout='wide',
)


# Load Data with Caching
@st.cache_data
def load_data():
  master_file = 'osd_618_social_cleaned_master.csv'
  if not os.path.exists(master_file):
    return None
  return pd.read_csv(master_file)


df = load_data()

if df is None:
  st.error(
      '⚠️ Processed master dataset `osd_618_social_cleaned_master.csv` not'
      ' found! Please run `clean_correlate_social_2.py` first.'
  )
  st.stop()

# Ensure clean string representation
for col in ['Hindlimb_Unloading', 'Ionizing_Radiation', 'Housing_Condition']:
  if col in df.columns:
    df[col] = df[col].fillna('Not Specified').astype(str).str.strip()
  else:
    df[col] = 'Not Specified'


# --- DATA CATEGORIZATION ---
def categorize_treatment(row):
  hu = str(row.get('Hindlimb_Unloading', '')).lower()
  rad = str(row.get('Ionizing_Radiation', '')).lower()
  housing = str(row.get('Housing_Condition', '')).lower()

  has_hu = 'hindlimb unloaded' in hu or (
      'unloaded' in hu and 'normal' not in hu and 'control' not in hu
  )
  has_rad = 'mixed' in rad or (
      'irradiated' in rad and 'sham' not in rad and 'control' not in rad
  )
  has_iso = 'isolation' in housing or 'isolated' in housing

  if has_hu or has_rad or has_iso:
    return 'Treated / Stressed'
  else:
    return 'Control / Untreated'


df['Treatment_Category'] = df.apply(categorize_treatment, axis=1)

# --- SIDEBAR FILTERS WITH SMART FALLBACK ---
st.sidebar.header('🔍 Group & Parameter Filters')
st.sidebar.caption(
    'Uncheck boxes to filter. If all are unchecked, it safely shows all'
    ' records.'
)


def render_checkbox_group(title, column_name, dataframe):
  st.sidebar.subheader(title)
  options = sorted(dataframe[column_name].unique().tolist())
  selected = []
  for opt in options:
    count = len(dataframe[dataframe[column_name] == opt])
    if st.sidebar.checkbox(
        f'{opt} ({count})', value=True, key=f'{column_name}_{opt}'
    ):
      selected.append(opt)
  if not selected:
    selected = options
  return selected


selected_categories = render_checkbox_group(
    'Compare Groups', 'Treatment_Category', df
)
st.sidebar.divider()
selected_hu = render_checkbox_group(
    'Hindlimb Unloading', 'Hindlimb_Unloading', df
)
st.sidebar.divider()
selected_rad = render_checkbox_group(
    'Ionizing Radiation', 'Ionizing_Radiation', df
)
st.sidebar.divider()
selected_housing = render_checkbox_group(
    'Housing Condition', 'Housing_Condition', df
)

# Apply Checkbox Filters
filtered_df = df[
    (df['Treatment_Category'].isin(selected_categories))
    & (df['Hindlimb_Unloading'].isin(selected_hu))
    & (df['Ionizing_Radiation'].isin(selected_rad))
    & (df['Housing_Condition'].isin(selected_housing))
]

# --- MAIN DASHBOARD HEADER ---
st.title('🐁 OSD-618: Spaceflight Stress & Social Behavior Dashboard')
st.markdown(
    'Directly comparing how **Hindlimb Unloading (HU)**, **Ionizing Radiation**,'
    ' and **Social Isolation** impact mouse social approach and stress'
    ' indicators compared to controls.'
)

# Metrics Overview
col1, col2, col3, col4 = st.columns(4)
col1.metric('Total Animals (Filtered)', len(filtered_df))
col2.metric(
    'Control / Untreated',
    len(
        filtered_df[
            filtered_df['Treatment_Category'] == 'Control / Untreated'
        ]
    ),
)
col3.metric(
    'Treated / Stressed',
    len(
        filtered_df[filtered_df['Treatment_Category'] == 'Treated / Stressed']
    ),
)
if 'Stress_Indicator_Score' in filtered_df.columns:
  col4.metric(
      'Mean Stress Score',
      f"{filtered_df['Stress_Indicator_Score'].mean():.2f}",
  )

st.divider()

# --- TABS FOR LAYOUT ---
tab1, tab2, tab3 = st.tabs([
    '📊 Behavioral Comparison by Treatment',
    '🗺️ Animal ID & Treatment Map',
    '🔥 Group Stress & Behavior Profile (Heatmap)',
])


# Helper function to explain metrics in plain English
def get_metric_explanation(metric_name):
  name_lower = metric_name.lower()
  if 'stress_indicator_score' in name_lower:
    return {
        'desc': (
            'Composite PCA score capturing overall neurobehavioral disruption'
            ' across tests.'
        ),
        'meaning': (
            'A **higher score** indicates greater overall behavioral'
            ' disruption and stress relative to controls.'
        ),
    }
  elif 'sociability_ratio' in name_lower or 'sociability_percent' in name_lower:
    return {
        'desc': (
            'Measures preference for interacting with a social target (mouse)'
            ' versus an empty container.'
        ),
        'meaning': (
            'A **higher score** indicates stronger sociability and social'
            ' preference.'
        ),
    }
  elif (
      'socialmemory_ratio' in name_lower or 'socialmemory_percent' in name_lower
  ):
    return {
        'desc': (
            'Measures preference for exploring a novel (unfamiliar) mouse'
            ' versus a familiar mouse.'
        ),
        'meaning': (
            'A **higher score** indicates better social recognition and'
            ' novelty memory.'
        ),
    }
  elif 'distance' in name_lower or 'velocity' in name_lower:
    return {
        'desc': (
            'Measures locomotor activity (total distance traveled in cm or'
            ' movement speed).'
        ),
        'meaning': (
            'A **higher score** indicates greater physical activity or'
            ' exploration.'
        ),
    }
  elif 'habituation' in name_lower:
    return {
        'desc': (
            'Measures baseline exploratory activity in the chamber before'
            ' social targets are introduced.'
        ),
        'meaning': (
            'A **higher score** indicates higher baseline exploratory'
            ' movement.'
        ),
    }
  else:
    return {
        'desc': 'Specific behavioral parameter recorded during the test.',
        'meaning': (
            'A **higher score** represents a higher numerical value for this'
            ' specific measurement.'
        ),
    }


with tab1:
  st.subheader('Behavioral Differences Across Experimental Groups')
  st.markdown(
      'Choose what category you want to compare on the chart, and select a'
      ' behavioral metric below.'
  )

  col_sel1, col_sel2 = st.columns(2)
  with col_sel1:
    x_axis_choice = st.selectbox(
        'Compare Groups By:',
        options=[
            'Treatment Status (Control vs. Stressed)',
            'Hindlimb Unloading (HU vs. Control)',
            'Ionizing Radiation (Radiation vs. Sham)',
            'Housing Condition (Isolated vs. Group)',
        ],
    )
  with col_sel2:
    numeric_cols = [
        c
        for c in filtered_df.select_dtypes(include=[np.number]).columns
        if c not in ['Animal_ID', 'Age_Timepoint']
    ]
    selected_metric = st.selectbox(
        'Select Behavioral Metric:',
        options=numeric_cols,
        index=(
            numeric_cols.index('Stress_Indicator_Score')
            if 'Stress_Indicator_Score' in numeric_cols
            else 0
        ),
    )

  factor_map = {
      'Treatment Status (Control vs. Stressed)': 'Treatment_Category',
      'Hindlimb Unloading (HU vs. Control)': 'Hindlimb_Unloading',
      'Ionizing Radiation (Radiation vs. Sham)': 'Ionizing_Radiation',
      'Housing Condition (Isolated vs. Group)': 'Housing_Condition',
  }
  group_col = factor_map[x_axis_choice]

  if selected_metric and group_col:
    fig_box = px.box(
        filtered_df,
        x=group_col,
        y=selected_metric,
        color=group_col,
        points='all',
        title=f'Comparison of {selected_metric} by {x_axis_choice}',
    )
    st.plotly_chart(fig_box, use_container_width=True)

    # --- DYNAMIC PLAIN-ENGLISH SUMMARY ---
    st.markdown('### 🧠 Plain-English Insight & Interpretation')

    info = get_metric_explanation(selected_metric)
    group_stats = (
        filtered_df.groupby(group_col)[selected_metric]
        .agg(['mean', 'median', 'count'])
        .reset_index()
    )

    if len(group_stats) >= 2:
      g1 = group_stats.iloc[0]
      g2 = group_stats.iloc[1]
      g1_name, g1_mean, g1_count = g1[group_col], g1['mean'], int(g1['count'])
      g2_name, g2_mean, g2_count = g2[group_col], g2['mean'], int(g2['count'])

      diff = g2_mean - g1_mean
      direction = (
          'higher' if diff > 0 else ('lower' if diff < 0 else 'about the same')
      )

      st.success(
          f"""
                ### 🎯 Key Takeaway
                * **The `{g2_name}` group averaged **{abs(diff):.3f} {direction}** compared to the `{g1_name}` group.**
                * **What a higher score means:** {info['meaning']}
                
                ---
                **Metric Details:**
                * **What `{selected_metric}` measures:** {info['desc']}
                * **Group Averages:** 
                  * **{g1_name}:** `{g1_mean:.3f}` ({g1_count} animals)
                  * **{g2_name}:** `{g2_mean:.3f}` ({g2_count} animals)
                """
      )
    else:
      st.info(
          'Please ensure at least two subgroups are present in your filter'
          ' selection to view a direct comparison.'
      )

with tab2:
  st.subheader('Animal ID, Age/Timepoint & Treatment Mapping')
  st.markdown(
      'Inspect individual animals, their separated **Animal ID** and'
      ' **Age/Timepoint**, and their specific environmental stressors.'
  )

  display_cols = [
      c
      for c in [
          'Animal_ID',
          'Age_Timepoint',
          'Treatment_Category',
          'Hindlimb_Unloading',
          'Ionizing_Radiation',
          'Housing_Condition',
          'Stress_Indicator_Score',
      ]
      if c in filtered_df.columns
  ]

  search_id = st.text_input('🔍 Search specific Animal ID (e.g., 309):')
  map_df = filtered_df[display_cols]
  if search_id:
    map_df = map_df[
        map_df['Animal_ID'].astype(str).str.contains(search_id, case=False)
    ]

  st.dataframe(map_df, use_container_width=True, hide_index=True)

  csv_data = map_df.to_csv(index=False).encode('utf-8')
  st.download_button(
      label='📥 Download Animal Mapping CSV',
      data=csv_data,
      file_name='animal_id_age_treatment_map.csv',
      mime='text/csv',
  )

with tab3:
  st.subheader('🔥 Group-Level Stress & Behavior Comparison Heatmap')
  st.markdown(
      'This heatmap displays the **average (mean) score** for key behavioral'
      ' and stress indicators broken down by specific experimental conditions.'
  )

  group_factor = st.selectbox(
      'Select Stress Factor to Compare Across Groups:',
      options=[
          col
          for col in [
              'Hindlimb_Unloading',
              'Ionizing_Radiation',
              'Housing_Condition',
              'Treatment_Category',
          ]
          if filtered_df[col].nunique() > 1
      ],
  )

  default_metrics = [
      c
      for c in [
          'Stress_Indicator_Score',
          'Sociability_ratio_3min',
          'Sociability_ratio_5min',
          'SocialMemory_ratio_3min',
          'SocialMemory_ratio_5min',
          'Social_Habituation_distance_cm',
      ]
      if c in filtered_df.columns
  ]

  if not default_metrics:
    default_metrics = numeric_cols[:6]

  grouped_means = (
      filtered_df.groupby(group_factor)[default_metrics].mean().reset_index()
  )
  grouped_means = grouped_means.set_index(group_factor)

  fig_heat = px.imshow(
      grouped_means,
      text_auto='.2f',
      aspect='auto',
      color_continuous_scale='Plasma',
      origin='lower',
  )
  fig_heat.update_layout(
      title=(
          f'Average Behavioral & Stress Scores by {group_factor.replace("_", " ")}'
      ),
      xaxis_title='Behavioral / Stress Metrics',
      yaxis_title=group_factor.replace('_', ' '),
      height=500,
  )
  st.plotly_chart(fig_heat, use_container_width=True)