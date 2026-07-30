import re
from collections import Counter
from pathlib import Path
import pandas as pd

CSV = Path(r"C:\Users\lee.booth\Documents\02_ServiceNow\Management_Reports\Symphony\raw\Symphony_Cases_With_SLA_Last_12-Months.csv")
if not CSV.exists():
    print('CSV not found:', CSV)
    raise SystemExit(1)

df = pd.read_csv(CSV, dtype=str)
df.columns = [c.strip() for c in df.columns]
if 'product' in df.columns:
    df = df[df['product'].fillna('').str.strip().str.lower()=='symphony']
if 'u_problem' in df.columns:
    df = df[df['u_problem'].isna() | (df['u_problem'].str.strip()=='')]

df['short_clean'] = df.get('short_description','').fillna('').astype(str).str.replace('\n',' ').str.replace('\r',' ').str.strip()

STOPWORDS = set(["the","and","to","a","of","in","is","for","on","with","by","an","be","this","that","are","as","it","from","at","or","has","have"])

patt = re.compile(r"\w+")
all_tokens = []
for s in df['short_clean']:
    toks = patt.findall(str(s).lower())
    toks = [t for t in toks if len(t)>2]
    all_tokens.extend(toks)

counter = Counter(all_tokens)
print('\nTop 30 raw tokens (no stopword filtering):')
for t,c in counter.most_common(30):
    print(f'{t}: {c}')

# show tokens after current STOPWORDS filtering
filtered = [t for t in all_tokens if t not in STOPWORDS]
fctr = Counter(filtered)
print('\nTop 30 tokens after current stopword filter:')
for t,c in fctr.most_common(30):
    print(f'{t}: {c}')

# Check specific tokens
targets = ['not','unable','test']
for tok in targets:
    print(f"\nSamples for token '{tok}':")
    mask = df['short_clean'].str.lower().str.contains(rf"\b{re.escape(tok)}\b", na=False)
    samples = df[mask]['short_clean'].head(8).tolist()
    if not samples:
        print('  (no samples)')
    else:
        for s in samples:
            print(' -', s)

print('\nNotes: tokens like "not" or "unable" are single words indicating negation or status; they are frequent because they appear commonly in issue descriptions. Consider adding them to stopwords or using phrase extraction (bigrams) to capture meaningful phrases like "not printing" or "unable to login".')
