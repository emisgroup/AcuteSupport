import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from datetime import datetime
import sys
from pathlib import Path
_base_dir = Path(__file__).resolve().parent.parent.parent
if str(_base_dir) not in sys.path:
    sys.path.insert(0, str(_base_dir))
from shared.utils.date_formatting import format_duration
from shared.utils.classification import apply_trend_classification

# Paths
# Base directories (dynamic)
BASE_DIR = os.getcwd()
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')

merged = os.path.join(PROCESSED_DIR, 'Merged_Cases_With_SLA_Formatted.csv')
if not os.path.exists(merged):
    merged = os.path.join(RAW_DIR, 'Merged_Cases_With_SLA_Formatted.csv')

trends_path = os.path.join(BASE_DIR, 'templates', 'Trends.txt')
out_tables = os.path.join(BASE_DIR, 'outputs', 'tables')
out_charts = os.path.join(BASE_DIR, 'outputs', 'charts')
os.makedirs(out_tables, exist_ok=True)
os.makedirs(out_charts, exist_ok=True)

# Read data
df = pd.read_csv(merged, encoding='utf-8')

# Parse dates (dayfirst=True)
for col in ['sys_created_on', 'resolved_at']:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')

# TTR in seconds where resolved_at present
if 'sys_created_on' in df.columns and 'resolved_at' in df.columns:
    df['TTR_seconds'] = (df['resolved_at'] - df['sys_created_on']).dt.total_seconds()
else:
    df['TTR_seconds'] = np.nan

# SLA seconds columns
for c in ['SLA_Business_Time_seconds','SLA_Duration_seconds']:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    else:
        df[c] = np.nan

# KPI calculations
total_cases = len(df)
closed_cases = df['state'].str.contains('Closed', na=False).sum() if 'state' in df.columns else 0
resolved_cases = df['resolved_at'].notna().sum()
open_cases = total_cases - closed_cases

# Priority counts (extract leading digit if present)
def extract_priority(x):
    try:
        if pd.isna(x):
            return 'Unknown'
        s = str(x)
        if '-' in s:
            return s.split('-')[0].strip()
        return s.strip()
    except:
        return 'Unknown'

if 'priority' in df.columns:
    df['priority_rank'] = df['priority'].apply(extract_priority)
    priority_counts = df['priority_rank'].value_counts().sort_index()
else:
    priority_counts = pd.Series()

# TTR metrics (for resolved only)
ttr_series = df.loc[df['TTR_seconds'].notna(), 'TTR_seconds']
median_ttr = np.nan
p90_ttr = np.nan
shortest_ttr = np.nan
longest_ttr = np.nan
if len(ttr_series)>0:
    median_ttr = np.nanmedian(ttr_series)
    p90_ttr = np.nanpercentile(ttr_series,90)
    shortest_ttr = np.nanmin(ttr_series)
    longest_ttr = np.nanmax(ttr_series)

# SLA averages
avg_sla_business = df['SLA_Business_Time_seconds'].dropna().mean()
avg_sla_duration = df['SLA_Duration_seconds'].dropna().mean()

# Monthly case trend
if 'sys_created_on' in df.columns:
    df['created_month'] = df['sys_created_on'].dt.to_period('M').astype(str)
    monthly = df.groupby('created_month').size().reset_index(name='cases')
else:
    monthly = pd.DataFrame(columns=['created_month','cases'])

# Product distribution
if 'product' in df.columns:
    product_dist = df['product'].fillna('Unknown').value_counts().reset_index()
    product_dist.columns = ['product','count']
else:
    product_dist = pd.DataFrame(columns=['product','count'])

# Trend classification using Trends.txt
df, trends, trend_keywords = apply_trend_classification(df, trends_path)
if trends:
    trend_dist = df['trend'].value_counts().reset_index()
    trend_dist.columns = ['trend','count']
    # Trend movement by month
    trend_movement = df.groupby(['created_month','trend']).size().reset_index(name='count')
    pivot_trend_movement = trend_movement.pivot(index='created_month', columns='trend', values='count').fillna(0)
else:
    trend_dist = pd.DataFrame(columns=['trend','count'])
    pivot_trend_movement = pd.DataFrame()



# Save KPI overview
kpi = {
    'total_cases': total_cases,
    'closed_cases': int(closed_cases),
    'open_cases': int(open_cases),
    'resolved_cases': int(resolved_cases),
    'median_ttr_seconds': float(median_ttr) if not np.isnan(median_ttr) else '',
    'p90_ttr_seconds': float(p90_ttr) if not np.isnan(p90_ttr) else '',
    'shortest_ttr_seconds': float(shortest_ttr) if not np.isnan(shortest_ttr) else '',
    'longest_ttr_seconds': float(longest_ttr) if not np.isnan(longest_ttr) else '',
    'median_ttr': format_duration(median_ttr) if not np.isnan(median_ttr) else '',
    'p90_ttr': format_duration(p90_ttr) if not np.isnan(p90_ttr) else '',
    'avg_sla_business_seconds': float(avg_sla_business) if not np.isnan(avg_sla_business) else '',
    'avg_sla_business': format_duration(avg_sla_business) if not np.isnan(avg_sla_business) else '',
    'avg_sla_duration_seconds': float(avg_sla_duration) if not np.isnan(avg_sla_duration) else '',
    'avg_sla_duration': format_duration(avg_sla_duration) if not np.isnan(avg_sla_duration) else ''
}

pd.DataFrame([kpi]).to_csv(os.path.join(out_tables,'kpi_overview.csv'), index=False)

# Save monthly, priority, product, trend tables
monthly.to_csv(os.path.join(out_tables,'monthly_case_trend.csv'), index=False)
priority_counts.to_csv(os.path.join(out_tables,'priority_profile.csv'), header=['count']) if not priority_counts.empty else pd.DataFrame().to_csv(os.path.join(out_tables,'priority_profile.csv'))
product_dist.to_csv(os.path.join(out_tables,'product_distribution.csv'), index=False)
trend_dist.to_csv(os.path.join(out_tables,'trend_distribution.csv'), index=False)
if not pivot_trend_movement.empty:
    pivot_trend_movement.to_csv(os.path.join(out_tables,'trend_movement.csv'))

# Generate charts
# Monthly case trend
plt.figure(figsize=(10,4))
plt.plot(monthly['created_month'], monthly['cases'], marker='o')
plt.xticks(rotation=45)
plt.title('Monthly Case Trend')
plt.tight_layout()
plt.savefig(os.path.join(out_charts,'monthly_case_trend.png'))
plt.close()

# Priority profile
if not priority_counts.empty:
    plt.figure(figsize=(6,4))
    priority_counts.sort_index().plot(kind='bar')
    plt.title('Priority Profile')
    plt.xlabel('Priority')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(os.path.join(out_charts,'priority_profile.png'))
    plt.close()

# Product distribution (top 10)
if not product_dist.empty:
    top_products = product_dist.head(10)
    plt.figure(figsize=(8,4))
    plt.bar(top_products['product'], top_products['count'])
    plt.xticks(rotation=45, ha='right')
    plt.title('Product Distribution (Top 10)')
    plt.tight_layout()
    plt.savefig(os.path.join(out_charts,'product_distribution.png'))
    plt.close()

# Trend distribution
if not trend_dist.empty:
    top_trends = trend_dist.head(15)
    plt.figure(figsize=(8,4))
    plt.bar(top_trends['trend'], top_trends['count'])
    plt.xticks(rotation=45, ha='right')
    plt.title('Trend Distribution')
    plt.tight_layout()
    plt.savefig(os.path.join(out_charts,'trend_distribution.png'))
    plt.close()

# Trend movement (stacked area)
if not pivot_trend_movement.empty:
    pivot_trend_movement.index = pivot_trend_movement.index.astype(str)
    pivot_trend_movement.plot(kind='area', stacked=True, figsize=(10,5))
    plt.xticks(rotation=45)
    plt.title('Trend Movement by Month')
    plt.tight_layout()
    plt.savefig(os.path.join(out_charts,'trend_movement.png'))
    plt.close()

# Median vs P90 TTR
plt.figure(figsize=(4,4))
metrics = ['Median TTR','P90 TTR']
vals = [median_ttr if not np.isnan(median_ttr) else 0, p90_ttr if not np.isnan(p90_ttr) else 0]
vals_minutes = [v/3600 if v else 0 for v in vals]
plt.bar(metrics, vals_minutes)
plt.title('Median vs P90 TTR (hours)')
plt.tight_layout()
plt.savefig(os.path.join(out_charts,'median_vs_p90.png'))
plt.close()

# SLA performance - average business vs average duration
plt.figure(figsize=(4,4))
sla_vals = [avg_sla_business if not np.isnan(avg_sla_business) else 0, avg_sla_duration if not np.isnan(avg_sla_duration) else 0]
sla_vals_hours = [v/3600 if v else 0 for v in sla_vals]
plt.bar(['Avg SLA Business Time','Avg SLA Duration'], sla_vals_hours)
plt.title('Average SLA (hours)')
plt.tight_layout()
plt.savefig(os.path.join(out_charts,'sla_performance.png'))
plt.close()

print('Tables written to', out_tables)
print('Charts written to', out_charts)
