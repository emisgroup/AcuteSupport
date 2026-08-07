# Meds — Management Report Pipeline

## Purpose
Tools and scripts to produce executive DOCX management reports from Meds ServiceNow case and SLA exports.

## Directory Structure
- `data/raw/` — Source export CSVs (`Meds_Cases_Last_12-Months.csv`, `Meds_SLA_Last_12-Months.csv`, robot/lock/merge exports)
- `data/processed/` — Merged and formatted dataset (`Merged_Cases_With_SLA_Formatted.csv`)
- `data/archive/` — Historical run backups
- `templates/` — `Cases_Management_Report_Template.docx`, `Trends.txt`, `Trends_prelim.txt`
- `scripts/` — Analysis, trend classification, and DOCX generation scripts
- `outputs/` — Execution deliverables
  - `outputs/charts/` — Visualisation charts (`monthly_case_trend.png`, `priority_profile.png`, etc.)
  - `outputs/tables/` — Trend classification CSVs (`Servicenow_Case_Trend_Classification.csv`, etc.)
  - `outputs/reports/` — Final DOCX report deliverables

## Quick Run
Run the full report build script from the `Meds/` directory:
```bash
python3 scripts/build_full_meds_docx_report.py
```

## Guidance & Rules
- See [`AGENTS.md`](file:///home/lee/Documents/1%20Projects/AcuteSupport/Meds/AGENTS.md) for detailed classification taxonomy, field mapping, and QA rules.
- Original source exports remain untouched in `data/raw/` for audit purposes.
