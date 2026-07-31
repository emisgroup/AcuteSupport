import csv
import os
import statistics

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MERGED_CSV = os.path.join(BASE_DIR, 'data', 'raw', 'Merged_Cases_With_SLA_Formatted.csv')
CLASS_CSV = os.path.join(BASE_DIR, 'data', 'raw', 'report_outputs', 'Servicenow_Case_Trend_Classification.csv')
OUTPUT_SLA_CSV = os.path.join(BASE_DIR, 'data', 'raw', 'report_outputs', 'Servicenow_Trend_SLA_Performance.csv')

def fmt_duration(seconds):
    if seconds is None or seconds < 0:
        return 'N/A'
    seconds = int(round(seconds))
    days = seconds // 86400
    remainder = seconds % 86400
    hours = remainder // 3600
    remainder %= 3600
    minutes = remainder // 60
    secs = remainder % 60
    
    parts = []
    if days > 0: parts.append(f'{days}d')
    if hours > 0: parts.append(f'{hours}h')
    if minutes > 0: parts.append(f'{minutes}m')
    if not parts: parts.append(f'{secs}s')
    return ' '.join(parts)

def update_sla_and_export():
    # Load classification mapping
    class_map = {}
    with open(CLASS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            class_map[r['Case Number']] = (r['Trend Category'], r['Sub-Category'])

    rows = []
    with open(MERGED_CSV, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for r in reader:
            c_num = r.get('number', '').strip()
            cat, sub = class_map.get(c_num, ('Unclassified', 'Needs Review'))
            r['trend_category'] = cat
            r['sub_category'] = sub
            r['trend'] = f"{cat} / {sub}"
            rows.append(r)

    # Write updated merged CSV
    if 'trend_category' not in fieldnames:
        fieldnames = fieldnames + ['trend_category', 'sub_category']
    
    with open(MERGED_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Calculate SLA stats by Category and Sub-Category
    cat_stats = {}
    sub_stats = {}

    for r in rows:
        cat = r['trend_category']
        sub = r['sub_category']
        bus_str = r.get('SLA_Business_Time_seconds', '').strip()
        dur_str = r.get('SLA_Duration_seconds', '').strip()
        
        b_val = float(bus_str) if bus_str and float(bus_str) >= 0 else None
        d_val = float(dur_str) if dur_str and float(dur_str) >= 0 else None
        
        # Category aggregation
        if cat not in cat_stats:
            cat_stats[cat] = {'count': 0, 'bus': [], 'dur': []}
        cat_stats[cat]['count'] += 1
        if b_val is not None: cat_stats[cat]['bus'].append(b_val)
        if d_val is not None: cat_stats[cat]['dur'].append(d_val)
        
        # Sub-category aggregation
        sub_key = (cat, sub)
        if sub_key not in sub_stats:
            sub_stats[sub_key] = {'count': 0, 'bus': [], 'dur': []}
        sub_stats[sub_key]['count'] += 1
        if b_val is not None: sub_stats[sub_key]['bus'].append(b_val)
        if d_val is not None: sub_stats[sub_key]['dur'].append(d_val)

    # Export SLA performance CSV
    sla_export_rows = []
    
    # Category summary rows
    for cat, d in sorted(cat_stats.items(), key=lambda x: x[1]['count'], reverse=True):
        bus = d['bus']
        dur = d['dur']
        n_sla = len(bus)
        if n_sla > 0:
            avg_b = statistics.mean(bus)
            med_b = statistics.median(bus)
            s_bus = sorted(bus)
            p90_b = s_bus[int(round(0.90 * (len(s_bus) - 1)))]
        else:
            avg_b = med_b = p90_b = None
        avg_d = statistics.mean(dur) if dur else None
        
        sla_export_rows.append({
            'Level': 'Category',
            'Trend Category': cat,
            'Sub-Category': 'ALL',
            'Total Cases': d['count'],
            'SLA Recorded Cases': n_sla,
            'Avg SLA Business Time': fmt_duration(avg_b),
            'Avg SLA Business Seconds': f"{avg_b:.0f}" if avg_b is not None else "",
            'Median SLA Business Time': fmt_duration(med_b),
            'P90 SLA Business Time': fmt_duration(p90_b),
            'Avg Elapsed Duration': fmt_duration(avg_d)
        })

    # Sub-category summary rows
    for (cat, sub), d in sorted(sub_stats.items(), key=lambda x: x[1]['count'], reverse=True):
        bus = d['bus']
        dur = d['dur']
        n_sla = len(bus)
        if n_sla > 0:
            avg_b = statistics.mean(bus)
            med_b = statistics.median(bus)
            s_bus = sorted(bus)
            p90_b = s_bus[int(round(0.90 * (len(s_bus) - 1)))]
        else:
            avg_b = med_b = p90_b = None
        avg_d = statistics.mean(dur) if dur else None
        
        sla_export_rows.append({
            'Level': 'Sub-Category',
            'Trend Category': cat,
            'Sub-Category': sub,
            'Total Cases': d['count'],
            'SLA Recorded Cases': n_sla,
            'Avg SLA Business Time': fmt_duration(avg_b),
            'Avg SLA Business Seconds': f"{avg_b:.0f}" if avg_b is not None else "",
            'Median SLA Business Time': fmt_duration(med_b),
            'P90 SLA Business Time': fmt_duration(p90_b),
            'Avg Elapsed Duration': fmt_duration(avg_d)
        })

    with open(OUTPUT_SLA_CSV, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['Level', 'Trend Category', 'Sub-Category', 'Total Cases', 'SLA Recorded Cases', 'Avg SLA Business Time', 'Avg SLA Business Seconds', 'Median SLA Business Time', 'P90 SLA Business Time', 'Avg Elapsed Duration']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sla_export_rows)

    print(f"Updated merged CSV with taxonomy: {MERGED_CSV}")
    print(f"Exported SLA taxonomy performance to: {OUTPUT_SLA_CSV}")

if __name__ == '__main__':
    update_sla_and_export()
