Symphony — Management Report Pipeline

Purpose
Generate executive DOCX management reports from Symphony ServiceNow exports. The pipeline merges case and SLA exports, classifies trends using the taxonomy in AGENTS.md, computes KPIs, creates charts, and fills a DOCX template.

Key folders
- data/raw/                - input CSVs and generated outputs
- data/raw/report_outputs/ - final reports, KPIs, charts and CSVs
- templates/               - DOCX templates and Trends.txt
- scripts/                 - pipeline and helper scripts (run from repo root)
- docs/                    - archived reports and notes

Prerequisites
- Python 3.8+
- Packages: pandas, matplotlib, python-docx, Pillow
  python -m pip install pandas matplotlib python-docx Pillow

Quick run
1) Put Symphony CSVs into data\raw\
2) From repository root run:
   python scripts\run_full_report.py
3) Outputs -> data\raw\report_outputs\ (final DOCX, charts, CSVs)

Guidance
- Read AGENTS.md for taxonomy, placeholder mapping and QA checks before changing templates.
- Scripts back up merged CSVs before overwriting.

Contact: Lee Booth (lee.booth@emishealth.com)

