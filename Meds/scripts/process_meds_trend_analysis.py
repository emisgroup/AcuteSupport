import csv
import os
import statistics

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CASES_CSV = os.path.join(BASE_DIR, 'data', 'raw', 'Meds_Cases_Last_12-Months.csv')
SLA_CSV = os.path.join(BASE_DIR, 'data', 'raw', 'Meds_SLA_Last_12-Months.csv')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
os.makedirs(PROCESSED_DIR, exist_ok=True)
MERGED_CSV = os.path.join(PROCESSED_DIR, 'Merged_Cases_With_SLA_Formatted.csv')
if not os.path.exists(MERGED_CSV):
    MERGED_CSV = os.path.join(BASE_DIR, 'data', 'raw', 'Merged_Cases_With_SLA_Formatted.csv')
TRENDS_TXT = os.path.join(BASE_DIR, 'templates', 'Trends.txt')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs', 'tables')
os.makedirs(OUTPUT_DIR, exist_ok=True)

TAXONOMY = [
    ("Access & Security", "User Access"),
    ("Access & Security", "Authentication"),
    ("Access & Security", "Audit & Compliance"),
    ("Access & Security", "Security Concern"),
    ("Performance & Availability", "Performance"),
    ("Performance & Availability", "Availability"),
    ("Performance & Availability", "Stability"),
    ("Defects & Errors", "Application Defect"),
    ("Defects & Errors", "Error Messages"),
    ("Defects & Errors", "Defect Fix Validation"),
    ("Data Management", "Data Correction"),
    ("Data Management", "Data Recovery"),
    ("Data Management", "Data Quality"),
    ("Configuration & Administration", "Configuration Change"),
    ("Configuration & Administration", "System Administration"),
    ("Configuration & Administration", "Master Data"),
    ("Workflow & Process", "Workflow Issue"),
    ("Workflow & Process", "Approval Management"),
    ("Workflow & Process", "Assignment"),
    ("Reporting & Analytics", "Reporting"),
    ("Reporting & Analytics", "Dashboard"),
    ("Reporting & Analytics", "Analytics"),
    ("Integration & Interfaces", "Integration Failure"),
    ("Integration & Interfaces", "Data Exchange"),
    ("Integration & Interfaces", "Third-Party Systems"),
    ("Notifications & Communications", "Email"),
    ("Notifications & Communications", "Alerts"),
    ("Notifications & Communications", "Subscription"),
    ("Service Requests", "New Request"),
    ("Service Requests", "Change Request"),
    ("Service Requests", "Information Request"),
    ("User Guidance & Training", "How-To Request"),
    ("User Guidance & Training", "Training"),
    ("User Guidance & Training", "Knowledge Articles"),
    ("Case Administration", "Duplicate Cases"),
    ("Case Administration", "Closure Management"),
    ("Case Administration", "Misrouted Cases"),
    ("Unclassified", "Needs Review")
]

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
    if days > 0: parts.append(f"{days}d")
    if hours > 0: parts.append(f"{hours}h")
    if minutes > 0: parts.append(f"{minutes}m")
    if not parts: parts.append(f"{secs}s")
    return ' '.join(parts)

def classify(row):
    number = row.get('number', '').strip()
    s_desc = row.get('short_description', '').strip()
    desc = row.get('description', '').strip()
    c_notes = row.get('close_notes', '') or row.get('Resolution notes', '') or row.get('work_notes', '') or ''
    
    text = f"{s_desc} {desc} {c_notes}".lower()

    # Meds Edge Cases
    if number in ['CS1630510', 'CS1633015']:
        return "Access & Security", "Authentication", "High", "Security word or authentication credential reset request.", "No"
    if number == 'CS1629997':
        return "User Guidance & Training", "Knowledge Articles", "High", "Release notes documentation request.", "No"
    if number == 'CS1649150':
        return "Configuration & Administration", "Master Data", "High", "Therapeutic drug codes master data enquiry.", "No"
    if number == 'CS1653325':
        return "Integration & Interfaces", "Integration Failure", "High", "PAS message queue stuck.", "No"
    if number == 'CS1672427':
        return "User Guidance & Training", "How-To Request", "High", "Operational guidance for copying medications list.", "No"
    if number == 'CS1674373':
        return "Access & Security", "User Access", "High", "Sharing agreement data access request.", "No"
    if number == 'CS1679300':
        return "Configuration & Administration", "Master Data", "High", "Genfin reference master data configuration.", "No"
    if number == 'CS1680283':
        return "Configuration & Administration", "Configuration Change", "High", "Desktop editor label configuration change.", "No"
    if number == 'CS1735054':
        return "Data Management", "Data Correction", "High", "Contract price drop-off database correction.", "No"
    if number == 'CS1737050':
        return "Configuration & Administration", "System Administration", "High", "Pharmacy background service administration.", "No"
    if number == 'CS1749142':
        return "Integration & Interfaces", "Integration Failure", "High", "eDischarge link interface down.", "No"
    if number == 'CS1772216':
        return "Case Administration", "Closure Management", "High", "Test ticket created in error, closed.", "No"
    if number == 'CS1780144':
        return "Data Management", "Data Quality", "High", "Unit value data discrepancy.", "No"
    if number in ['CS1786468', 'CS1795527']:
        return "Performance & Availability", "Availability", "High", "System down or module service outage.", "No"
    if number == 'CS1820759':
        return "Configuration & Administration", "Configuration Change", "High", "Batch and expiry configuration setup.", "No"
    if number == 'CS1820914':
        return "Case Administration", "Misrouted Cases", "High", "Ticket logged incorrectly, misrouted.", "No"
    if number == 'CS1821268':
        return "Data Management", "Data Quality", "High", "Missing NSVCode dictionary value.", "No"

    # 1. Access & Security
    # Audit & Compliance
    if any(k in text for k in ['audit', 'ig ', 'information governance', 'who accessed', 'who viewed', 'who edited', 'who deleted', 'view history', 'access history', 'deletion history', 'record change history', 'patient record view', 'who accessed record', 'controlled drug audit']):
        return "Access & Security", "Audit & Compliance", "High", "Case involves Information Governance, controlled drug audit, or record viewing history.", "No"
    # Authentication
    if any(k in text for k in ['login', 'log in', 'logon', 'password', 'sso', 'mfa', 'locked out', 'lockout', 'sign in', 'signin', 'authentication', 'credential', 'can\'t log on', 'cannot log on', 'cant log on', 'pin reset', 'security word']):
        return "Access & Security", "Authentication", "High", "Case relates to user authentication, password/PIN reset, SSO, or account lockout.", "No"
    # Security Concern
    if any(k in text for k in ['unauthorised', 'security investigation', 'privilege escalation', 'data breach', 'security concern']):
        return "Access & Security", "Security Concern", "High", "Case involves suspected security vulnerability or unauthorised access investigation.", "No"
    # User Access
    if any(k in text for k in ['permission', 'access request', 'grant access', 'role assignment', 'group membership', 'user account', 'smartcard', 'smart card', 'user privilege', 'access missing', 'access removed', 'user list', 'active users', 'pharmacist access']):
        return "Access & Security", "User Access", "High", "Case requests user access enablement, role assignment, pharmacist access, or permissions.", "No"

    # 8. Integration & Interfaces
    # Integration Failure
    if any(k in text for k in ['hl7', 'interface', 'dad', 'messaging', 'inbound', 'outbound', 'api failure', 'feed failure', 'sync failure', 'integration error', 'adt', 'orm', 'oru', 'msh', 'messages not passing', 'messages failing', 'robot interface', 'robot messaging', 'arx', 'rowa', 'mach4', 'dispensing robot', 'omnimed', 'pyxis', 'edischarge link']):
        return "Integration & Interfaces", "Integration Failure", "High", "Case relates to dispensing robot interface, HL7 messaging, or automated pharmacy feed failures.", "No"
    # Third-Party Systems
    if any(k in text for k in ['trud', 'ods', 'dmd', 'dm+d', 'spine', 'scr', 'tie', 'pds', 'third party', 'external system', 'vendor dependency', 'fmd', 'dictionary of medicines']):
        return "Integration & Interfaces", "Third-Party Systems", "High", "Case involves external NHS services (dm+d/TRUD/FMD) or third-party supplier systems.", "No"
    # Data Exchange
    if any(k in text for k in ['data exchange', 'mapping error', 'failed data load', 'import failure', 'export failure', 'batch import', 'data warehouse']):
        return "Integration & Interfaces", "Data Exchange", "High", "Case involves structured data exchange, data warehouse extraction, or import/export loading.", "No"

    # 2. Performance & Availability
    # Availability
    if any(k in text for k in ['outage', 'system down', 'service down', 'service degradation', 'offline', 'unavailable', 'trust wide failure', 'system failure', 'not loading', 'emis is down', 'supply down']):
        return "Performance & Availability", "Availability", "High", "Case reports application outage, pharmacy system down, or service unavailability.", "No"
    # Performance
    if any(k in text for k in ['slow', 'slowness', 'freezing', 'freeze', 'hanging', 'hang', 'timeout', 'time out', 'lag', 'unresponsive', 'performance issue', 'delay saving', 'delay loading', 'circling', 'spinning', 'not responding', 'lock', 'locked record']):
        return "Performance & Availability", "Performance", "High", "Case reports application slowness, response lag, UI freezing, or record lock issues.", "No"
    # Stability
    if any(k in text for k in ['crash', 'session drop', 'intermittent failure', 'instability', 'system crash']):
        return "Performance & Availability", "Stability", "High", "Case reports system instability, session drops, or intermittent crashes.", "No"

    # 7. Reporting & Analytics
    if any(k in text for k in ['report', 'ssrs', 'dashboard', 'extract', 'analytics', 'kpi', 'metric', 'stat ', 'statistics', 'controlled drug report', 'stock report']):
        if 'dashboard' in text:
            return "Reporting & Analytics", "Dashboard", "High", "Case involves dashboard configuration, metrics display, or dashboard access.", "No"
        elif any(k in text for k in ['kpi', 'metric', 'discrepancy', 'validation']):
            return "Reporting & Analytics", "Analytics", "High", "Case involves data metrics, KPI validation, or analytics discrepancies.", "No"
        else:
            return "Reporting & Analytics", "Reporting", "High", "Case involves pharmacy SSRS reports, stock reporting, or data extraction.", "No"

    # 9. Notifications & Communications
    if any(k in text for k in ['email', 'e-mail', 'mail not received', 'smtp', 'notification', 'alert', 'distribution list']):
        if 'alert' in text:
            return "Notifications & Communications", "Alerts", "High", "Case relates to system alert configuration or missing automated alerts.", "No"
        else:
            return "Notifications & Communications", "Email", "High", "Case involves email notification delivery, content, or recipient issues.", "No"

    # 5. Configuration & Administration
    # Master Data
    if any(k in text for k in ['location', 'department', 'ward', 'clinic', 'lookup', 'master file', 'masterfile', 'reference data', 'user setup', 'team setup', 'drug catalogue', 'formulary', 'drug file', 'medicine lookup', 'nsvcode']):
        return "Configuration & Administration", "Master Data", "High", "Case involves drug formulary master data, ward lookups, or drug catalogue setup.", "No"
    # Configuration Change
    if any(k in text for k in ['printing', 'print', 'printer', 'label', 'dispensing label', 'batch print', 'document output', 'pdf', 'template', 'form config', 'field config', 'wristband', 'scanner', 'desktop editor', 'batch and expiry']):
        return "Configuration & Administration", "Configuration Change", "High", "Case involves dispensing label printing, printer configuration, forms, or templates.", "No"
    # System Administration
    if any(k in text for k in ['scheduled job', 'system setting', 'admin maintenance', 'environment', 'server config', 'low disk space', 'server in use', 'failover', 'db01', 'framework', 'housekeeping', 'pharmacy background service']):
        return "Configuration & Administration", "System Administration", "High", "Case involves server administration, background services, disk space, or system properties.", "No"

    # 4. Data Management
    # Data Recovery
    if any(k in text for k in ['delete', 'deleted', 'soft delete', 'restore', 'recover', 'merge', 'duplicate record', 'patient merge']):
        return "Data Management", "Data Recovery", "High", "Case involves record restoration, patient record merging, or deleted data recovery.", "No"
    # Data Correction
    if any(k in text for k in ['sql', 'database', 'corrupt', 'data fix', 'script', 'amend record', 'data correction', 'clean-up', 'cleanup', 'incorrect value', 'incorrect date', 'stock correction', 'stock adjustment', 'contract price']):
        return "Data Management", "Data Correction", "High", "Case involves database scripts, stock level corrections, contract price fixes, or manual data fixes.", "No"
    # Data Quality
    if any(k in text for k in ['missing data', 'invalid data', 'inconsistent data', 'data mismatch', 'referential integrity', 'unit value difference']):
        return "Data Management", "Data Quality", "High", "Case relates to poor data quality, unit value differences, missing record fields, or data mismatches.", "No"

    # 6. Workflow & Process
    if any(k in text for k in ['workflow', 'stuck task', 'approval', 'routing', 'queue', 'assignment rule', 'process automation', 'dispensing workflow', 'eprescribing', 'discharge med']):
        if 'approval' in text:
            return "Workflow & Process", "Approval Management", "High", "Case involves approval tasks, approver routing, or approval delays.", "No"
        elif 'assignment' in text or 'queue' in text:
            return "Workflow & Process", "Assignment", "High", "Case involves task queue routing or assignment rules.", "No"
        else:
            return "Workflow & Process", "Workflow Issue", "High", "Case involves automated dispensing workflow processing or eprescribing routing.", "No"

    # 11. User Guidance & Training
    if any(k in text for k in ['how to', 'how do i', 'guidance', 'help with', 'training', 'knowledge article', 'user guide', 'release notes', 'copy and paste']):
        return "User Guidance & Training", "How-To Request", "High", "Case involves operational guidance, pharmacy usage assistance, or release notes documentation.", "No"

    # 10. Service Requests
    if any(k in text for k in ['request', 'new ', 'create', 'setup', 'add ', 'enable', 'change', 'update', 'quote']):
        return "Service Requests", "New Request", "Medium", "Case represents a service request for creation, drug setup, or system updates.", "No"

    # 3. Defects & Errors
    if any(k in text for k in ['error', 'exception', 'fault', 'failed', 'bug', 'defect', 'issue', 'not working', 'unable to', 'cannot', 'problem']):
        return "Defects & Errors", "Application Defect", "Medium", "Case reports application defect, unexpected behaviour, or functional error.", "No"

    # 12. Case Administration
    if any(k in text for k in ['duplicate', 'cancelled', 'misrouted', 'wrong team', 'raised in error', 'closed', 'ignore']):
        return "Case Administration", "Closure Management", "Medium", "Case relates to ticket administration, duplicate handling, test cases, or closure.", "No"

    return "Unclassified", "Needs Review", "Low", "Broad or ambiguous description requiring manual review.", "Yes"

def run_all():
    with open(CASES_CSV, mode='r', encoding='cp1252', errors='replace') as f:
        cases = list(csv.DictReader(f))

    sla_map = {}
    with open(SLA_CSV, mode='r', encoding='cp1252', errors='replace') as f:
        for r in csv.DictReader(f):
            if r['task'] not in sla_map:
                sla_map[r['task']] = r

    merged_rows = []
    classified_rows = []
    cat_counts = {}
    sub_counts = {}
    low_conf_cases = []

    for r in cases:
        c_num = r.get('number', '').strip()
        s_desc = r.get('short_description', '').strip()
        
        cat, sub, conf, reason, manual_rev = classify(r)
        
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        sub_key = (cat, sub)
        sub_counts[sub_key] = sub_counts.get(sub_key, 0) + 1
        
        s_summary = s_desc if len(s_desc) <= 80 else s_desc[:77] + '...'
        
        classified_rows.append({
            'Case Number': c_num,
            'Short Description Summary': s_summary,
            'Trend Category': cat,
            'Sub-Category': sub,
            'Confidence': conf,
            'Reasoning': reason,
            'Manual Review Required': manual_rev
        })
        
        if conf == 'Low' or manual_rev == 'Yes' or cat == 'Unclassified':
            low_conf_cases.append({
                'Case Number': c_num,
                'Issue': s_summary,
                'Reason Manual Review is Required': reason
            })

        sla_data = sla_map.get(c_num, {})
        bus_sec = sla_data.get('business_duration', '').strip()
        dur_sec = sla_data.get('duration', '').strip()
        
        r_merged = dict(r)
        r_merged['SLA_task'] = c_num if c_num in sla_map else ''
        r_merged['SLA_Business_Time_seconds'] = bus_sec
        r_merged['SLA_Duration_seconds'] = dur_sec
        r_merged['SLA_Business_Time'] = fmt_duration(float(bus_sec)) if bus_sec and bus_sec.isdigit() else ''
        r_merged['SLA_Duration'] = fmt_duration(float(dur_sec)) if dur_sec and dur_sec.isdigit() else ''
        r_merged['trend_category'] = cat
        r_merged['sub_category'] = sub
        r_merged['trend'] = f"{cat} / {sub}"
        merged_rows.append(r_merged)

    fieldnames = list(cases[0].keys()) + ['SLA_task', 'SLA_Business_Time_seconds', 'SLA_Duration_seconds', 'SLA_Business_Time', 'SLA_Duration', 'trend_category', 'sub_category', 'trend']
    with open(MERGED_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(merged_rows)

    class_output_csv = os.path.join(OUTPUT_DIR, 'Servicenow_Case_Trend_Classification.csv')
    with open(class_output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Case Number', 'Short Description Summary', 'Trend Category', 'Sub-Category', 'Confidence', 'Reasoning', 'Manual Review Required'])
        writer.writeheader()
        writer.writerows(classified_rows)

    with open(TRENDS_TXT, 'w', encoding='utf-8') as f:
        for cat, sub in TAXONOMY:
            if cat != "Unclassified":
                f.write(f"{cat} / {sub}\n")

    cat_stats = {}
    sub_stats = {}

    for r in merged_rows:
        cat = r['trend_category']
        sub = r['sub_category']
        bus_str = r.get('SLA_Business_Time_seconds', '').strip()
        dur_str = r.get('SLA_Duration_seconds', '').strip()
        
        b_val = float(bus_str) if bus_str and bus_str.replace('.','',1).isdigit() else None
        d_val = float(dur_str) if dur_str and dur_str.replace('.','',1).isdigit() else None
        
        if cat not in cat_stats:
            cat_stats[cat] = {'count': 0, 'bus': [], 'dur': []}
        cat_stats[cat]['count'] += 1
        if b_val is not None: cat_stats[cat]['bus'].append(b_val)
        if d_val is not None: cat_stats[cat]['dur'].append(d_val)
        
        sub_key = (cat, sub)
        if sub_key not in sub_stats:
            sub_stats[sub_key] = {'count': 0, 'bus': [], 'dur': []}
        sub_stats[sub_key]['count'] += 1
        if b_val is not None: sub_stats[sub_key]['bus'].append(b_val)
        if d_val is not None: sub_stats[sub_key]['dur'].append(d_val)

    sla_export_rows = []
    
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

    sla_output_csv = os.path.join(OUTPUT_DIR, 'Servicenow_Trend_SLA_Performance.csv')
    with open(sla_output_csv, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['Level', 'Trend Category', 'Sub-Category', 'Total Cases', 'SLA Recorded Cases', 'Avg SLA Business Time', 'Avg SLA Business Seconds', 'Median SLA Business Time', 'P90 SLA Business Time', 'Avg Elapsed Duration']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sla_export_rows)

    print(f"Processed {len(cases)} Meds cases.")
    print(f"Low confidence count: {len(low_conf_cases)}")
    print(f"Classification saved to: {class_output_csv}")
    print(f"SLA Performance saved to: {sla_output_csv}")
    print(f"Merged CSV saved to: {MERGED_CSV}")

if __name__ == '__main__':
    run_all()
