import pandas as pd
import os
import re
from collections import Counter

# Base directories (dynamic)
BASE_DIR = os.getcwd()
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
ARCHIVE_DIR = os.path.join(BASE_DIR, 'data', 'archive')

merged = os.path.join(PROCESSED_DIR, 'Merged_Cases_With_SLA_Formatted.csv')
if not os.path.exists(merged):
    merged = os.path.join(RAW_DIR, 'Merged_Cases_With_SLA_Formatted.csv')

out_tables = os.path.join(BASE_DIR, 'outputs', 'tables')
out_charts = os.path.join(BASE_DIR, 'outputs', 'charts')
os.makedirs(out_tables, exist_ok=True)
os.makedirs(out_charts, exist_ok=True)

backup = os.path.join(ARCHIVE_DIR, 'Merged_Cases_With_SLA_Formatted_backup_before_new_trends.csv')
trends_path = os.path.join(BASE_DIR, 'templates', 'Trends.txt')

print('Reading', merged)
df = pd.read_csv(merged, encoding='utf-8')

# Load existing trends
# trends_path defined above (templates/Trends.txt)
trends_list = []
if os.path.exists(trends_path):
    with open(trends_path,'r',encoding='utf-8') as tf:
        for line in tf:
            t = line.strip()
            if t:
                trends_list.append(t)

# Build tokens
trend_tokens = []
for t in trends_list:
    parts = re.split('[/,]', t)
    tokens = [p.strip() for p in parts if p.strip()]
    trend_tokens.append((t, tokens))

# Initial classification
def classify_initial_row(text):
    for trend_name, tokens in trend_tokens:
        for tok in tokens:
            if tok.lower() in text:
                return trend_name
    return 'Other'

# Prepare text column
def text_for_row(r):
    return (' '.join([str(r.get('short_description','') or ''), str(r.get('description','') or '')])).lower()

if 'trend' not in df.columns:
    df['trend'] = df.apply(lambda r: classify_initial_row(text_for_row(r)), axis=1)
else:
    # ensure trend values exist; for safety, re-classify any blank/NaN
    df['trend'] = df['trend'].fillna('')
    df.loc[df['trend']=='', 'trend'] = df[df['trend']==''].apply(lambda r: classify_initial_row(text_for_row(r)), axis=1)

before_other = df['trend'].value_counts().get('Other', 0)
print('Other before:', before_other)

# Existing keyword pass (expanded) - reuse similar mapping
existing_mapping = {
    'Audit / IG / access investigation': ['audit','access request','access','subject access','audit trail','subject access request','sas','access rights','access permissions','permissions'],
    'DAD / HL7 / interface messaging': ['dad','hl7','interface','message','tie','t ie','integration','interface messaging','mf n','mfn','mfn message','mfn messages','mfn messages','t ie','gp connect','gpconnect','mf n'],
    'Performance / outage / errors': ['slow','performance','outage','error','failed','suspended','suspend','timeout','latency','blank page','not working','not working','stopped'],
    'Clinical workflow / DEP / clinic / BRM': ['dep','clinic','appointment','clinic','sdec','workflow','brm','booking','virtual physio','majax','majax'],
    'Data / SQL / configuration': ['sql','configuration','config','data','table','column','export','csv','database','query','config','import','master file','masterfile'],
    'Location / department / lookup changes': ['location','department','lookup','ward','site','hospital','department'],
    'Login / access / permissions': ['login','log in','sign in','credentials','password','auth','authenticate','permission','permissions','role'],
    'Printing / documents / output': ['print','printing','batch printing','documents','pdf','printer','print job'],
    'Reporting / SSRS / dashboards': ['report','reports','ssrs','dashboard','reporting'],
    'Appointments / scheduling': ['appointment','scheduling','book','booking','clinic booking']
}

for idx,row in df[df['trend']=='Other'].iterrows():
    text = text_for_row(row)
    assigned = None
    for trend, kws in existing_mapping.items():
        for kw in kws:
            if kw.lower() in text:
                assigned = trend
                break
        if assigned:
            df.at[idx,'trend'] = assigned
            break

after_expanded = df['trend'].value_counts().get('Other', 0)
print('Other after expanded mapping:', after_expanded)

# New trends to add (user approved recommendations)
new_trend_map = {
    'Environment / Deployment / Test': ['symphony test','symphony test','dev test','test train','dev test','dev','deploy','deployment','environment','dev test','test','into live','test train','dev'],
    'Master File / Import': ['master file','update master','update master file','masterfile','master','master import','masterdata','master file update','update master file','master update','import','import file','file import'],
    'ODS / TRUD updates': ['ods update','trud','ods','new trud','trud update','trud updates']
}

reclassified_count = 0
for idx,row in df[df['trend']=='Other'].iterrows():
    text = text_for_row(row)
    for trend, kws in new_trend_map.items():
        for kw in kws:
            if kw.lower() in text:
                df.at[idx,'trend'] = trend
                reclassified_count += 1
                break
        if df.at[idx,'trend'] != 'Other':
            break

after_new = df['trend'].value_counts().get('Other', 0)
print('Reclassified with new trends:', reclassified_count)
print('Other remaining:', after_new)

# Save backup and overwrite merged file
if os.path.exists(merged):
    print('Saving backup to', backup)
    pd.read_csv(merged, encoding='utf-8').to_csv(backup, index=False)

print('Overwriting merged file with new trend column')
df.to_csv(merged, index=False)

# Write summary and preview
os.makedirs(out_tables, exist_ok=True)
sum_path = os.path.join(out_tables,'reclassification_summary.txt')
with open(sum_path,'w',encoding='utf-8') as sf:
    sf.write(f'Other before: {before_other}\n')
    sf.write(f'Other after expanded mapping: {after_expanded}\n')
    sf.write(f'Reclassified with new trends: {reclassified_count}\n')
    sf.write(f'Other remaining: {after_new}\n')

preview_path = os.path.join(out_tables,'reclassification_preview_after.csv')
df.to_csv(preview_path, index=False)
print('Wrote preview to', preview_path)
print('Wrote summary to', sum_path)

print('Done')
