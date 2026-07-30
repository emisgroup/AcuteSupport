"""
Run the full Symphony management report pipeline.

Steps executed (in order):
 1) Merge case and SLA CSVs into data/raw/Merged_Cases_With_SLA_Formatted.csv
 2) Generate KPI tables and charts
 3) Classify 'Other' trends (inspect)
 4) Apply authorised new trends (if any) and regenerate
 5) Export charts into DOCX
 6) Fill remaining DOCX placeholders
 7) Populate tables in DOCX
 8) Finalise metrics, executive summary, recommended actions, appendix

Run from repository root: python scripts\run_full_report.py
"""
import os
import subprocess
import sys
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')

CASE_CSV = os.path.join(RAW_DIR, 'Symphony_Casea_Last_12-Months.csv')
SLA_CSV = os.path.join(RAW_DIR, 'Symphony_SLA_Last_12-Months.csv')
MERGED = os.path.join(RAW_DIR, 'Merged_Cases_With_SLA_Formatted.csv')
OUT_DIR = os.path.join(RAW_DIR, 'report_outputs')
os.makedirs(OUT_DIR, exist_ok=True)

PY = sys.executable

def format_duration_from_seconds(s):
    try:
        s = int(float(s))
    except Exception:
        return ''
    if s<=0:
        return ''
    mins = s//60
    days = mins // (24*60)
    mins_rem = mins - days*24*60
    hours = mins_rem // 60
    minutes = mins_rem - hours*60
    parts = []
    if days>0:
        parts.append(f"{days} days")
    if hours>0:
        parts.append(f"{hours} hrs")
    if minutes>0:
        parts.append(f"{minutes} mins")
    return ', '.join(parts)


def merge_and_format():
    print('Merging case and SLA CSVs...')
    if not os.path.exists(CASE_CSV):
        raise SystemExit(f'Cases CSV missing: {CASE_CSV}')
    if not os.path.exists(SLA_CSV):
        raise SystemExit(f'SLA CSV missing: {SLA_CSV}')
    def read_csv_with_fallback(path):
        # Try common encodings: utf-8, cp1252 (windows-1252), latin-1
        for enc in ('utf-8', 'cp1252', 'latin-1'):
            try:
                return pd.read_csv(path, encoding=enc, low_memory=False)
            except UnicodeDecodeError:
                print(f"Encoding {enc} failed for {os.path.basename(path)}; trying next encoding...")
            except Exception as e:
                # Non-encoding related error - re-raise
                raise
        # Last resort: read with latin-1 and replace invalid bytes
        print(f"All encoding attempts failed for {path}; reading with latin-1 permissive mode.")
        return pd.read_csv(path, encoding='latin-1', low_memory=False)

    cases = read_csv_with_fallback(CASE_CSV)
    sla = read_csv_with_fallback(SLA_CSV)
    # normalize column names
    cases_cols = [c.strip() for c in cases.columns]
    cases.columns = cases_cols
    sla_cols = [c.strip() for c in sla.columns]
    sla.columns = sla_cols
    # expected keys
    # cases: number
    # sla: task, business_duration, duration
    if 'number' not in cases.columns:
        # try common alternatives
        for alt in ['Number','case_number','Case Number']:
            if alt in cases.columns:
                cases['number'] = cases[alt]
                break
    if 'task' not in sla.columns:
        for alt in ['task','Task','case_number','Number']:
            if alt in sla.columns:
                sla['task'] = sla[alt]
                break
    # map durations
    bcol = None
    dcol = None
    for cand in ['business_duration','SLA_Business_Time','businessDuration','business_duration_seconds','business_duration_sec']:
        if cand in sla.columns:
            bcol = cand; break
    for cand in ['duration','SLA_Duration','duration_seconds','actual_duration']:
        if cand in sla.columns:
            dcol = cand; break
    if bcol is None:
        print('Warning: business duration column not found in SLA CSV; leaving blank')
    if dcol is None:
        print('Warning: duration column not found in SLA CSV; leaving blank')

    # prepare lookup
    sla_lookup = {}
    for _, row in sla.iterrows():
        key = str(row.get('task','')).strip()
        sla_lookup[key] = row
    # left join by iterating to preserve order
    merged_rows = []
    for _, r in cases.iterrows():
        key = str(r.get('number','')).strip()
        s = sla_lookup.get(key)
        new = r.copy()
        if s is not None:
            new['SLA_task'] = s.get('task','')
            new['SLA_Business_Time_seconds'] = s.get(bcol, '') if bcol else ''
            new['SLA_Duration_seconds'] = s.get(dcol, '') if dcol else ''
        else:
            new['SLA_task'] = ''
            new['SLA_Business_Time_seconds'] = ''
            new['SLA_Duration_seconds'] = ''
        # add formatted fields
        new['SLA_Business_Time'] = format_duration_from_seconds(new['SLA_Business_Time_seconds'])
        new['SLA_Duration'] = format_duration_from_seconds(new['SLA_Duration_seconds'])
        merged_rows.append(new)
    merged_df = pd.DataFrame(merged_rows)
    # backup existing
    if os.path.exists(MERGED):
        ts = datetime.now().strftime('%Y%m%d%H%M%S')
        bak = MERGED.replace('.csv', f'_backup_{ts}.csv')
        print('Backing up existing merged to', bak)
        os.rename(MERGED, bak)
    merged_df.to_csv(MERGED, index=False)
    print('Wrote merged file:', MERGED)


def run_script(script_rel):
    script = os.path.join(SCRIPTS_DIR, script_rel)
    if not os.path.exists(script):
        print('Skipping missing script', script)
        return True
    print('\n--- Running', script_rel, '---')
    proc = subprocess.run([PY, script], cwd=BASE_DIR)
    if proc.returncode != 0:
        print('Script failed:', script_rel)
        return False
    return True


def main():
    merge_and_format()
    sequence = [
        'generate_report_charts.py',
        'classify_other_trends.py',
        'apply_new_trends_and_regenerate.py',
        'export_charts_to_docx.py',
        'fill_remaining_docx_placeholders.py',
        'fill_tables_advanced.py',
        'fill_metrics_and_finalize_report.py'
    ]
    for s in sequence:
        ok = run_script(s)
        if not ok:
            print('Pipeline halted at', s)
            sys.exit(1)
    print('\nPipeline completed. Final report at:', os.path.join(OUT_DIR, 'Cases_Management_Report_Completed_tables_filled_final.docx'))

if __name__ == '__main__':
    main()
