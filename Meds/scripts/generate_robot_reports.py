import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(r"C:/Users/lee.booth/Documents/02_ServiceNow/Management_Reports/Meds")
CLASS_CSV = BASE / r"data/raw/report_outputs/trend_classification.csv"
ORIG_CSV = BASE / r"data/raw/Meds_Cases_Last_12-Months.csv"
OUT_DIR = BASE / r"data/raw/report_outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)
ROBOT_CSV = OUT_DIR / "robot_cases.csv"
MONTHLY_CSV = OUT_DIR / "robot_monthly_counts.csv"
PLOT_PNG = OUT_DIR / "robot_trend_monthly.png"

print('Reading classification CSV:', CLASS_CSV)
classif = pd.read_csv(CLASS_CSV)
# filter robot rows
robot_rows = classif[(classif['Trend Category']== 'Integration & Interfaces') & (classif['Sub-Category']== 'Third-Party Systems')]
print('Robot rows found:', len(robot_rows))

print('Reading original cases CSV (cp1252 encoding):', ORIG_CSV)
orig = pd.read_csv(ORIG_CSV, encoding='cp1252', low_memory=False)
# merge to bring in dates and other fields
merged = pd.merge(robot_rows, orig, left_on='Case Number', right_on='number', how='left', suffixes=('_class', '_orig'))
# write robot_cases CSV
merged.to_csv(ROBOT_CSV, index=False, encoding='utf-8')
print('Wrote robot cases:', ROBOT_CSV)

# parse date column - try common column names
date_col = None
for c in ['sys_created_on', 'created', 'Created', 'sys_created_on']:
    if c in merged.columns:
        date_col = c
        break

if date_col is None:
    print('No sys_created_on column found; attempting to use sys_updated_on or resolved_at')
    for c in ['sys_updated_on','resolved_at','Resolved_at']:
        if c in merged.columns:
            date_col = c
            break

if date_col is None:
    print('No date column available; generating monthly counts from classification only (count per file order)')
    monthly = robot_rows.groupby(robot_rows.index // 1).size().rename('count').reset_index()
    monthly.to_csv(MONTHLY_CSV, index=False)
else:
    print('Using date column:', date_col)
    # parse dates (day-first)
    merged['created_dt'] = pd.to_datetime(merged[date_col], dayfirst=True, errors='coerce')
    merged['month'] = merged['created_dt'].dt.to_period('M').dt.to_timestamp()
    monthly = merged.groupby('month').size().rename('count').reset_index()
    monthly.to_csv(MONTHLY_CSV, index=False)
    # plot
    if not monthly.empty:
        plt.figure(figsize=(8,4))
        plt.plot(monthly['month'], monthly['count'], marker='o')
        plt.title('Robot-related cases — monthly trend')
        plt.xlabel('Month')
        plt.ylabel('Number of robot cases')
        plt.grid(True, linestyle='--', alpha=0.4)
        plt.tight_layout()
        plt.savefig(PLOT_PNG)
        print('Wrote plot:', PLOT_PNG)
    else:
        print('No monthly data to plot')

print('Done')
