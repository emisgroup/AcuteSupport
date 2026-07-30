import pandas as pd
from pathlib import Path
import math

BASE = Path(r"C:/Users/lee.booth/Documents/02_ServiceNow/Management_Reports/Meds")
RAW = BASE / "data/raw"
OUT_DIR = RAW / "report_outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

robot_csv = RAW / "Meds_Robot_Cases_Last_12-Months.csv"
merge_csv = RAW / "Meds_Merge_Cases_Last_12-Months.csv"
lock_csv = RAW / "Meds_Lock_Cases_Last_12-Months.csv"
sla_csv = RAW / "Meds_SLA_Last_12-Months.csv"

out_xlsx = OUT_DIR / "trend_lists_with_sla.xlsx"

def read_csv(path):
    return pd.read_csv(path, encoding='cp1252', low_memory=False)

def format_seconds(sec):
    # sec may be NaN or missing
    try:
        if pd.isna(sec) or sec == '':
            return ''
        s = int(float(sec))
    except Exception:
        return ''
    days, rem = divmod(s, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, _ = divmod(rem, 60)
    parts = []
    if days:
        parts.append(f"{days} days")
    if hours:
        parts.append(f"{hours} hrs")
    if minutes:
        parts.append(f"{minutes} mins")
    if not parts:
        return '0 mins'
    return ', '.join(parts)

# load SLA
sla = read_csv(sla_csv)
# normalize task column name
if 'task' not in sla.columns:
    sla = sla.rename(columns={sla.columns[0]: 'task'})
sla.set_index('task', inplace=False)

# define sheets
sheets = [
    ('Robots', robot_csv),
    ('Merges', merge_csv),
    ('Locks', lock_csv)
]

writer = pd.ExcelWriter(out_xlsx, engine='openpyxl')

for sheet_name, path in sheets:
    if not path.exists():
        print(f"Warning: {path} not found, skipping {sheet_name}")
        continue
    df = read_csv(path)
    # add Trend column at front
    df.insert(0, 'Trend', sheet_name)
    # ensure case number column named 'number'
    num_col = None
    for c in ['number','Number','case_number']:
        if c in df.columns:
            num_col = c
            break
    if num_col is None:
        # if no number column, create an index-based id
        df.insert(1, 'Case Number', df.index.map(lambda i: f'Row {i+1}'))
        num_col = 'Case Number'
    # merge SLA
    sla_df = read_csv(sla_csv)
    sla_df.rename(columns={sla_df.columns[0]:'task'}, inplace=True)
    # keep business_duration and duration columns if present
    for col in ['business_duration','duration','start_time','end_time']:
        if col not in sla_df.columns:
            # try common variants
            if col.upper() in sla_df.columns:
                sla_df.rename(columns={col.upper():col}, inplace=True)
    merged = pd.merge(df, sla_df, left_on=num_col, right_on='task', how='left', suffixes=('','_sla'))
    # compute formatted SLA fields
    merged['SLA_Business_Seconds'] = merged.get('business_duration')
    merged['SLA_Duration_Seconds'] = merged.get('duration')
    merged['SLA_Business_Formatted'] = merged['SLA_Business_Seconds'].apply(format_seconds)
    merged['SLA_Duration_Formatted'] = merged['SLA_Duration_Seconds'].apply(format_seconds)
    # compute TTR: resolved_at - sys_created_on
    def parse_dt(x):
        try:
            return pd.to_datetime(x, dayfirst=True, errors='coerce')
        except Exception:
            return pd.NaT
    if 'sys_created_on' in merged.columns and 'resolved_at' in merged.columns:
        merged['created_dt'] = merged['sys_created_on'].apply(parse_dt)
        merged['resolved_dt'] = merged['resolved_at'].apply(parse_dt)
        merged['TTR_Seconds'] = (merged['resolved_dt'] - merged['created_dt']).dt.total_seconds()
        merged['TTR_Formatted'] = merged['TTR_Seconds'].apply(lambda s: format_seconds(s) if not pd.isna(s) else '')
    else:
        merged['TTR_Seconds'] = ''
        merged['TTR_Formatted'] = ''
    # write sheet and csv backup
    merged.to_excel(writer, sheet_name=sheet_name, index=False)
    merged.to_csv(OUT_DIR / f"{sheet_name.lower()}_with_sla.csv", index=False, encoding='utf-8')
    print(f"Wrote sheet and csv for {sheet_name}")

writer.close()
print('Workbook written to', out_xlsx)
