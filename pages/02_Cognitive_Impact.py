import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from utils import (
    categorize_treatment,
    get_metric_explanation,
    load_data,
    render_sidebar_filters,
    render_study_subtitle
)

st.set_page_config(
    page_title='Novel Object Recognition - OSD-618',
    page_icon='🔍',
    layout='wide',
)

df = load_data('osd_618_nor_cleaned_master.csv')
if df is None:
  st.error(
      'Processed NOR dataset `osd_618_nor_cleaned_master.csv` not found!'
      ' Please run `clean_correlate_nor.py` first.'
  )
  st.stop()

for col in ['Hindlimb_Unloading', 'Ionizing_Radiation', 'Housing_Condition']:
  df[col] = (
      df[col].fillna('Not Specified').astype(str).str.strip()
      if col in df.columns
      else 'Not Specified'
  )

df['Treatment_Category'] = df.apply(categorize_treatment, axis=1)

# --- SIMPLIFIED SIDEBAR FILTERS ---
filtered_df = render_sidebar_filters(df, prefix='nor')

st.title('Cognitive & Memory Stress')
render_study_subtitle()
st.markdown(
    'Evaluating **recognition memory** and **cognitive decline** by comparing'
    ' how much time mice spend exploring a novel object versus a familiar'
    ' object.'
)

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
if 'NOR_Stress_Score' in filtered_df.columns:
  col4.metric(
      'Mean NOR Stress Score', f"{filtered_df['NOR_Stress_Score'].mean():.2f}"
  )

st.divider()

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
      'Select NOR Metric:',
      options=numeric_cols,
      index=(
          numeric_cols.index('NOR_Stress_Score')
          if 'NOR_Stress_Score' in numeric_cols
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
      title=f'NOR Comparison: {selected_metric} by {x_axis_choice}',
  )
  st.plotly_chart(fig_box, use_container_width=True)

  st.markdown('### Plain-English Insight & Interpretation')
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

    st.success(f"""
        ### Key Takeaway
        * **The `{g2_name}` group averaged **{abs(diff):.3f} {direction}** compared to the `{g1_name}` group.**
        * **What a higher score means:** {info['meaning']}
        
        ---
        **Metric Details:**
        * **What `{selected_metric}` measures:** {info['desc']}
        * **Group Averages:** 
          * **{g1_name}:** `{g1_mean:.3f}` ({g1_count} animals)
          * **{g2_name}:** `{g2_mean:.3f}` ({g2_count} animals)
        """)
  else:
    st.info(
        'Please ensure at least two subgroups are present in your filter'
        ' selection to view a direct comparison.'
    )