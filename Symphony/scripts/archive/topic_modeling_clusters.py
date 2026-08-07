import re
from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.feature_extraction import _stop_words

BASE = Path(r"C:\Users\lee.booth\Documents\02_ServiceNow\Management_Reports")
RAW = BASE / 'Symphony' / 'raw'
REPORTS = BASE / 'Symphony' / 'reports'
CSV = RAW / 'Symphony_Cases_With_SLA_Last_12-Months.csv'
REPORTS.mkdir(parents=True, exist_ok=True)

if not CSV.exists():
    raise SystemExit(f"CSV not found: {CSV}")

df = pd.read_csv(CSV, dtype=str)
df.columns = [c.strip() for c in df.columns]
if 'product' in df.columns:
    df = df[df['product'].fillna('').str.strip().str.lower()=='symphony']
if 'u_problem' in df.columns:
    df = df[df['u_problem'].isna() | (df['u_problem'].str.strip()=='')]

texts = df.get('short_description','').fillna('').astype(str)
# basic clean
texts_clean = texts.str.replace('\n',' ').str.replace('\r',' ').str.lower()
texts_clean = texts_clean.str.replace(r"[^a-z0-9\s]", ' ', regex=True)
texts_clean = texts_clean.str.replace(r"\s+", ' ', regex=True).str.strip()

# stopwords: sklearn built-in + custom
custom = set(['symphony','symptom','sym','issue','issues','case','cases','please','thanks','thank','test','testing','error','problem'])
stop = list(_stop_words.ENGLISH_STOP_WORDS.union(custom))

# TF-IDF with unigrams and bigrams
vec = TfidfVectorizer(stop_words=stop, ngram_range=(1,2), max_features=5000)
X = vec.fit_transform(texts_clean)

# choose number of clusters
n_clusters = 8
km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
labels = km.fit_predict(X)

# top terms per cluster
terms = vec.get_feature_names_out()
order_centroids = km.cluster_centers_.argsort()[:, ::-1]
cluster_terms = {}
for i in range(n_clusters):
    top_terms = [terms[ind] for ind in order_centroids[i, :15]]
    cluster_terms[i] = top_terms

# attach labels and save sample rows
df_out = df.copy()
df_out['topic_cluster'] = labels
out_csv = REPORTS / 'symphony_topic_clusters.csv'
df_out.to_csv(out_csv, index=False)

# write summary
summary = REPORTS / 'symphony_topic_summary.txt'
with open(summary, 'w', encoding='utf-8') as f:
    f.write('TF-IDF + KMeans topic modeling summary\n')
    f.write(f'Input rows: {len(df)}\n')
    f.write(f'Clusters: {n_clusters}\n\n')
    for i in range(n_clusters):
        f.write(f'Cluster {i}: top terms: {", ".join(cluster_terms[i][:10])}\n')
        # sample descriptions
        samples = df_out[df_out['topic_cluster']==i].get('short_description','').dropna().head(6).tolist()
        for s in samples:
            f.write(f' - {s}\n')
        f.write('\n')

print('Saved:', out_csv)
print('Summary:', summary)
