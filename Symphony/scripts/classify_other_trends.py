import pandas as pd
import os
import re
from collections import Counter

# Base directories (dynamic)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
merged = os.path.join(RAW_DIR, 'Merged_Cases_With_SLA_Formatted.csv')
out_dir = os.path.join(RAW_DIR, 'report_outputs')
os.makedirs(out_dir, exist_ok=True)

trends_path = os.path.join(BASE_DIR, 'templates', 'Trends.txt')

df = pd.read_csv(merged, encoding='utf-8')

# Build initial trend classification from templates (if available)
trends_list = []
trends_path = r'C:\Users\lee.booth\Documents\02_ServiceNow\Management_Reports\Symphony\templates\Trends.txt'
if os.path.exists(trends_path):
    with open(trends_path,'r',encoding='utf-8') as tf:
        for line in tf:
            t = line.strip()
            if t:
                trends_list.append(t)

# make a basic token list from trends
trend_tokens = []
for t in trends_list:
    parts = re.split('[/,]', t)
    tokens = [p.strip() for p in parts if p.strip()]
    trend_tokens.append((t, tokens))

# classify using simple substring match
def classify_initial(row):
    text = (' '.join([str(row.get('short_description','') or ''), str(row.get('description','') or '')])).lower()
    for trend_name, tokens in trend_tokens:
        for tok in tokens:
            if tok.lower() in text:
                return trend_name
    return 'Other'

if len(trend_tokens)>0:
    df['trend'] = df.apply(classify_initial, axis=1)
else:
    df['trend'] = 'Other'

other_df = df[df['trend'] == 'Other']
print(f"Other count: {len(other_df)}")

# show samples
samples = other_df.head(10)[['number','short_description','description']].fillna('')
print('\nSample Other rows (first 10):')
for idx,row in samples.iterrows():
    desc = row['short_description'] + ' ' + (row['description'][:200] if pd.notna(row['description']) else '')
    print(str(row['number']) + ' -> ' + re.sub(r'\s+',' ', desc.replace('\n',' '))[:300])

# Expanded keyword mapping to existing trend names
mapping = {
    'Audit / IG / access investigation': ['audit','access request','access','subject access','audit trail','subject access request','sas','access rights','access permissions','permissions'],
    'DAD / HL7 / interface messaging': ['dad','hl7','interface','message','t ie','tie','interface','integration','mbus','madx','dcp','ti e','dae','adt^a31','ad t','hanl','midas'],
    'Performance / outage / errors': ['slow','performance','outage','error','failed','suspended','suspend','timeout','latency'],
    'Clinical workflow / DEP / clinic / BRM': ['dep','clinic','appointment','clinic','sdec','workflow','brm','booking','virtual physio','majax','midax','ma jax'],
    'Data / SQL / configuration': ['sql','configuration','config','data','table','column','export','csv','database','query','config'],
    'Location / department / lookup changes': ['location','department','lookup','ward','site','hospital','department'],
    'Login / access / permissions': ['login','log in','sign in','credentials','password','auth','authenticate','permission','permissions','role'],
    'Printing / documents / output': ['print','printing','batch printing','documents','pdf','printing','printer','print job'],
    'Reporting / SSRS / dashboards': ['report','reports','ssrs','dashboard','reporting'],
    'Appointments / scheduling': ['appointment','scheduling','book','booking','clinic booking']
}

# Prepare text
def text_for_row(r):
    return (' '.join([str(r.get('short_description','') or ''), str(r.get('description','') or '')])).lower()

reclassified = {}
for i,row in other_df.iterrows():
    text = text_for_row(row)
    matched = None
    for trend, keywords in mapping.items():
        for kw in keywords:
            if kw.lower() in text:
                matched = trend
                break
        if matched:
            reclassified[i] = matched
            break

print('\nAuto-reclassified count:', len(reclassified))

# Apply reclassification to a copy
df2 = df.copy()
for idx,trend in reclassified.items():
    df2.at[idx,'trend_auto'] = trend

# Remaining others
remaining = df2[(df2['trend']=='Other') & (df2['trend_auto'].isnull())]
print('Remaining unclassified after keyword pass:', len(remaining))

# Propose candidate new trends by common tokens in remaining
# simple tokenisation and stopword removal
stop = set(['the','and','is','in','to','a','of','for','with','on','please','we','can','our','are','from','not','they','this','that','or','it','be'])
word_counter = Counter()
bigram_counter = Counter()
for idx,row in remaining.iterrows():
    text = text_for_row(row)
    # remove non-word
    tokens = re.findall(r"[a-z]{3,}", text)
    tokens = [t for t in tokens if t not in stop]
    word_counter.update(tokens)
    # bigrams
    for i in range(len(tokens)-1):
        bigram_counter.update([tokens[i] + ' ' + tokens[i+1]])

common_words = word_counter.most_common(30)
common_bigrams = bigram_counter.most_common(30)

print('\nTop words in remaining Other items:')
for w,c in common_words[:15]:
    print(f"{w}: {c}")

print('\nTop bigrams:')
for w,c in common_bigrams[:15]:
    print(f"{w}: {c}")

# Write preview CSV with auto suggestions
preview_path = os.path.join(out_dir,'reclassification_preview.csv')
cols = list(df2.columns) + ['trend_auto'] if 'trend_auto' in df2.columns else list(df2.columns)
df2.to_csv(preview_path, index=False)

print('\nWrote preview to', preview_path)
print('\nProposed new trend candidates (based on frequent tokens / bigrams):')
# propose top bigrams as candidate trend names (first 5)
proposals = [b for b,c in common_bigrams[:8]]
for p in proposals:
    print('-', p)

print('\nNext: confirm which candidate(s) to accept as new trend names, or request further tuning (e.g., regex, fuzzy matching, manual labelling).')
