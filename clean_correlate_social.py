import re
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# 1. Load datasets
df = pd.read_csv(
    'LSDS-48_Three_Chamber_Social_Test_618_SOCIALAPPROACH_TRANSFORMED.csv'
)
data_dict = pd.read_excel(
    'LSDS-48_Three_Chamber_Social_Test_618_SOCIAL_APPROACH_SUBMITTED.xlsx'
)
osd_meta = pd.read_csv('s_OSD-618.txt', sep='\t')

print(f'Original behavioral shape: {df.shape}')
print(f'Metadata shape: {osd_meta.shape}')


# Helper function to find ID or metadata columns dynamically
def find_matching_column(dataframe, keywords):
  for col in dataframe.columns:
    if any(kw.lower() in col.lower() for kw in keywords):
      return col
  return dataframe.columns[0]


beh_id_col = find_matching_column(df, ['subject', 'sample', 'source', 'id'])
meta_id_col = find_matching_column(
    osd_meta, ['source name', 'sample name', 'subject', 'id']
)


# 2. Separate Animal ID and Age/Timepoint into two distinct columns
def parse_animal_id_and_age(val):
  val_str = str(val).strip()
  if '_' in val_str:
    parts = val_str.split('_', 1)
    return parts[0].strip().upper(), parts[1].strip().upper()
  else:
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


# 3. Dynamically extract OSD experimental factors
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

# 4. Apply Data Dictionary renaming for behavioral metrics
if 'Raw_Name' in data_dict.columns and 'Clean_Name' in data_dict.columns:
  mapping_dict = dict(zip(data_dict['Raw_Name'], data_dict['Clean_Name']))
else:
  mapping_dict = dict(zip(data_dict.iloc[:, 0], data_dict.iloc[:, 1]))
df = df.rename(columns=mapping_dict)

# 5. Clean treatment columns
for col in ['Hindlimb_Unloading', 'Ionizing_Radiation', 'Housing_Condition']:
  if col in df.columns:
    df[col] = df[col].fillna('Not Specified').astype(str).str.strip()
  else:
    df[col] = 'Not Specified'

if 'Join_ID' in df.columns:
  df = df.drop(columns=['Join_ID'])

# 6. Define metadata and numerical columns
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
metadata_cols = [c for c in metadata_cols if c in df.columns]

numeric_cols = [
    col
    for col in df.select_dtypes(include=[np.number]).columns
    if col not in metadata_cols
]

# 7. Impute missing numeric values
df = df.dropna(subset=numeric_cols, how='all')
df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

# 8. Direction-Corrected & Sign-Guaranteed PCA Stress Score
decreasing_stress_metrics = [
    c
    for c in numeric_cols
    if any(
        kw in c.lower()
        for kw in ['ratio', 'percent', 'sociability_ms', 'socialmemory_fm']
    )
]

scaler = StandardScaler()
scaled_array = scaler.fit_transform(df[numeric_cols])
scaled_df = pd.DataFrame(scaled_array, columns=numeric_cols, index=df.index)

for col in decreasing_stress_metrics:
  if col in scaled_df.columns:
    scaled_df[col] = -scaled_df[col]

pca = PCA(n_components=1)
pca_score = pca.fit_transform(scaled_df)[:, 0]

# Guarantee sign alignment: ensure positive correlation with impairment/distance metrics
temp_sum = scaled_df.mean(axis=1)
if np.corrcoef(pca_score, temp_sum)[0, 1] < 0:
  pca_score = -pca_score

df['Stress_Indicator_Score'] = pca_score

# 9. Compute Correlation Matrix
correlation_matrix = df[numeric_cols].corr(method='pearson')

# 10. Export Outputs
df.to_csv('osd_618_social_cleaned_master.csv', index=False)
correlation_matrix.to_csv('osd_618_social_correlation_matrix.csv')

print(
    'Successfully ran cleaning script with sign-corrected PCA Stress Score!'
)