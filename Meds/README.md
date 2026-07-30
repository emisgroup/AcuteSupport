Meds — Management Report Pipeline

Purpose
Tools and scripts to produce an executive DOCX management report from Meds ServiceNow exports.

Layout
- data/raw/               - place source CSVs here (Meds_Cases_Last_12-Months.csv, Meds_SLA_Last_12-Months.csv)
- data/raw/report_outputs - generated charts, tables, CSVs and final DOCX
- scripts/                - classification, merge and report generation scripts
- templates/              - DOCX template and Trends.txt

Typical workflow
1) Copy export CSVs to data/raw/
2) Run scripts\classify_meds_cases.py to produce trend classification CSV
3) Run scripts\generate_report_charts.py and other pipeline scripts to produce charts and final DOCX

Outputs
- data/raw/report_outputs/trend_classification.csv
- data/raw/report_outputs/*.png, *.csv, Cases_Management_Report_Completed_tables_filled_final.docx

See AGENTS.md for detailed rules, mappings and QA checklist.
