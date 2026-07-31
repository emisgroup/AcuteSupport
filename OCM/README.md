# OCM — Management Report Pipeline

## Purpose
Pipeline and templates to produce executive DOCX management reports from OCM ServiceNow case and SLA exports.

## Directory Structure
- `data/raw/` — Source export CSVs (`OCM_Cases_Last_12-Months.csv`, `OCM_SLA_Last_12-Months.csv`)
- `data/processed/` — Merged and formatted dataset (`Merged_Cases_With_SLA_Formatted.csv`)
- `data/archive/` — Historical run backups
- `templates/` — `Cases_Management_Report_Template.docx` and `Trends.txt`
- `scripts/` — Trend classification and report generation scripts
- `outputs/` — Deliverables folder
  - `outputs/charts/` — Visualisation charts
  - `outputs/tables/` — Trend classification and SLA performance CSVs
  - `outputs/reports/` — Final DOCX management reports

## Quick Run
Run the full report build script from the `OCM/` directory:
```bash
python3 scripts/build_full_ocm_docx_report.py
```

## Guidance & Rules
- See [`AGENTS.md`](file:///home/lee/Documents/1%20Projects/AcuteSupport/OCM/AGENTS.md) for taxonomy specifications, placeholder mappings, and QA checklists.
- Source exports in `data/raw/` are preserved without manual edits.
