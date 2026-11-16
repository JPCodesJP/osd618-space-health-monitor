import re
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# 1. Load RAWM dataset and OSD metadata (Skip renaming from Data Dictionary!)
df = pd.read_csv('LSDS-48_Radial_Arm_Water_Maze_618_RAWM_TRANSFORMED.csv')
osd_meta = pd.read_csv('s_OSD-618.txt', sep='\t')


def find_matching_column(dataframe, keywords):
  for col in dataframe.columns:
    if any(kw.lower() in col.lower() for kw in keywords):
      return col
  return dataframe.columns[0]


beh_id_col = find_matching_column(df, ['subject', 'sample', 'source', 'id'])
meta_id_col = find_matching_column(
    osd_meta, ['source name', 'sample name', 'subject', 'id']
)


# 2. Separate Animal ID and Age/Timepoint
def parse_animal_id_and_age(val):
  val_str = str(val).strip()
  if '_' in val_str:
    parts = val_str.split('_', 1)
    return parts[0].strip().upper(), parts[1].strip().upper()
  match = re.search(r'\d+', val_str)
  num_id = match.group(0) if match else val_str
  return num_id.upper(), 'UNKNOWN'


parsed_tuples = df[beh_id_col].apply(parse_animal_id_and_age)
df['Animal_ID'] = [t[0] for t in parsed_tuples]
df['Age_Timepoint'] = [t[1] for t in parsed_tuples]

osd_meta['Join_ID'] = (
    osd_meta[meta_id_col]
    .apply(lambda x: str(x).split('_')[0].strip().upper())
    .astype(str)
)


# 3. Extract OSD experimental factors
def find_col_by_kw(dataframe, kws):
  for col in dataframe.columns:
    if all(kw.lower() in col.lower() for kw in kws):
      return col
  return None


col_unloading = find_col_by_kw(osd_meta, ['unloading'])
col_radiation = find_col_by_kw(osd_meta, ['radiation'])
col_housing = find_col_by_kw(osd_meta, ['housing'])

meta_cols_subset = ['Join_ID']
rename_dict = {'Join_ID': 'Join_ID'}
if col_unloading:
  meta_cols_subset.append(col_unloading)
  rename_dict[col_unloading] = 'Hindlimb_Unloading'
if col_radiation:
  meta_cols_subset.append(col_radiation)
  rename_dict[col_radiation] = 'Ionizing_Radiation'
if col_housing:
  meta_cols_subset.append(col_housing)
  rename_dict[col_housing] = 'Housing_Condition'

osd_subset = osd_meta[meta_cols_subset].rename(columns=rename_dict)
osd_subset = osd_subset.drop_duplicates(subset=['Join_ID'])
df = pd.merge(df, osd_subset, left_on='Animal_ID', right_on='Join_ID', how='left')

# 4. Clean treatment columns
for col in ['Hindlimb_Unloading', 'Ionizing_Radiation', 'Housing_Condition']:
  df[col] = (
      df[col].fillna('Not Specified').astype(str).str.strip()
      if col in df.columns
      else 'Not Specified'
  )

if 'Join_ID' in df.columns:
  df = df.drop(columns=['Join_ID'])

# 5. Impute missing numeric values
metadata_cols = [
    'Animal_ID',
    'Age_Timepoint',
    'Treatment_Group',
    'Sex',
    'Batch',
    'Hindlimb_Unloading',
    'Ionizing_Radiation',
    'Housing_Condition',
]
numeric_cols = [
    col
    for col in df.select_dtypes(include=[np.number]).columns
    if col not in metadata_cols
]

df = df.dropna(subset=numeric_cols, how='all')
df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

# 6. Sign-Guaranteed PCA Stress Score (Higher Errors & Duration = Higher Stress)
scaler = StandardScaler()
scaled_df = pd.DataFrame(
    scaler.fit_transform(df[numeric_cols]),
    columns=numeric_cols,
    index=df.index,
)

# Invert velocity so slower swim speed aligns with impairment if needed,
# while keeping Errors and Duration positive
for col in numeric_cols:
  if 'velocity' in col.lower():
    scaled_df[col] = -scaled_df[col]

pca = PCA(n_components=1)
pca_score = pca.fit_transform(scaled_df)[:, 0]

error_cols = [c for c in numeric_cols if 'error' in c.lower()]
if np.corrcoef(pca_score, scaled_df[error_cols].mean(axis=1))[0, 1] < 0:
  pca_score = -pca_score

df['RAWM_Stress_Score'] = pca_score

# 7. Export clean master file
df.to_csv('osd_618_rawm_cleaned_master.csv', index=False)
print('Successfully regenerated osd_618_rawm_cleaned_master.csv!')