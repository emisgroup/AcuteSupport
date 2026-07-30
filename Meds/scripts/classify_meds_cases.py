import csv
import re
from collections import Counter, defaultdict

CSV_PATH = r"C:\Users\lee.booth\Documents\02_ServiceNow\Management_Reports\Meds\data\raw\Meds_Cases_Last_12-Months.csv"
OUT_MD = r"C:\Users\lee.booth\Documents\02_ServiceNow\Management_Reports\Meds\data\raw\report_outputs\trend_classification.md"
OUT_CSV = r"C:\Users\lee.booth\Documents\02_ServiceNow\Management_Reports\Meds\data\raw\report_outputs\trend_classification.csv"

# Lightweight keyword-to-(Category,Subcategory) mapping
MAPPING = [
    # Access & Security
    ("access", ("Access & Security","User Access")),
    ("permission", ("Access & Security","User Access")),
    ("login", ("Access & Security","Authentication")),
    ("mfa", ("Access & Security","Authentication")),
    ("password", ("Access & Security","Authentication")),
    ("audit", ("Access & Security","Audit & Compliance")),
    ("who deleted", ("Access & Security","Audit & Compliance")),
    ("unauthoris", ("Access & Security","Security Concern")),

    # Performance & Availability
    ("slow", ("Performance & Availability","Performance")),
    ("unrespons", ("Performance & Availability","Performance")),
    ("hang", ("Performance & Availability","Performance")),
    ("timeout", ("Performance & Availability","Performance")),
    ("outage", ("Performance & Availability","Availability")),
    ("down", ("Performance & Availability","Availability")),
    ("not available", ("Performance & Availability","Availability")),

    # Defects & Errors
    ("error", ("Defects & Errors","Error Messages")),
    ("exception", ("Defects & Errors","Error Messages")),
    ("bug", ("Defects & Errors","Application Defect")),
    ("doesn' t work", ("Defects & Errors","Application Defect")),
    ("server error", ("Defects & Errors","Error Messages")),

    # Data Management
    ("duplicate", ("Data Management","Data Correction")),
    ("incorrect data", ("Data Management","Data Correction")),
    ("missing data", ("Data Management","Data Quality")),
    ("restore", ("Data Management","Data Recovery")),
    ("deleted", ("Data Management","Data Recovery")),

    # Configuration & Administration
    ("config", ("Configuration & Administration","Configuration Change")),
    ("configure", ("Configuration & Administration","Configuration Change")),
    ("patch", ("Configuration & Administration","System Administration")),
    ("setting", ("Configuration & Administration","System Administration")),

    # Workflow & Process
    ("workflow", ("Workflow & Process","Workflow Issue")),
    ("stuck", ("Workflow & Process","Workflow Issue")),
    ("approval", ("Workflow & Process","Approval Management")),
    ("assignment", ("Workflow & Process","Assignment")),

    # Reporting & Analytics
    ("report", ("Reporting & Analytics","Reporting")),
    ("dashboard", ("Reporting & Analytics","Dashboard")),

    # Integration & Interfaces
    ("interface", ("Integration & Interfaces","Integration Failure")),
    ("hl7", ("Integration & Interfaces","Integration Failure")),
    ("integration", ("Integration & Interfaces","Integration Failure")),
    ("import", ("Integration & Interfaces","Data Exchange")),
    ("export", ("Integration & Interfaces","Data Exchange")),
    # Robot / Robotics / Third-party interfaces (Omnicell, BD, Rowa, PIC, Medicator)
    ("robot", ("Integration & Interfaces","Third-Party Systems")),
    ("robotic", ("Integration & Interfaces","Third-Party Systems")),
    ("robotics", ("Integration & Interfaces","Third-Party Systems")),
    ("omnicell", ("Integration & Interfaces","Third-Party Systems")),
    ("rowa", ("Integration & Interfaces","Third-Party Systems")),
    ("bd robot", ("Integration & Interfaces","Third-Party Systems")),
    ("bd arim", ("Integration & Interfaces","Third-Party Systems")),
    ("bd", ("Integration & Interfaces","Third-Party Systems")),
    ("pic-lite", ("Integration & Interfaces","Third-Party Systems")),
    ("pic lite", ("Integration & Interfaces","Third-Party Systems")),
    ("pic", ("Integration & Interfaces","Third-Party Systems")),
    ("medicator", ("Integration & Interfaces","Third-Party Systems")),
    ("medecator", ("Integration & Interfaces","Third-Party Systems")),
    ("medicator import", ("Integration & Interfaces","Third-Party Systems")),

    # Notifications & Communications
    ("email", ("Notifications & Communications","Email")),
    ("alert", ("Notifications & Communications","Alerts")),
    ("notification", ("Notifications & Communications","Alerts")),

    # Service Requests
    ("request", ("Service Requests","New Request")),
    ("change", ("Service Requests","Change Request")),
    ("information", ("Service Requests","Information Request")),

    # User Guidance & Training
    ("how to", ("User Guidance & Training","How-To Request")),
    ("training", ("User Guidance & Training","Training")),
    ("knowledge", ("User Guidance & Training","Knowledge Articles")),

    # Case Administration
    ("duplicate ticket", ("Case Administration","Duplicate Cases")),
    ("cancel", ("Case Administration","Closure Management")),
    ("raised in error", ("Case Administration","Closure Management")),
]

# Priority order of categories for tie-breaking
CATEGORY_ORDER = [
    "Access & Security","Performance & Availability","Defects & Errors","Data Management",
    "Configuration & Administration","Workflow & Process","Reporting & Analytics","Integration & Interfaces",
    "Notifications & Communications","Service Requests","User Guidance & Training","Case Administration"
]

# Helper normalise text

def norm_text(s):
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r"\s+", " ", s)
    return s

rows = []

with open(CSV_PATH, newline='', encoding='cp1252') as f:
    reader = csv.DictReader(f)
    for i, r in enumerate(reader, start=1):
        num = r.get('number') or r.get('Number') or f'Row {i}'
        sd = r.get('short_description') or r.get('Short description') or r.get('short_description'.title()) or r.get('short_description'.capitalize()) or r.get('short_description') or r.get('short_description')
        # fallback to header names present
        # build combined text
        desc = r.get('description') or r.get('Description') or ''
        close = r.get('close_notes') or r.get('Close notes') or r.get('close_notes') or r.get('close_notes'.title()) or r.get('close_notes'.capitalize()) or ''
        combined = ' '.join([sd or '', desc or '', close or ''])
        t = norm_text(combined)
        matches = []
        for token, (cat, sub) in MAPPING:
            if token in t:
                matches.append((cat, sub, token))
        # deduce classification
        if not matches:
            category = 'Unclassified'
            subcategory = 'Needs Review'
            confidence = 'Low'
            reasoning = 'No strong keyword match in short description/description/close notes.'
            manual = 'Yes'
        else:
            # choose highest-priority category among matches
            cats = [m[0] for m in matches]
            # if single unique category -> High
            uniq = list(dict.fromkeys(cats))
            if len(uniq) == 1 and len(matches) == 1:
                category = matches[0][0]
                subcategory = matches[0][1]
                confidence = 'High'
                reasoning = f"Matched token '{matches[0][2]}' in text."
                manual = 'No'
            else:
                # pick first by CATEGORY_ORDER
                chosen = None
                for c in CATEGORY_ORDER:
                    for m in matches:
                        if m[0] == c:
                            chosen = m
                            break
                    if chosen:
                        break
                if not chosen:
                    chosen = matches[0]
                category, subcategory, token = chosen
                # confidence medium if multiple matches but chosen has clear token
                confidence = 'Medium'
                reasoning = f"Matched token '{token}' among multiple possible matches."
                manual = 'No' if confidence == 'Medium' else 'Yes'
        rows.append({
            'Case Number': num,
            'Short Description Summary': (sd or '').replace('\n',' ').strip()[:200],
            'Trend Category': category,
            'Sub-Category': subcategory,
            'Confidence': confidence,
            'Reasoning': reasoning,
            'Manual Review Required': manual
        })

# write outputs

# ensure output dir exists
import os
os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)

with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

# Markdown table
with open(OUT_MD, 'w', encoding='utf-8') as f:
    f.write('| Case Number | Short Description Summary | Trend Category | Sub-Category | Confidence | Reasoning | Manual Review Required |\n')
    f.write('|---|---|---|---|---|---|---:|\n')
    for r in rows:
        f.write(f"| {r['Case Number']} | {r['Short Description Summary']} | {r['Trend Category']} | {r['Sub-Category']} | {r['Confidence']} | {r['Reasoning']} | {r['Manual Review Required']} |\n")

# summaries
cat_count = Counter(r['Trend Category'] for r in rows)
sub_count = Counter((r['Trend Category'], r['Sub-Category']) for r in rows)
low_conf = [r for r in rows if r['Confidence']=='Low' or r['Manual Review Required']=='Yes']

with open(OUT_MD, 'a', encoding='utf-8') as f:
    f.write('\n\n## Trend Summary\n\n')
    f.write('| Trend Category | Count |\n')
    f.write('|---|---:|\n')
    for k,v in cat_count.most_common():
        f.write(f'| {k} | {v} |\n')
    f.write('\n\n## Sub-Category Summary\n\n')
    f.write('| Trend Category | Sub-Category | Count |\n')
    f.write('|---|---|---:|\n')
    for (cat, sub), cnt in sub_count.most_common():
        f.write(f'| {cat} | {sub} | {cnt} |\n')
    f.write('\n\n## Low Confidence / Manual Review Cases\n\n')
    f.write('| Case Number | Issue | Reason Manual Review is Required |\n')
    f.write('|---|---|---|\n')
    for r in low_conf:
        f.write(f"| {r['Case Number']} | {r['Short Description Summary'][:80]} | {r['Reasoning']} |\n")

print('Classification complete')
print('Markdown output:', OUT_MD)
print('CSV output:', OUT_CSV)
