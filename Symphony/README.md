# Symphony — Management Report Pipeline

## Purpose
Automated pipeline to generate executive DOCX management reports from Symphony ServiceNow case and SLA exports. The pipeline merges case and SLA exports, classifies ticket trends using keyword taxonomies, computes KPIs and SLAs, generates visual charts, and populates executive DOCX report templates.

## Directory Structure
- `data/raw/` — Input source CSVs (`Symphony_Casea_Last_12-Months.csv`, `Symphony_SLA_Last_12-Months.csv`)
- `data/processed/` — Merged and formatted dataset (`Merged_Cases_With_SLA_Formatted.csv`)
- `data/archive/` — Timestamped CSV backups
- `templates/` — `Cases_Management_Report_Template.docx` and `Trends.txt`
- `scripts/` — Active pipeline scripts
  - `scripts/archive/` — Deprecated single-file script iterations
- `outputs/` — Deliverables folder
  - `outputs/charts/` — Generated PNG charts
  - `outputs/tables/` — Metric CSVs and reclassification previews
  - `outputs/reports/` — Final management DOCX reports

## Prerequisites
- Python 3.8+
- Packages: `pandas`, `matplotlib`, `python-docx`, `Pillow`
  ```bash
  python3 -m pip install pandas matplotlib python-docx Pillow
  ```

## Execution
Run the full automated pipeline from the `Symphony/` root directory:
```bash
python3 scripts/run_full_report.py
```

The pipeline executes the following sequence:
1. Merges case and SLA CSV exports into `data/processed/Merged_Cases_With_SLA_Formatted.csv`.
2. Computes KPIs and generates chart PNGs in `outputs/charts/` and metric tables in `outputs/tables/`.
3. Inspects unclassified "Other" cases and applies approved trend expansions.
4. Populates charts, metric tables, executive summary, and appendices into the DOCX template.
5. Saves final completed management report to `outputs/reports/Cases_Management_Report_Completed_tables_filled_final.docx`.

## Governance & Guidance
- Refer to [`AGENTS.md`](file:///home/lee/Documents/1%20Projects/AcuteSupport/Symphony/AGENTS.md) for precise taxonomy rules, field mappings, and QA checks before making template changes.
- Merged data backups are automatically created under `data/archive/`.

**Contact**: Lee Booth (lee.booth@emishealth.com)
