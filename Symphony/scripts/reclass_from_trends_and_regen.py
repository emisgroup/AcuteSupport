import pandas as pd
import os
import re

# Base directories (dynamic)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
merged = os.path.join(RAW_DIR, 'Merged_Cases_With_SLA_Formatted.csv')
trends_path = os.path.join(BASE_DIR, 'templates', 'Trends.txt')
out_dir = os.path.join(RAW_DIR, 'report_outputs')
backup = os.path.join(RAW_DIR, 'Merged_Cases_With_SLA_Formatted_backup_before_reclass_from_trends.csv')
merged = os.path.join(base, 'Merged_Cases_With_SLA_Formatted.csv')
trends_path = r'C:\Users\lee.booth\Documents\02_ServiceNow\Management_Reports\Symphony\templates\Trends.txt'
out_dir = os.path.join(base, 'report_outputs')
backup = os.path.join(base, 'Merged_Cases_With_SLA_Formatted_backup_before_reclass_from_trends.csv')

print('Reading', merged)
df = pd.read_csv(merged, encoding='utf-8')

# load trends
trend_tokens = []
if os.path.exists(trends_path):
    with open(trends_path,'r',encoding='utf-8') as f:
        for line in f:
            t = line.strip()
            if not t:
                continue
            parts = re.split('[/,]', t)
            tokens = [p.strip() for p in parts if p.strip()]
            trend_tokens.append((t, tokens))

if not trend_tokens:
    print('No trends found in Trends.txt; aborting')
    raise SystemExit(1)

# classifier
def text_for_row(r):
    return (' '.join([str(r.get('short_description','') or ''), str(r.get('description','') or '')])).lower()

def classify_initial_row(text):
    for trend_name, tokens in trend_tokens:
        for tok in tokens:
            if tok.lower() in text:
                return trend_name
    return 'Other'

# backup
if os.path.exists(merged):
    pd.read_csv(merged, encoding='utf-8').to_csv(backup, index=False)
    print('Backup saved to', backup)

# apply classification
df['trend'] = df.apply(lambda r: classify_initial_row(text_for_row(r)), axis=1)

# save merged
df.to_csv(merged, index=False)
print('Wrote reclassified merged CSV to', merged)

# write preview
os.makedirs(out_dir, exist_ok=True)
preview = os.path.join(out_dir,'reclassification_after_templates.csv')
df.to_csv(preview, index=False)
print('Wrote preview to', preview)

# regenerate charts
print('Regenerating charts...')
os.system(f'python "{os.path.join(os.path.dirname(os.path.abspath(__file__)), "generate_report_charts.py")}"')
print('Done')
