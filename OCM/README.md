OCM — Management Report Pipeline

Purpose
Scripts and templates to generate management reports from OCM ServiceNow exports.

Layout
- data/raw/               - place source CSVs (OCM_Cases_Last_12-Months.csv, OCM_SLA_Last_12-Months.csv)
- data/raw/report_outputs - generated charts, CSVs and DOCX
- scripts/                - processing and reporting scripts
- templates/              - DOCX templates and Trends.txt

Quick start
1) Install Python 3.8+ and required packages
2) Put exports into data\raw\
3) Run scripts\run_full_report.py or product-specific scripts from repo root

See root README and AGENTS.md for detailed rules and QA checklist.
