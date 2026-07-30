from pathlib import Path
import pandas as pd
from docx import Document
from datetime import datetime
import re

BASE = Path(r"C:\Users\lee.booth\Documents\02_ServiceNow\Management_Reports")
SYM = BASE / 'Symphony'
RAW = SYM / 'raw'
REPORTS = SYM / 'reports'

# Find latest filled report
reports = sorted(REPORTS.glob('Symphony_Report_Filled_*.docx'), key=lambda p: p.stat().st_mtime, reverse=True)
if not reports:
    raise SystemExit('No filled report found')
IN_REPORT = reports[0]
OUT_REPORT = REPORTS / f"{IN_REPORT.stem}_clusters_replaced_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"

# Files
clusters_csv = REPORTS / 'symphony_topic_clusters.csv'
summary_txt = REPORTS / 'symphony_topic_summary.txt'

if not clusters_csv.exists() or not summary_txt.exists():
    raise SystemExit('Clusters CSV or summary missing in reports/')

# Load clusters
df = pd.read_csv(clusters_csv, dtype=str)
df.columns = [c.strip() for c in df.columns]
# ensure sys_created_on parsed
if 'sys_created_on' in df.columns:
    df['sys_created_on'] = pd.to_datetime(df['sys_created_on'], dayfirst=True, errors='coerce')

# Parse summary to get top terms per cluster
cluster_terms = {}
with open(summary_txt, 'r', encoding='utf-8') as f:
    for line in f:
        m = re.match(r'Cluster\s*(\d+):\s*top terms:\s*(.*)', line)
        if m:
            idx = int(m.group(1))
            terms = [t.strip() for t in m.group(2).split(',') if t.strip()]
            cluster_terms[idx] = terms

# Compute counts per cluster and recent signal (since June 1 current year)
counts = df['topic_cluster'].value_counts().to_dict()
now = datetime.now()
june1 = pd.Timestamp(year=now.year, month=6, day=1)
recent_counts = {}
for clus in sorted(cluster_terms.keys()):
    sub = df[df['topic_cluster'].astype(int)==clus]
    total = len(sub)
    if 'sys_created_on' in sub.columns:
        recent = sub[sub['sys_created_on'] >= june1]
        recent_counts[clus] = len(recent)
    else:
        recent_counts[clus] = ''

# Prepare management implication templates by keyword
def infer_implication(terms):
    tset = ' '.join(terms).lower()
    if 'dad' in tset or 'message' in tset or 'outbound' in tset:
        return 'Investigate DAD/queue health; automate queue monitoring; escalate to integration team.'
    if 'print' in tset or 'printing' in tset or 'report' in tset:
        return 'Review report generation and print service; provide KB for common fixes; check file permissions.'
    if 'access' in tset or 'audit' in tset or 'permission' in tset:
        return 'Review access controls and audit trails; simplify common access requests; clarify process.'
    if 'gp' in tset or 'ods' in tset or 'trud' in tset or 'connect' in tset:
        return 'Coordinate with GP/ODS teams; validate TRUD imports; schedule regular sync checks.'
    if 'unable' in tset or 'log' in tset or 'login' in tset:
        return 'Improve authentication reliability; add clear triage steps for login issues and test environments.'
    return 'Investigate root cause and create KB; prioritise automation for repeat issues.'

# Open report and replace table 8
doc = Document(IN_REPORT)
try:
    t8 = doc.tables[8]
except IndexError:
    raise SystemExit('Template structure changed: table 8 not found')

# Ensure enough rows: table has header row + N rows
header_rows = 1
needed = header_rows + len(cluster_terms)
while len(t8.rows) < needed:
    t8.add_row()

# Fill rows
for i, clus in enumerate(sorted(cluster_terms.keys()), start=1):
    row = t8.rows[i]
    terms = cluster_terms.get(clus, [])
    theme_label = f"Cluster {clus}: {terms[0]}" if terms else f"Cluster {clus}"
    row.cells[0].text = theme_label
    row.cells[1].text = str(counts.get(str(clus), counts.get(clus, 0)))
    row.cells[2].text = str(recent_counts.get(clus, ''))
    row.cells[3].text = infer_implication(terms)

# Clear any remaining old rows beyond used clusters (optional) - leave as is

# Save
doc.save(OUT_REPORT)
print('Updated report with clusters saved to:', OUT_REPORT)
