import csv
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
INPUT_CSV = os.path.join(BASE_DIR, 'data', 'raw', 'Symphony_Casea_Last_12-Months.csv')
TRENDS_TXT = os.path.join(BASE_DIR, 'templates', 'Trends.txt')
OUTPUT_DIR = os.path.join(BASE_DIR, 'data', 'raw', 'report_outputs')
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

def classify(row):
    number = row.get('number', '').strip()
    s_desc = row.get('short_description', '').strip()
    desc = row.get('description', '').strip()
    c_notes = row.get('close_notes', '') or row.get('Resolution notes', '') or row.get('work_notes', '') or ''
    
    text = f"{s_desc} {desc} {c_notes}".lower()

    # Specific Edge Case Handling
    if number == 'CS1647425':
        return "Access & Security", "User Access", "High", "Request to reinstate consultant user account.", "No"
    if number == 'CS1724856':
        return "Performance & Availability", "Availability", "High", "Application failing to load or launch.", "No"
    if number == 'CS1750314':
        return "Integration & Interfaces", "Third-Party Systems", "Medium", "Service restart request for EMIS/Optum external integration.", "No"
    if number == 'CS1798818':
        return "Configuration & Administration", "System Administration", "Medium", "Server status query regarding active infrastructure.", "No"
    if number == 'CS1802477':
        return "Reporting & Analytics", "Analytics", "Medium", "Practice utilization tracking and usage query.", "No"
    if number == 'CS1813664':
        return "Access & Security", "User Access", "High", "Departmental dropdown access request for Cromer and ED.", "No"
    if number == 'CS1821217':
        return "Integration & Interfaces", "Data Exchange", "Medium", "Date and time timestamp structure query for cloud integration.", "No"

    # 1. Access & Security
    # Audit & Compliance
    if any(k in text for k in ['audit', 'ig ', 'information governance', 'who accessed', 'who viewed', 'who edited', 'who deleted', 'view history', 'access history', 'deletion history', 'record change history', 'patient record view', 'who accessed record']):
        return "Access & Security", "Audit & Compliance", "High", "Case involves Information Governance, record access audit, or viewing history request.", "No"
    # Authentication
    if any(k in text for k in ['login', 'log in', 'logon', 'password', 'sso', 'mfa', 'locked out', 'lockout', 'sign in', 'signin', 'authentication', 'credential', 'can\'t log on', 'cannot log on', 'cant log on']):
        return "Access & Security", "Authentication", "High", "Case relates to user authentication, password reset, SSO, or account lockout.", "No"
    # Security Concern
    if any(k in text for k in ['unauthorised', 'security investigation', 'privilege escalation', 'data breach', 'security concern']):
        return "Access & Security", "Security Concern", "High", "Case involves suspected security vulnerability or unauthorised access investigation.", "No"
    # User Access
    if any(k in text for k in ['permission', 'access request', 'grant access', 'role assignment', 'group membership', 'user account', 'smartcard', 'smart card', 'user privilege', 'access missing', 'access removed', 'user list', 'active users', 'reinstate account']):
        return "Access & Security", "User Access", "High", "Case requests user access enablement, role assignment, active user list, or account reinstatement.", "No"

    # 8. Integration & Interfaces
    # Integration Failure
    if any(k in text for k in ['hl7', 'interface', 'dad', 'messaging', 'inbound', 'outbound', 'api failure', 'feed failure', 'sync failure', 'integration error', 'adt', 'orm', 'oru', 'msh', 'messages not passing', 'not going to maxims', 'messages failing', 'ecds failure', 'ecds submission', 'did not go to ipms', 'pas number']):
        return "Integration & Interfaces", "Integration Failure", "High", "Case relates to HL7 messaging, DAD interface, interop feeds, or message trigger failures.", "No"
    # Third-Party Systems
    if any(k in text for k in ['trud', 'ods', 'dmd', 'spine', 'scr', 'tie', 'pds', 'third party', 'external system', 'vendor dependency', 'gp import']):
        return "Integration & Interfaces", "Third-Party Systems", "High", "Case involves external NHS services (SCR/TIE/TRUD/ODS/GP Import) or vendor system dependencies.", "No"
    # Data Exchange
    if any(k in text for k in ['data exchange', 'mapping error', 'failed data load', 'import failure', 'export failure', 'batch import', 'data warehouse']):
        return "Integration & Interfaces", "Data Exchange", "High", "Case involves structured data exchange, data warehouse extraction, or import/export loading.", "No"

    # 2. Performance & Availability
    # Availability
    if any(k in text for k in ['outage', 'system down', 'service down', 'service degradation', 'offline', 'unavailable', 'trust wide failure', 'system failure', 'not loading']):
        return "Performance & Availability", "Availability", "High", "Case reports application outage, site-wide failure, or service unavailability.", "No"
    # Performance
    if any(k in text for k in ['slow', 'slowness', 'freezing', 'freeze', 'hanging', 'hang', 'timeout', 'time out', 'lag', 'unresponsive', 'performance issue', 'delay saving', 'delay loading', 'circling', 'spinning', 'not responding']):
        return "Performance & Availability", "Performance", "High", "Case reports application slowness, response lag, UI freezing, or spinning wheel.", "No"
    # Stability
    if any(k in text for k in ['crash', 'session drop', 'intermittent failure', 'instability', 'system crash']):
        return "Performance & Availability", "Stability", "High", "Case reports system instability, session drops, or intermittent crashes.", "No"

    # 7. Reporting & Analytics
    if any(k in text for k in ['report', 'ssrs', 'dashboard', 'extract', 'analytics', 'kpi', 'metric', 'stat ', 'statistics', 'shrewd']):
        if 'dashboard' in text:
            return "Reporting & Analytics", "Dashboard", "High", "Case involves dashboard configuration, metrics display, or dashboard access.", "No"
        elif any(k in text for k in ['kpi', 'metric', 'discrepancy', 'validation', 'shrewd']):
            return "Reporting & Analytics", "Analytics", "High", "Case involves data metrics, KPI validation, or analytics discrepancies.", "No"
        else:
            return "Reporting & Analytics", "Reporting", "High", "Case involves SSRS report generation, custom reports, or data extraction.", "No"

    # 9. Notifications & Communications
    if any(k in text for k in ['email', 'e-mail', 'mail not received', 'smtp', 'notification', 'alert', 'distribution list']):
        if 'alert' in text:
            return "Notifications & Communications", "Alerts", "High", "Case relates to system alert configuration or missing automated alerts.", "No"
        else:
            return "Notifications & Communications", "Email", "High", "Case involves email notification delivery, content, or recipient issues.", "No"

    # 5. Configuration & Administration
    # Master Data
    if any(k in text for k in ['location', 'department', 'ward', 'clinic', 'lookup', 'bedford', 'master file', 'masterfile', 'reference data', 'user setup', 'team setup', 'grey team', 'remove team']):
        return "Configuration & Administration", "Master Data", "High", "Case involves master reference data, department/ward lookups, team setup, or site configuration.", "No"
    # Configuration Change
    if any(k in text for k in ['printing', 'print', 'printer', 'label', 'batch print', 'document output', 'pdf', 'template', 'form config', 'field config', 'wristband', 'scanner', 'midas']):
        return "Configuration & Administration", "Configuration Change", "High", "Case involves document output, printer configuration, scanner hardware, forms, or templates.", "No"
    # System Administration
    if any(k in text for k in ['scheduled job', 'system setting', 'admin maintenance', 'environment', 'server config', 'low disk space', 'server in use', 'failover', 'db01', 'framework']):
        return "Configuration & Administration", "System Administration", "High", "Case involves server administration, disk space, failover configuration, or background environment setup.", "No"

    # 4. Data Management
    # Data Recovery
    if any(k in text for k in ['delete', 'deleted', 'soft delete', 'restore', 'recover', 'merge', 'duplicate record', 'e-docs missing', 'missing e-docs']):
        return "Data Management", "Data Recovery", "High", "Case involves record restoration, deleted data recovery, missing e-docs, or record merging.", "No"
    # Data Correction
    if any(k in text for k in ['sql', 'database', 'corrupt', 'data fix', 'script', 'amend record', 'data correction', 'clean-up', 'cleanup', 'incorrect value', 'incorrect date', 'duplicating comments']):
        return "Data Management", "Data Correction", "High", "Case involves database scripts, data corrections, record timestamp fixes, or duplicate text clean-up.", "No"
    # Data Quality
    if any(k in text for k in ['missing data', 'invalid data', 'inconsistent data', 'data mismatch', 'referential integrity']):
        return "Data Management", "Data Quality", "High", "Case relates to poor data quality, missing record fields, or data mismatches.", "No"

    # 6. Workflow & Process
    if any(k in text for k in ['workflow', 'stuck task', 'approval', 'routing', 'queue', 'assignment rule', 'process automation', 'checkout zone', 'brm']):
        if 'approval' in text:
            return "Workflow & Process", "Approval Management", "High", "Case involves approval tasks, approver routing, or approval delays.", "No"
        elif 'assignment' in text or 'queue' in text or 'checkout zone' in text:
            return "Workflow & Process", "Assignment", "High", "Case involves task queue routing, checkout zone assignments, or ownership rules.", "No"
        else:
            return "Workflow & Process", "Workflow Issue", "High", "Case involves automated workflow processing, stuck tasks, or clinical process routing.", "No"

    # 11. User Guidance & Training
    if any(k in text for k in ['how to', 'how do i', 'guidance', 'help with', 'training', 'knowledge article', 'user guide', 'meows', 'majax']):
        return "User Guidance & Training", "How-To Request", "High", "Case involves operational guidance, clinical scoring setup (MEOWS/MAJAX), or usage assistance.", "No"

    # 10. Service Requests
    if any(k in text for k in ['request', 'new ', 'create', 'setup', 'add ', 'enable', 'change', 'update', 'quote']):
        return "Service Requests", "New Request", "Medium", "Case represents a service request for creation, software quote, or configuration updates.", "No"

    # 3. Defects & Errors
    if any(k in text for k in ['error', 'exception', 'fault', 'failed', 'bug', 'defect', 'issue', 'not working', 'unable to', 'cannot', 'problem', 'blank pages']):
        return "Defects & Errors", "Application Defect", "Medium", "Case reports application defect, scanning blank pages, or functional error.", "No"

    # 12. Case Administration
    if any(k in text for k in ['duplicate', 'cancelled', 'misrouted', 'wrong team', 'raised in error', 'closed']):
        return "Case Administration", "Closure Management", "Medium", "Case relates to ticket administration, duplicate handling, or closure.", "No"

    return "Unclassified", "Needs Review", "Low", "Broad or ambiguous description requiring manual review.", "Yes"

def run_classification():
    with open(INPUT_CSV, mode='r', encoding='cp1252', errors='replace') as f:
        reader = csv.DictReader(f)
        cases = list(reader)

    classified_rows = []
    cat_counts = {}
    sub_counts = {}
    low_conf_cases = []

    for row in cases:
        c_num = row.get('number', '').strip()
        s_desc = row.get('short_description', '').strip()
        desc = row.get('description', '').strip()
        
        cat, sub, conf, reason, manual_rev = classify(row)
        
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

    output_csv = os.path.join(OUTPUT_DIR, 'Servicenow_Case_Trend_Classification.csv')
    with open(output_csv, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Case Number', 'Short Description Summary', 'Trend Category', 'Sub-Category', 'Confidence', 'Reasoning', 'Manual Review Required'])
        writer.writeheader()
        writer.writerows(classified_rows)

    # Recreate Trends.txt
    with open(TRENDS_TXT, mode='w', encoding='utf-8') as f:
        # Write unique category/subcategory taxonomy
        for cat, sub in TAXONOMY:
            if cat != "Unclassified":
                f.write(f"{cat} / {sub}\n")

    print(f"Classification completed for {len(cases)} cases.")
    print(f"Results saved to: {output_csv}")
    print(f"Trends.txt updated at: {TRENDS_TXT}")
    print(f"Low confidence cases count: {len(low_conf_cases)}")

if __name__ == '__main__':
    run_classification()
