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

BASE_DIR = os.getcwd()
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
ARCHIVE_DIR = os.path.join(BASE_DIR, 'data', 'archive')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')
OUT_TABLES = os.path.join(BASE_DIR, 'outputs', 'tables')
OUT_CHARTS = os.path.join(BASE_DIR, 'outputs', 'charts')
OUT_REPORTS = os.path.join(BASE_DIR, 'outputs', 'reports')

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)
os.makedirs(OUT_TABLES, exist_ok=True)
os.makedirs(OUT_CHARTS, exist_ok=True)
os.makedirs(OUT_REPORTS, exist_ok=True)

MERGED = os.path.join(PROCESSED_DIR, 'Merged_Cases_With_SLA_Formatted.csv')

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
    
    def read_csv_with_fallback(path):
        for enc in ('utf-8', 'cp1252', 'latin-1'):
            try:
                return pd.read_csv(path, encoding=enc, low_memory=False)
            except UnicodeDecodeError:
                pass
            except Exception:
                raise
        return pd.read_csv(path, encoding='latin-1', low_memory=False)

    # 1. Discover all active Case CSV files in RAW_DIR (ignoring subdirectories like IgnoredFiles/IgnoreFile)
    case_files = []
    for fname in sorted(os.listdir(RAW_DIR)):
        full_path = os.path.join(RAW_DIR, fname)
        if os.path.isdir(full_path):
            continue
        if fname.lower().endswith('.csv') and 'case' in fname.lower():
            case_files.append(full_path)

    if not case_files:
        raise SystemExit(f'No active case CSV files found in {RAW_DIR}')

    print(f"Ingesting case files in order: {[os.path.basename(f) for f in case_files]}")

    cases_dict = {}
    for cf in case_files:
        df = read_csv_with_fallback(cf)
        df.columns = [c.strip() for c in df.columns]
        num_col = None
        for cand in ['number', 'Number', 'case_number', 'Case Number']:
            if cand in df.columns:
                num_col = cand
                break
        if not num_col:
            continue

        for _, row in df.iterrows():
            key = str(row.get(num_col, '')).strip()
            if not key:
                continue
            r_dict = row.to_dict()
            r_dict['number'] = key
            if key not in cases_dict:
                cases_dict[key] = r_dict
            else:
                existing = cases_dict[key]
                for k, v in r_dict.items():
                    if pd.notna(v) and str(v).strip() != '':
                        existing[k] = v
                cases_dict[key] = existing

    cases_df = pd.DataFrame(list(cases_dict.values()))
    print(f"Total consolidated unique cases: {len(cases_df)}")

    # 2. Discover all active SLA CSV files in RAW_DIR (ignoring subdirectories like IgnoredFiles/IgnoreFile)
    sla_files = []
    for fname in sorted(os.listdir(RAW_DIR)):
        full_path = os.path.join(RAW_DIR, fname)
        if os.path.isdir(full_path):
            continue
        if fname.lower().endswith('.csv') and 'sla' in fname.lower():
            sla_files.append(full_path)

    print(f"Ingesting SLA files in order: {[os.path.basename(f) for f in sla_files]}")

    sla_dict = {}
    for sf in sla_files:

        df = read_csv_with_fallback(sf)
        df.columns = [c.strip() for c in df.columns]
        task_col = None
        for cand in ['task', 'Task', 'case_number', 'Number']:
            if cand in df.columns:
                task_col = cand
                break
        if not task_col:
            continue

        bcol = None
        dcol = None
        for cand in ['business_duration', 'SLA_Business_Time', 'businessDuration', 'business_duration_seconds']:
            if cand in df.columns:
                bcol = cand
                break
        for cand in ['duration', 'SLA_Duration', 'duration_seconds', 'actual_duration']:
            if cand in df.columns:
                dcol = cand
                break

        for _, row in df.iterrows():
            key = str(row.get(task_col, '')).strip()
            if not key:
                continue
            r_dict = row.to_dict()
            r_dict['task'] = key
            r_dict['business_duration'] = r_dict.get(bcol, '') if bcol else ''
            r_dict['duration'] = r_dict.get(dcol, '') if dcol else ''

            if key not in sla_dict:
                sla_dict[key] = r_dict
            else:
                existing = sla_dict[key]
                for k, v in r_dict.items():
                    if pd.notna(v) and str(v).strip() != '':
                        existing[k] = v
                sla_dict[key] = existing

    print(f"Total consolidated unique SLA records: {len(sla_dict)}")

    # 3. Join cases with SLA data
    merged_rows = []
    for _, r in cases_df.iterrows():
        key = str(r.get('number', '')).strip()
        s = sla_dict.get(key)
        new = r.copy()
        if s is not None:
            new['SLA_task'] = s.get('task', '')
            new['SLA_Business_Time_seconds'] = s.get('business_duration', '')
            new['SLA_Duration_seconds'] = s.get('duration', '')
        else:
            new['SLA_task'] = ''
            new['SLA_Business_Time_seconds'] = ''
            new['SLA_Duration_seconds'] = ''

        new['SLA_Business_Time'] = format_duration_from_seconds(new['SLA_Business_Time_seconds'])
        new['SLA_Duration'] = format_duration_from_seconds(new['SLA_Duration_seconds'])
        merged_rows.append(new)

    merged_df = pd.DataFrame(merged_rows)

    if os.path.exists(MERGED):
        ts = datetime.now().strftime('%Y%m%d%H%M%S')
        bak_name = f"Merged_Cases_With_SLA_Formatted_backup_{ts}.csv"
        bak = os.path.join(ARCHIVE_DIR, bak_name)
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
        'fill_tables_advanced.py',
        'fill_metrics_and_finalize_report.py'
    ]
    for s in sequence:
        ok = run_script(s)
        if not ok:
            print('Pipeline halted at', s)
            sys.exit(1)
    print('\nPipeline completed. Final report at:', os.path.join(OUT_REPORTS, 'Cases_Management_Report_Completed_tables_filled_final.docx'))

if __name__ == '__main__':
    main()
