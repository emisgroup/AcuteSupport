Symphony Management Report Pipeline

Overview

This repo generates executive DOCX reports from Symphony (ServiceNow) case exports. The pipeline merges raw case and SLA exports, classifies trends, computes KPIs, produces charts/tables, and fills a DOCX template.

Repository layout (canonical)
- data/raw/                <- input CSVs and generated outputs (canonical)
  - Symphony_Casea_Last_12-Months.csv
  - Symphony_SLA_Last_12-Months.csv
  - Merged_Cases_With_SLA_Formatted.csv
  - report_outputs/        <- KPIs, charts, CSV tables, final DOCX
- templates/               <- DOCX template and Trends.txt
  - Cases_Management_Report_Template.docx
  - Trends.txt
- scripts/                 <- pipeline scripts (run from repo root)
  - run_full_report.py     <- orchestrates full pipeline
  - generate_report_charts.py
  - classify_other_trends.py
  - apply_new_trends_and_regenerate.py
  - export_charts_to_docx.py
  - fill_remaining_docx_placeholders.py
  - fill_tables_advanced.py
  - fill_metrics_and_finalize_report.py
- docs/                    <- archived reports and notes
- AGENTS.md                <- agent specification and run instructions

Prerequisites
- Python 3.8+
- Packages: pandas, matplotlib, python-docx, Pillow
  - Install: python -m pip install pandas matplotlib python-docx Pillow

Quick start
1. Place source CSVs into data\raw\ with exact filenames listed above.
2. From repository root run:
   python scripts\run_full_report.py
3. Outputs are written to data\raw\report_outputs\
   - Final report: Cases_Management_Report_Completed_tables_filled_final.docx
   - KPIs and supporting CSVs: *.csv
   - Charts: *.png

Notes
- AGENTS.md contains exact placeholder rules and QA checklist; read it before changing templates.
- Scripts create backups before overwriting merged CSVs or DOCX files.
- If a file appears missing, confirm you are running the scripts from the repository root.

Contact
- Project owner: Lee Booth
